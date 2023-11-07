import docker
import logging
from datetime import datetime
from docker.types import Mount
from exasol.ds.sandbox.lib import pretty_print
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


DSS_VERSION = version("exasol-data-science-sandbox")


class DssDockerImage:
    DEFAULT_CONTAINER_NAME = "ds-sandbox-docker"
    DEFAULT_IMAGE_NAME = f"exasol/data-science-sandbox:{DSS_VERSION}"

    @classmethod
    def for_production(cls) -> "DssDockerImage":
        return DssDockerImage(
            container_name=DssDockerImage.DEFAULT_CONTAINER_NAME,
            image_name=DssDockerImage.DEFAULT_IMAGE_NAME,
            log_level=logging.INFO,
        )

    def __init__(self, container_name: str, image_name: str, log_level: str):
        self.container_name = container_name
        self.image_name = image_name
        self.log_level = log_level

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

    def create(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(self.log_level)
        logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")
        try:
            start = datetime.now()
            docker_client = docker.from_env()
            path = Path(__file__).parent
            logger.info(
                f"Creating docker image {self.image_name}"
                f" from {path / 'Dockerfile'}"
            )
            docker_client.images.build(path=str(path), tag=self.image_name)
            socket_mount = Mount("/var/run/docker.sock", "/var/run/docker.sock", type="bind")
            mapped_ports = {'8888/tcp': 8888}
            container = docker_client.containers.create(
                image=self.image_name,
                name=self.container_name,
                mounts=[socket_mount],
                command="sleep infinity",
                detach=True,
                ports=mapped_ports,
            )
            logger.info("Starting container")
            container.start()
            logger.info("Installing dependencies")
            run_install_dependencies(
                AnsibleAccess(),
                configuration=self._ansible_config(),
                host_infos=tuple(),
                ansible_run_context=self._ansible_run_context(),
                ansible_repositories=ansible_repository.default_repositories,
            )
            logger.info("Committing changes to docker container")
            image = container.commit(
                repository=self.image_name,
            )
        except Exception as ex:
            raise ex
        finally:
            logger.info("Stopping container")
            container.stop()
            logger.info("Removing container")
            container.remove()
        size = pretty_print.size(image.attrs["Size"])
        elapsed = pretty_print.elapsed(start)
        logger.info(f"Built Docker image {self.image_name} size {size} in {elapsed}.")


if __name__ == "__main__":
    DssDockerImage.for_production().create()
