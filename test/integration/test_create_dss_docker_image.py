import docker
import logging
import os
import pytest
import re
import requests
import tenacity
import time
import typing

from datetime import datetime
from tenacity.retry import (
    retry_if_exception_type,
    retry_if_not_result,
)
from tenacity import Retrying
from docker.models.containers import Container
from pathlib import Path
from re import Pattern
from contextlib import contextmanager
from tenacity.wait import wait_fixed
from tenacity.stop import stop_after_delay
from typing import Set, Tuple
from datetime import datetime, timedelta
from inspect import cleandoc

from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib import pretty_print
from test.docker.in_memory_build_context import InMemoryBuildContext
from test.docker.image import (
    DockerImageSpec,
    image,
    pull as pull_docker_image,
)
from test.docker.container import (
    container,
    container_context,
    DOCKER_SOCKET_CONTAINER,
    sanitize_container_name,
    wait_for,
    wait_for_socket_access,
)


DOCKER_SOCKET_HOST = "/var/run/docker.sock"

_logger = logging.getLogger(__name__)


@pytest.fixture
def dss_docker_container(request, dss_docker_image, jupyter_port):
    mapped_ports = { f'{jupyter_port}/tcp': jupyter_port }
    yield from container(
        request,
        image=dss_docker_image.image_name,
        ports=mapped_ports,
        volumes={DOCKER_SOCKET_HOST: {
            'bind': DOCKER_SOCKET_CONTAINER,
            'mode': 'rw', }, },
    )

@pytest.fixture
def dss_container_context(request, dss_docker_image):
    def context(docker_socket_host: Path):
        return container_context(
            request,
            image_name=dss_docker_image.image_name,
            volumes={ docker_socket_host: {
                'bind': DOCKER_SOCKET_CONTAINER,
                'mode': 'rw', }, },
        )

    return context


@pytest.fixture
def ubuntu_container_context(request, docker_auth):
    spec = DockerImageSpec("ubuntu", "20.04")
    pull_docker_image(spec, docker_auth)
    def context(path_on_host: Path, path_in_container: str):
        return container_context(
            request,
            image_name=spec.name,
            command="sleep infinity",
            volumes={ path_on_host: {
                'bind': path_in_container,
                'mode': 'rw', }, },
        )
    return context


def retry(exception: typing.Type[BaseException], timeout: timedelta):
    return tenacity.retry(
        retry=retry_if_exception_type(exception),
        wait=wait_fixed(timeout/10),
        stop=stop_after_delay(timeout),
    )


def assert_exec_run(container: Container, command: str, **kwargs) -> str:
    """
    Execute command in container and verify success.
    """
    exit_code, output = container.exec_run(command, **kwargs)
    output = output.decode("utf-8").strip()
    assert exit_code == 0, output
    return output


class SocketInspector:
    def __init__(self, context_provider, socket_on_host: Path):
        self._context_provider = context_provider
        self.socket_on_host = socket_on_host
        self._container = None
        self._context = None

    def __enter__(self):
        self._context = self._context_provider(self.socket_on_host)
        self._container = self._context.__enter__()
        wait_for_socket_access(self._container)
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self._container = None
        self._context.__exit__(exc_type, exc, exc_tb)

    def run(self, command: str, **kwargs) -> str:
        return assert_exec_run(self._container, command, **kwargs)

    def numeric_gid(self, group_entry: str) -> int:
        """group_entry is "ubuntu:x:971:", for example"""
        return int(group_entry.split(':')[2])

    def get_gid(self, group_name: str) -> int:
        output = self.run(f"getent group {group_name}")
        return self.numeric_gid(output)

    def get_unassigned_gid(self) -> int:
        """
        Return a new gid, that is not used for any other group, yet.
        """
        gid = 0
        for line in self.run("cat /etc/group").splitlines():
            if not line.startswith(f"nogroup:"):
                gid = max(gid, self.numeric_gid(line))
        return gid + 1

    def assert_jupyter_member_of(self, group_name: str):
        output = self.run(f"getent group {group_name}")
        members = output.split(":")[3].split(",")
        assert "jupyter" in members

    def assert_write_to_socket(self):
        signal = f"Is there anybody out there {datetime.now()}?"
        self.run(
            f'bash -c "echo {signal} > {DOCKER_SOCKET_CONTAINER}"',
            user="jupyter")
        assert signal == self.socket_on_host.read_text().strip()


@pytest.fixture
def socket_inspector(dss_container_context, accessible_file):
    yield SocketInspector(dss_container_context, accessible_file)


class GroupChanger:
    def __init__(self, context_provider):
        self._context_provider = context_provider

    def chgrp(self, gid: int, path_on_host: Path):
        path_in_container = "/mounted"
        with self._context_provider(path_on_host, path_in_container) as container:
            assert_exec_run(container, f"chgrp {gid} {path_in_container}")


@pytest.fixture
def group_changer(ubuntu_container_context):
    return GroupChanger(ubuntu_container_context)


