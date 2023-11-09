import docker
import humanfriendly
import importlib_resources

from datetime import datetime
from docker.types import Mount
from exasol.ds.sandbox.lib import pretty_print
from importlib_metadata import version
from pathlib import Path

from exasol.ds.sandbox.lib.config import ConfigObject, SLC_VERSION
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.ansible import ansible_repository
from exasol.ds.sandbox.lib.ansible.ansible_run_context import AnsibleRunContext
from exasol.ds.sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol.ds.sandbox.lib.setup_ec2.run_install_dependencies import run_install_dependencies

DSS_VERSION = version("exasol-data-science-sandbox")


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

    def _docker_file(self) -> Path:
        return (
            importlib_resources
            .files("exasol.ds.sandbox.lib.dss_docker")
            .joinpath("Dockerfile")
        )

    def create(self):
        logger = get_status_logger(LogType.DOCKER_IMAGE)
        docker_file = self._docker_file()
        try:
            start = datetime.now()
            docker_client = docker.from_env()
            logger.info(f"Creating docker image {self.image_name} from {docker_file}")
            docker_client.images.build(path=str(docker_file.parent), tag=self.image_name)
            container = docker_client.containers.create(
                image=self.image_name,
                name=self.container_name,
                command="sleep infinity",
                detach=True,
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
            if self.keep_container:
                logger.info("Keeping container running")
            else:
                logger.info("Stopping container")
                container.stop()
                logger.info("Removing container")
                container.remove()
        size = humanfriendly.format_size(image.attrs["Size"])
        elapsed = pretty_print.elapsed(start)
        logger.info(f"Built Docker image {self.image_name} size {size} in {elapsed}.")


# if __name__ == "__main__":
#     p = importlib.resources.files("exasol.ds.sandbox.lib.dss_docker").joinpath("Dockerfile").parent
#     print(f'parent {p}')
