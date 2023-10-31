import tempfile

import requests
import shutil
import time
from pathlib import Path
from inspect import cleandoc

import docker
import pytest
from docker.types import Mount

from exasol.ds.sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol.ds.sandbox.lib.ansible.ansible_repository import AnsibleResourceRepository, \
    default_repositories
from exasol.ds.sandbox.lib.ansible.ansible_run_context import AnsibleRunContext
from exasol.ds.sandbox.lib.setup_ec2.run_install_dependencies import run_install_dependencies
import test.ansible

TEST_CONTAINER_NAME = "ansible-test"
TEST_CONTAINER_IMAGE_TAG = "data_science_sandbox_test_container:latest"

# AWS AMI Image is based on Ubuntu20.04 server.
# So we try to simulate same environment here.
DOCKERFILE_CONTENT = cleandoc(
    """
    FROM ubuntu:20.04
    ENV DEBIAN_FRONTEND noninteractive
    RUN apt-get update && apt-get install -y ubuntu-server
    """
)

@pytest.fixture(scope="session")
def dockerfile(tmp_path_factory):
    dockerfile = tmp_path_factory.mktemp("test_container") / "Dockerfile"
    with dockerfile.open("w") as f:
        print(DOCKERFILE_CONTENT, file = f)
    yield dockerfile
    shutil.rmtree(str(dockerfile.parent))


@pytest.fixture(scope="session")
def docker_test_container(test_config, dockerfile):
    with tempfile.TemporaryDirectory() as tmp_path:
        docker_env = docker.from_env()
        docker_env.images.build(
            path=str(dockerfile.parent),
            tag=TEST_CONTAINER_IMAGE_TAG
        )
        socket_mount = Mount("/var/run/docker.sock", "/var/run/docker.sock", type="bind")
        tmp_mount = Mount(tmp_path, tmp_path, type="bind")
        mapped_ports = {'8888/tcp': 8888}
        test_container = docker_env.containers.create(image=TEST_CONTAINER_IMAGE_TAG,
                                                      name=TEST_CONTAINER_NAME, mounts=[socket_mount, tmp_mount],
                                                      command="sleep infinity", detach=True, ports=mapped_ports)
        test_container.start()
        repos = default_repositories + (AnsibleResourceRepository(test.ansible),)
        ansible_run_context = \
            AnsibleRunContext(playbook="slc_setup_test.yml",
                              extra_vars={"test_docker_container": test_container.name,
                                          "slc_dest_folder": f"{tmp_path}/script-languages-release"})
        try:
            run_install_dependencies(AnsibleAccess(), configuration=test_config,
                                     host_infos=tuple(), ansible_run_context=ansible_run_context,
                                     ansible_repositories=repos)
            yield test_container, tmp_path
            # Note: script-languages-release will be cloned by ansible within the docker container.
            #       Because the docker container runs as root, the repository will be owned by root.
            #       For simplicity, we delete the folder from within the Docker container (as root).
            #       Otherwise, we get a permission problem when tmp_path tries to clean-up itself.
        finally:
            test_container.exec_run(f"rm -rf {tmp_path}/script-languages-release")
            test_container.stop()
            test_container.remove()


def test_install_dependencies_jupyterlab(docker_test_container):
    """"
    Test that jupyterlab is configured properly
    """
    jupyter_command = "/root/jupyterenv/bin/jupyter-lab --notebook-dir=/root/notebooks --no-browser --allow-root"
    container, _ = docker_test_container
    container.exec_run(jupyter_command, detach=True)
    time.sleep(5.0)
    container.reload()
    docker_test_container_ip = container.attrs['NetworkSettings']['IPAddress']
    http_conn = requests.get(f"http://{docker_test_container_ip}:8888/lab")
    assert http_conn.status_code == 200


def test_install_dependencies_script_languages(docker_test_container):
    """"
    Test that script-languages-release is configured properly
    """
    container, tmp_dir = docker_test_container
    slc_command = "./exaslct build --flavor-path ./flavors/python-3.8-minimal-EXASOL-6.2.0"
    exit_code_build, output = container.exec_run(slc_command, workdir=f"{tmp_dir}/script-languages-release")
    print("------------ begin output build -------------------------")
    print(output)
    print("------------ end output build -------------------------")
    slc_command = "./exaslct clean-flavor-images --flavor-path ./flavors/python-3.8-minimal-EXASOL-6.2.0"
    exit_code_cleanup, output = container.exec_run(slc_command, workdir=f"{tmp_dir}/script-languages-release")
    print("------------ begin output clean-flavor-images -------------------------")
    print(output)
    print("------------ end output clean-flavor-images -------------------------")

    assert exit_code_build == 0
    assert exit_code_cleanup == 0


def test_install_notebook_connector(docker_test_container):
    container, _ = docker_test_container
    command = f'/root/jupyterenv/bin/python -c "import exasol.secret_store"'
    exit_code, output = container.exec_run(command)
    output = output.decode('utf-8').strip()
    assert exit_code == 0, f'Got output "{output}".'
