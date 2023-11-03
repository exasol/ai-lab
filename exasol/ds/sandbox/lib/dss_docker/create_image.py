import docker
import logging
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
CONTAINER_IMAGE_TAG = f"ds-sandbox:{DSS_VERSION}"


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")


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
        docker_env = docker.from_env()
        path = Path(__file__).parent
        _logger.info(
            f"Creating docker image {CONTAINER_IMAGE_TAG}"
            f" from {path / 'Dockerfile'}"
        )
        docker_env.images.build(path=str(path), tag=CONTAINER_IMAGE_TAG)
        container = docker_env.containers.create(
            image=CONTAINER_IMAGE_TAG,
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
        container.commit(
            repository=f"exasol/{CONTAINER_IMAGE_TAG}",
            tag="latest",
        )
    except Exception as ex:
        raise ex
    finally:
        _logger.info("Stopping container")
        container.stop()
        _logger.info("Removing container")
        container.remove()


if __name__ == "__main__":
    create_image()
