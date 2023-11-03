import docker
import logging
import tempfile
from docker.types import Mount
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
CONTAINER_IMAGE_TAG = "ds-sandbox:latest"
ANSIBLE_CONFIG = ConfigObject(
    time_to_wait_for_polling=0.1,
    slc_version=SLC_VERSION,
)


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s")


def create_image():
    with tempfile.TemporaryDirectory() as tmp_path:
        docker_env = docker.from_env()
        path = Path(__file__).parent
        _logger.info(
            f"Creating docker image {CONTAINER_IMAGE_TAG}"
            f" from {path / 'Dockerfile'}"
            f" in tmp path {tmp_path}"
        )
        docker_env.images.build(path=str(path), tag=CONTAINER_IMAGE_TAG)
        socket_mount = Mount("/var/run/docker.sock", "/var/run/docker.sock", type="bind")
        tmp_mount = Mount(tmp_path, tmp_path, type="bind")
        container = docker_env.containers.create(
            image=CONTAINER_IMAGE_TAG,
            name=CONTAINER_NAME,
            mounts=[socket_mount, tmp_mount],
            command="sleep infinity",
            detach=True,
        )
        _logger.info("Starting container")
        container.start()
        extra_vars = {
            "docker_container": container.name,
            # Is it wise / required to use a temp folder here
            # and mount it to docker container?
            "slc_dest_folder": f"{tmp_path}/script-languages-release",
        }
        ansible_run_context = AnsibleRunContext(
            playbook="slc_docker_playbook.yml", extra_vars=extra_vars)
        try:
            run_install_dependencies(
                AnsibleAccess(),
                configuration=ANSIBLE_CONFIG,
                host_infos=tuple(),
                ansible_run_context=ansible_run_context,
                ansible_repositories=ansible_repository.default_repositories,
            )
            # Note: script-languages-release will be cloned by ansible within the docker container.
            #       Because the docker container runs as root, the repository will be owned by root.
            #       For simplicity, we delete the folder from within the Docker container (as root).
            #       Otherwise, we get a permission problem when tmp_path tries to clean-up itself.
        except Exception as ex:
            raise ex
        finally:
            container.commit(
                repository=f"exasol/{CONTAINER_IMAGE_TAG}",
                tag="latest",
            )
            _logger.info("Cleaning up")
            container.exec_run(f"rm -rf {tmp_path}/script-languages-release")
            container.stop()
            container.remove()


if __name__ == "__main__":
    create_image()
