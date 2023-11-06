import docker
import logging
from datetime import datetime, timedelta
from importlib_metadata import version
from pathlib import Path

from exasol.ds.sandbox.lib.config import ConfigObject, SLC_VERSION
# renaming proposal:
# import exasol.ds.sandbox.lib.ansible
# file ansible.__init__.py with content "import ...ansible.repository"
# enables usage: ansible.repository.default
from exasol.ds.sandbox.lib.ansible import ansible_repository
from exasol.ds.sandbox.lib.ansible.ansible_run_context import AnsibleRunContext
from exasol.ds.sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol.ds.sandbox.lib.setup_ec2.run_install_dependencies import run_install_dependencies

CONTAINER_NAME = "ds-sandbox-docker"
DSS_VERSION = version("exasol-data-science-sandbox")
DOCKER_IMAGE = f"exasol/ds-sandbox:{DSS_VERSION}"


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")


def duration(start: datetime) -> str:
    d = datetime.now() - start
    d = d - timedelta(microseconds=d.microseconds)
    return str(d)


def pretty_size(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"


def create_image():
    def _ansible_run_context() -> AnsibleRunContext:
        extra_vars = {
            "docker_container": CONTAINER_NAME,
        }
        return AnsibleRunContext(
            playbook="dss_docker_playbook.yml",
            extra_vars=extra_vars,
        )

    def _ansible_config() -> ConfigObject:
        return ConfigObject(
            time_to_wait_for_polling=0.1,
            slc_version=SLC_VERSION,
        )

    try:
        start = datetime.now()
        docker_env = docker.from_env()
        path = Path(__file__).parent
        _logger.info(
            f"Creating docker image {DOCKER_IMAGE}"
            f" from {path / 'Dockerfile'}"
        )
        docker_env.images.build(path=str(path), tag=DOCKER_IMAGE)
        container = docker_env.containers.create(
            image=DOCKER_IMAGE,
            name=CONTAINER_NAME,
            command="sleep infinity",
            detach=True,
        )
        _logger.info("Starting container")
        container.start()
        _logger.info("Installing dependencies")
        run_install_dependencies(
            AnsibleAccess(),
            configuration=_ansible_config(),
            host_infos=tuple(),
            ansible_run_context=_ansible_run_context(),
            ansible_repositories=ansible_repository.default_repositories,
        )
        _logger.info("Committing changes to docker container")
        image = container.commit(
            repository=DOCKER_IMAGE,
        )
    except Exception as ex:
        raise ex
    finally:
        _logger.info("Stopping container")
        container.stop()
        _logger.info("Removing container")
        container.remove()
    size = pretty_size(image.attrs["Size"])
    _logger.info(f"Built Docker image {DOCKER_IMAGE} size {size} in {duration(start)}.")
    # TODO: Publish image to hub.docker.com


if __name__ == "__main__":
    create_image()
