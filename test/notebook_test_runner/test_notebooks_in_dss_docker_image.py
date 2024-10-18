import io
import logging
import os
import time
from inspect import cleandoc
from pathlib import Path
from datetime import timedelta

import pytest

from test.docker.exec_run import exec_command
from test.docker.image import image
from test.docker.in_memory_build_context import InMemoryBuildContext
from test.docker.container import (
    container,
    wait_for_socket_access,
    wait_for,
)

TEST_RESOURCE_PATH = Path(__file__).parent.parent / "notebooks"
_logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def notebook_test_dockerfile_content(dss_docker_image) -> str:
    yield cleandoc(
        f"""
        FROM {dss_docker_image.image_name}
        COPY notebooks/* /tmp/notebooks/
        RUN sudo mv /tmp/notebooks/* "$NOTEBOOK_FOLDER_INITIAL" && sudo rmdir /tmp/notebooks/
        RUN sudo chown -R jupyter:jupyter "$NOTEBOOK_FOLDER_INITIAL"
        WORKDIR $NOTEBOOK_FOLDER_INITIAL
        RUN sudo "$VIRTUAL_ENV/bin/python3" -m pip install -r test_dependencies.txt
        RUN sudo chown -R jupyter:jupyter "$VIRTUAL_ENV"
        """
    )


@pytest.fixture(scope="session")
def notebook_test_build_context(notebook_test_dockerfile_content) -> io.BytesIO:
    with InMemoryBuildContext() as context:
        context.add_string_to_file(name="Dockerfile", string=notebook_test_dockerfile_content)
        context.add_host_path(host_path=str(TEST_RESOURCE_PATH), path_in_tar="../notebooks", recursive=True)
    yield context.fileobj


@pytest.fixture(scope="session")
def notebook_test_image(request, notebook_test_build_context):
    _logger.debug('building docker image "notebook_test"')
    yield from image(request,
                     name="notebook_test",
                     fileobj=notebook_test_build_context,
                     custom_context=True,
                     print_log=True)

@pytest.fixture()
def notebook_test_container(request, notebook_test_image):
    _logger.debug(f'Starting container context for docker image {notebook_test_image.id}')
    yield from container(
        request,
        notebook_test_image,
        volumes={'/var/run/docker.sock': {
                'bind': '/var/run/docker.sock',
                'mode': 'rw', }, },
    )


@pytest.fixture()
def notebook_test_container_with_log(notebook_test_container):
    container = notebook_test_container
    wait_for_socket_access(container)
    logs = container.logs().decode("utf-8").strip()
    print(f"Container Logs: {logs or '(empty)'}", flush=True)
    yield container


def test_notebook(notebook_test_container_with_log, notebook_test_file, notebook_test_backend):
    _logger.info(f"Running notebook tests for {notebook_test_file} at {notebook_test_backend}")
    container = notebook_test_container_with_log
    command_echo_virtual_env = 'bash -c "echo $VIRTUAL_ENV"'
    virtual_env = exec_command(command_echo_virtual_env, container)
    command_run_test = (
        f"{virtual_env}/bin/python"
        f" -m pytest --setup-show -s --backend={notebook_test_backend} --itde-nameserver='8.8.8.8' {notebook_test_file}"
    )
    environ = os.environ.copy()
    environ["NBTEST_ACTIVE"] = "TRUE"
    nbtest_environ = {key: value for key, value in environ.items() if (
        key.startswith("NBTEST_") or key.startswith("SAAS_"))}
    exec_command(
        command_run_test,
        container,
        print_output=True,
        environment=nbtest_environ,
        user="jupyter",
    )
