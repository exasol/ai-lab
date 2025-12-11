from datetime import datetime
from functools import reduce
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

import docker
import humanfriendly
import importlib_resources
from docker.models.containers import Container as DockerContainer
from docker.models.images import Image as DockerImage
from importlib_metadata import version

from exasol.ds.sandbox.lib import pretty_print
from exasol.ds.sandbox.lib.ansible import ansible_repository
from exasol.ds.sandbox.lib.ansible.ansible_access import (
    AnsibleAccess,
    AnsibleFacts as OldAnsibleFacts,
)
from exasol.ds.sandbox.lib.ansible.ansible_run_context import AnsibleRunContext
from exasol.ds.sandbox.lib.ansible.facts import AnsibleFacts
from exasol.ds.sandbox.lib.config import (
    AI_LAB_VERSION,
    ConfigObject,
)
from exasol.ds.sandbox.lib.logging import (
    LogType,
    get_status_logger,
)
from exasol.ds.sandbox.lib.setup_ec2.host_info import HostInfo
from exasol.ds.sandbox.lib.setup_ec2.run_install_dependencies import (
    run_install_dependencies,
)

DEFAULT_ORG_AND_REPOSITORY = "exasol/ai-lab"
_logger = get_status_logger(LogType.DOCKER_IMAGE)


def to_docker_env(env: dict[str, Any]) -> list[str]:
    return [f'{var}={val}' for var, val in env.items()]


# def get_fact(facts: OldAnsibleFacts, *keys: str) -> Optional[str]:
#     return get_nested_value(facts, "dss_facts", *keys)


# def get_nested_value(mapping: Dict[str, any], *keys: str) -> Optional[str]:
#     def nested_item(current, key):
#         valid = current is not None and key in current
#         return current[key] if valid else None
#
#     return reduce(nested_item, keys, mapping)


def jupyter_env_vars(facts: AnsibleFacts) -> dict[str, Any]:
    if facts.get("jupyter", "server") is None:
        return {}

    env_spec = {
        "JUPYTER_VENV": ("jupyter", "virtualenv"),
        "NOTEBOOK_DEFAULTS": ("notebook_folder", "initial"),
        "NOTEBOOKS": ("notebook_folder", "final"),
    }
    return facts.as_dict(env_spec)


# obsolete
def old_entrypoint(facts: OldAnsibleFacts) -> List[str]:
    def jupyter():
        command = get_fact(facts, "jupyter", "command")
        if command is None:
            return []
        docker_group = get_fact(facts, "docker_group")
        port = get_fact(facts, "jupyter", "port")
        user_name = get_fact(facts, "jupyter", "user")
        group = get_fact(facts, "jupyter", "group")
        user_home = get_fact(facts, "jupyter", "home")
        password = get_fact(facts, "jupyter", "password")
        logfile = get_fact(facts, "jupyter", "logfile")
        virtualenv = get_fact(facts, "jupyter", "virtualenv")
        return [
            "--home", user_home,
            "--jupyter-server", command,
            "--port", port,
            "--user", user_name,
            "--group", group,
            "--docker-group", docker_group,
            "--password", password,
            "--jupyter-logfile", logfile,
            "--venv", virtualenv,
        ]

    entrypoint = get_fact(facts, "entrypoint")
    if entrypoint is None:
        return ["sleep", "infinity"]
    entry_cmd = ["sudo", "python3", entrypoint]
    folder = get_fact(facts, "notebook_folder")
    if not folder:
        return entry_cmd + jupyter()
    return entry_cmd + [
        "--notebook-defaults", folder["initial"],
        "--notebooks", folder["final"]
    ] + jupyter()


# obsolete
def old_entrypoint_2(facts: OldAnsibleFacts, env: dict[str, Any]) -> List[str]:
    entrypoint = facts.get("entrypoint")
    if not entrypoint:
        return ["sleep", "infinity"]

    env_vars = ",".join(env)
    return ["sudo", f"--preserve-env={env_vars}", "python3", entrypoint]


def build_entrypoint(facts: AnsibleFacts) -> List[str]:
    def jupyter():
        command = facts.get("jupyter", "server")
        if command is None:
            return []
        return [
            "--jupyter-server", command,
            "--jupyter-core", facts.get("jupyter", "core"),
            "--home", facts.get("jupyter", "home"),
            "--port", facts.get("jupyter", "port"),
            "--user", facts.get("jupyter", "user"),
            "--group", facts.get("jupyter", "group"),
            "--docker-group", facts.get("docker_group"),
            "--password", facts.get("jupyter", "password"),
            "--jupyter-logfile", facts.get("jupyter", "logfile"),
            "--venv", facts.get("jupyter", "virtualenv"),
        ]

    entrypoint = facts.get("entrypoint")
    if entrypoint is None:
        return ["sleep", "infinity"]
    entry_cmd = [
        "sudo",
        "--preserve-env=JUPYTER_PASSWORD",
        "python3",
        entrypoint,
    ]
    folder = facts.get("notebook_folder")
    if not folder:
        return entry_cmd + jupyter()
    return entry_cmd + [
        "--notebook-defaults", folder["initial"],
        "--notebooks", folder["final"]
    ] + jupyter()


