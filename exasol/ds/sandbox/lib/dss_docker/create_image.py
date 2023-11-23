import docker
import humanfriendly
import importlib_resources

from datetime import datetime
from docker.types import Mount
from exasol.ds.sandbox.lib import pretty_print
from importlib_metadata import version
from pathlib import Path
from typing import List

from exasol.ds.sandbox.lib.config import ConfigObject, SLC_VERSION
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.ansible import ansible_repository
from exasol.ds.sandbox.lib.ansible.ansible_run_context import AnsibleRunContext
from exasol.ds.sandbox.lib.ansible.ansible_access import AnsibleAccess, AnsibleFacts
from exasol.ds.sandbox.lib.setup_ec2.run_install_dependencies import run_install_dependencies


DSS_VERSION = version("exasol-data-science-sandbox")
_logger = get_status_logger(LogType.DOCKER_IMAGE)


class DssDockerImage:
    @classmethod
    def timestamp(cls) -> str:
        return f'{datetime.now().timestamp():.0f}'

    def __init__(
            self,
            repository: str,
            version: str = None,
            publish: bool = False,
            keep_container: bool = False,
    ):
        version = version if version else DSS_VERSION
        self.container_name = f"ds-sandbox-{DssDockerImage.timestamp()}"
        self.image_name = f"{repository}:{version}"
        self.publish = publish
        self.keep_container = keep_container

    def _ansible_run_context(self) -> AnsibleRunContext:
        extra_vars = {
            "docker_container": self.container_name,
        }
        return AnsibleRunContext(
            playbook="dss_docker_playbook.yml",
            extra_vars=extra_vars,
        )

    def _ansible_config(self) -> ConfigObject:
        return ConfigObject(
            time_to_wait_for_polling=0.1,
            slc_version=SLC_VERSION,
        )

    def _docker_file(self) -> importlib_resources.abc.Traversable:
        return (
            importlib_resources
            .files("exasol.ds.sandbox.lib.dss_docker")
            .joinpath("Dockerfile")
        )

    def _copy_args(self, facts: AnsibleFacts) -> List[str]:
        if not "dss_ansible_facts" in facts:
            return []
        folder = facts["dss_ansible_facts"].get("notebook_folder", None)
        if not folder:
            return []
        return [ "--copy-from", "/root/notebooks",
                 "--copy-to", "/root/new" ]

    def create(self):
        docker_file = self._docker_file()
        try:
            start = datetime.now()
            docker_client = docker.from_env()
            _logger.info(f"Creating docker image {self.image_name} from {docker_file}")
            with docker_file.open("rb") as fileobj:
                docker_client.images.build(fileobj=fileobj, tag=self.image_name)
            container = docker_client.containers.create(
                image=self.image_name,
                name=self.container_name,
                command="sleep infinity",
                detach=True,
            )
            _logger.info("Starting container")
            container.start()
            _logger.info("Installing dependencies")
            facts = run_install_dependencies(
                AnsibleAccess(),
                configuration=self._ansible_config(),
                host_infos=tuple(),
                ansible_run_context=self._ansible_run_context(),
                ansible_repositories=ansible_repository.default_repositories,
            )

            _logger.info(f"Ansible facts: {facts}")
            _logger.info("Committing changes to docker container")
            entrypoint = [
                # "sleep",
                # "infinity",
                "python3",
                "/root/entrypoint.py",
                "--jupyter-server",
                # "--sleep",
            ] + self._copy_args(facts)
            conf = {
                "Entrypoint": entrypoint,
                "Cmd": [],
            }
            image = container.commit(
                repository=self.image_name,
                conf=conf,
            )
        except Exception as ex:
            raise ex
        finally:
            if self.keep_container:
                _logger.info("Keeping container running")
            else:
                _logger.info("Stopping container")
                container.stop()
                _logger.info("Removing container")
                container.remove()
        size = humanfriendly.format_size(image.attrs["Size"])
        elapsed = pretty_print.elapsed(start)
        _logger.info(f"Built Docker image {self.image_name} size {size} in {elapsed}.")