def test_jupyterlab(dss_docker_container, jupyter_port):
    """"
    Test that jupyterlab is configured properly
    """
    container = dss_docker_container
    ip_address = container.attrs['NetworkSettings']['IPAddress']
    if ip_address == "":
        ip_address = "localhost"
    url = f"http://{ip_address}:{jupyter_port}/lab"

    @retry(requests.exceptions.ConnectionError, timedelta(seconds=5))
    def request_with_retry(url: str) -> requests.Response:
        return requests.get(url)

    start = datetime.now()
    response = request_with_retry(url)
    assert response.status_code == 200


def test_import_notebook_connector(dss_docker_container):
    command = ('/home/jupyter/jupyterenv/bin/python'
               ' -c "import exasol.nb_connector.secret_store"')
    assert_exec_run(dss_docker_container, command)


def test_install_notebooks(dss_docker_container):
    def filename_set(string: str) -> Set[str]:
        return set(re.split(r'\s+', string.strip()))

    wait_for(dss_docker_container, "entrypoint.py: Copied notebooks")
    output = assert_exec_run(
        dss_docker_container,
        "ls --indicator-style=slash /home/jupyter/notebooks",
    )

    actual = filename_set(output)
    expected = filename_set("""
        transformers/
        sklearn/
        cloud/
        sagemaker/
    """)
    assert actual.issuperset(expected)


def test_docker_socket_access(dss_docker_container):
    wait_for_socket_access(dss_docker_container)
    output = assert_exec_run(
        dss_docker_container,
        "docker ps", user="jupyter")
    assert re.match(r"^CONTAINER ID +IMAGE .*", output)


def test_insufficient_group_permissions_on_docker_socket(dss_container_context, non_accessible_file):
    """
    This test cannot wait for a specifc log message but only for the
    container's entrypoint _trying_ to access the Docker socket.

    The test expects the trial to fail and verifies the failure based on
    the exception added to the Docker log.
    """
    socket = non_accessible_file
    with dss_container_context(socket) as container:
        time.sleep(1)
        expected = "PermissionError: No rw permissions for group in -rw------- /var/run/docker.sock."
        assert expected in container.logs().decode("utf-8")


def test_docker_socket_on_host_touched(dss_container_context, fake_docker_socket_on_host):
    """
    Verify that when mounting the docker socket from the host's file
    system into the container, the permissions and owner of the original
    socket in the host's file system remain unchanged.

    The test uses a fake_docker_socket_on_host to maximize the chance of
    potential changes.
    """
    socket = fake_docker_socket_on_host
    stat_before = socket.stat()
    with dss_container_context(socket) as container:
        wait_for_socket_access(container)

    assert stat_before == socket.stat()


# def test_write_socket_known_gid(socket_inspector, group_changer):
#     with socket_inspector as inspector:
#         gid = inspector.get_gid("ubuntu")
#     group_changer.chgrp(gid, socket_inspector.socket_on_host)
#     with socket_inspector as inspector:
#         inspector.assert_jupyter_member_of("ubuntu")
#         inspector.assert_write_to_socket()


@contextmanager
def added_group(request, base_image, gid, group_name):
    # dss_docker_image.image_name
    dockerfile_content = cleandoc(
        f"""
        FROM {base_image}
        RUN sudo groupadd --gid {gid} {group_name}
        """
    )
    with InMemoryBuildContext() as context:
        context.add_string_to_file(name="Dockerfile", string=dockerfile_content)
    yield from image(
        request,
        name=f"ai_lab_with_additional_group",
        fileobj=context.fileobj,
        custom_context=True,
    )


def altered_inspector(request, image_name: str, socket_on_host: Path):
    def context_provider(socket_on_host):
        return container_context(
            request,
            image_name=image_name,
            volumes={ socket_on_host: {
                'bind': DOCKER_SOCKET_CONTAINER,
                'mode': 'rw', }, },
        )
    return SocketInspector(context_provider, socket_on_host)


def test_write_socket_known_gid(request, dss_docker_image, socket_inspector, group_changer):
    initial_inspector = socket_inspector
    with initial_inspector as inspector:
        gid = inspector.get_unassigned_gid()

    socket_on_host = initial_inspector.socket_on_host
    group_changer.chgrp(gid, socket_on_host)

    # create new image based on dss_docker_image but with an additional
    # group with gid set to the one inquired before
    base_image = dss_docker_image.image_name
    group_name = "artifical_group"
    with added_group(request, base_image, gid, group_name) as image:
        with altered_inspector(request, image.id, socket_on_host) as inspector:
            inspector.assert_jupyter_member_of(group_name)
            inspector.assert_write_to_socket()


def test_write_socket_unknown_gid(socket_inspector, group_changer):
    with socket_inspector as inspector:
        gid = inspector.get_unassigned_gid()
    group_changer.chgrp(gid, socket_inspector.socket_on_host)
    with socket_inspector as inspector:
        assert gid == inspector.get_gid("docker")
        inspector.assert_jupyter_member_of("docker")
        inspector.assert_write_to_socket()