class DssDockerImage:
    @classmethod
    def timestamp(cls) -> str:
        return f'{datetime.now().timestamp():.0f}'

    def __init__(
            self,
            repository: str,
            version: str = None,
            keep_container: bool = False,
            work_in_progress_notebooks: bool = False
    ):
        self.work_in_progress_notebooks = work_in_progress_notebooks
        version = version if version else AI_LAB_VERSION
        self.container_name = f"ds-sandbox-{DssDockerImage.timestamp()}"
        self.repository = repository
        self.version = version
        self.keep_container = keep_container
        self._start = None
        self.registry = None

    @property
    def image_name(self):
        return f"{self.repository}:{self.version}"

    def _ansible_run_context(self) -> AnsibleRunContext:
        extra_vars = {
            "docker_container": self.container_name,
            "work_in_progress_notebooks": self.work_in_progress_notebooks
        }
        return AnsibleRunContext(
            playbook="ai_lab_docker_playbook.yml",
            extra_vars=extra_vars,
        )

    def _ansible_config(self) -> ConfigObject:
        return ConfigObject(
            time_to_wait_for_polling=0.1,
            ai_lab_version=AI_LAB_VERSION,
        )

    def _docker_file(self) -> importlib_resources.abc.Traversable:
        return (
            importlib_resources
            .files("exasol.ds.sandbox.lib.dss_docker")
            .joinpath("Dockerfile")
        )

    def _start_container(self) -> DockerContainer:
        self._start = datetime.now()
        # default timeout is 60 seconds.
        docker_client = docker.from_env(timeout=600)
        try:
            return docker_client.containers.get(self.container_name)
        except:
            pass
        docker_file = self._docker_file()
        _logger.info(f"Creating docker image {self.image_name} from {docker_file}")
        if self.registry is not None:
            docker_client.login(self.registry.username, self.registry.password)
        with docker_file.open("rb") as fileobj:
            docker_client.images.build(
                fileobj=fileobj,
                tag=self.image_name,
                rm=True,
            )
        container = docker_client.containers.create(
            image=self.image_name,
            name=self.container_name,
            command="sleep infinity",
            detach=True,
        )
        _logger.info("Starting container")
        container.start()
        return container

    def _install_dependencies(self) -> AnsibleFacts:
        _logger.info("Installing dependencies")
        host_infos = (HostInfo(self.container_name, None),)
        return run_install_dependencies(
            AnsibleAccess(),
            configuration=self._ansible_config(),
            host_infos=host_infos,
            ansible_run_context=self._ansible_run_context(),
            ansible_repositories=ansible_repository.default_repositories,
        )

    def _commit_container(
            self,
            container: DockerContainer,
            facts: AnsibleFacts,
    ) -> DockerImage:
        _logger.debug(f'AI Lab facts: {facts.get()}')
        _logger.info("Committing changes to docker container")
        # virtualenv = get_fact(facts, "jupyter", "virtualenv")
        port = facts.get("jupyter", "port")
        notebook_folder_final = facts.get("notebook_folder", "final")
        # notebook_folder_initial = get_fact(facts, "notebook_folder", "initial")

        env = jupyter_env_vars(facts)
        # entrypoint = old_entrypoint_2(facts, env)
        entrypoint = build_entrypoint(facts)
        conf = {
            "Entrypoint": entrypoint,
            "Cmd": [],
            "Volumes": {notebook_folder_final: {}, },
            "ExposedPorts": {f"{port}/tcp": {}},
            "User": facts.get("docker_user"),
            # "Env": [
            #     f"VIRTUAL_ENV={virtualenv}",
            #     f"NOTEBOOK_FOLDER_FINAL={notebook_folder_final}",
            #     f"NOTEBOOK_FOLDER_INITIAL={notebook_folder_initial}",
            # ],
            "Env": to_docker_env(env),
        }
        img = container.commit(repository=self.image_name, conf=conf)
        img.tag(self.repository, "latest")
        return img

    def _cleanup(self, container: DockerContainer):
        if container is None:
            return
        if self.keep_container:
            _logger.info(f"Keeping container {self.container_name} running")
            return
        _logger.info("Stopping container")
        container.stop()
        _logger.info("Removing container")
        container.remove()

    def _push(self):
        if self.registry is not None:
            self.registry.push(self.repository, self.version)
            self.registry.push(self.repository, "latest")

    def create(self):
        container = None
        try:
            container = self._start_container()
            facts = self._install_dependencies()
            image = self._commit_container(container, facts)
            self._push()
        except Exception as ex:
            raise ex
        finally:
            self._cleanup(container)
        size = humanfriendly.format_size(image.attrs["Size"])
        elapsed = pretty_print.elapsed(self._start)
        _logger.info(f"Built Docker image {self.image_name} size {size} in {elapsed}.")
