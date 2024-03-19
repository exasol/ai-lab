import docker
import io
import os
import pytest
import re
import requests
import sys
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
from exasol.ds.sandbox.lib.dss_docker import DssDockerImage
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib import pretty_print
from test.docker.container import (
    container,
    DOCKER_SOCKET_CONTAINER,
    wait_for,
    wait_for_socket_access,
)


DOCKER_SOCKET_HOST = "/var/run/docker.sock"


@pytest.fixture
def dss_docker_container(dss_docker_image, jupyter_port):
    client = docker.from_env()
    mapped_ports = { f'{jupyter_port}/tcp': jupyter_port }
    container = client.containers.create(
        image=dss_docker_image.image_name,
        name=dss_docker_image.container_name,
        detach=True,
        ports=mapped_ports,
        volumes={DOCKER_SOCKET_HOST: {
            'bind': DOCKER_SOCKET_CONTAINER,
            'mode': 'rw', }, },
    )
    container.start()
    try:
        yield container
    finally:
        container.stop()
        container.remove()


def retry(exception: typing.Type[BaseException], timeout: timedelta):
    return tenacity.retry(
        retry=retry_if_exception_type(exception),
        wait=wait_fixed(timeout/10),
        stop=stop_after_delay(timeout),
    )


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
    print(f'{url} responded after {pretty_print.elapsed(start)}.')
    assert response.status_code == 200


def test_import_notebook_connector(dss_docker_container):
    container = dss_docker_container
    command = ('/home/jupyter/jupyterenv/bin/python'
               ' -c "import exasol.nb_connector.secret_store"')
    exit_code, output = container.exec_run(command)
    output = output.decode('utf-8').strip()
    assert exit_code == 0, f'Got output "{output}".'


def test_install_notebooks(dss_docker_container):
    def filename_set(string: str) -> Set[str]:
        return set(re.split(r'\s+', string.strip()))

    wait_for(dss_docker_container, "entrypoint.py: Copied notebooks")
    exit_code, output = dss_docker_container.exec_run(
        "ls --indicator-style=slash /home/jupyter/notebooks"
    )
    output = output.decode('utf-8').strip()
    assert exit_code == 0, f'Got output "{output}".'

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
    exit_code, output = dss_docker_container.exec_run("docker ps", user="jupyter")
    output = output.decode("utf-8").strip()
    assert exit_code == 0 and re.match(r"^CONTAINER ID +IMAGE .*", output)


@pytest.fixture
def dss_container_context(request, dss_docker_image):
    @contextmanager
    def context(docker_socket_host: Path):
        volumes = None
        if docker_socket_host is not None:
            volumes = { docker_socket_host: {
                'bind': DOCKER_SOCKET_CONTAINER,
                'mode': 'rw', }, }
        yield from container(
            request,
            base_name="C",
            image=dss_docker_image.image_name,
            volumes=volumes,
        )
    return context


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


class SocketManipulator:
    def __init__(self, context_provider, socket_on_host: Path):
        self._context_provider = context_provider
        self._socket_on_host = socket_on_host
        self._container = None

    @contextmanager
    def context(self):
        with self._context_provider(self._socket_on_host) as container:
            self._container = container
            yield self
            self._container = None

    def run(self, command: str, **kwargs) -> str:
        """
        Execute command in container and verify success.
        """
        exit_code, output = self._container.exec_run(command, **kwargs)
        output = output.decode("utf-8").strip()
        assert exit_code == 0, output
        return output

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

    def chgrp_of_docker_socket_on_host(self, gid: str):
        self.run(f"chgrp {gid} {DOCKER_SOCKET_CONTAINER}", user="root")

    def assert_jupyter_member_of(self, group_name: str):
        output = self.run(f"getent group {group_name}")
        members = output.split(":")[3].split(",")
        assert "jupyter" in members

    def assert_write_to_socket(self):
        signal = f"Is there anybody out there {datetime.now()}?"
        self.run(f'bash -c "echo {signal} > {DOCKER_SOCKET_CONTAINER}"')
        assert signal == self._socket_on_host.read_text().strip()


@pytest.fixture
def socket_manipulator(dss_container_context, accessible_file):
    yield SocketManipulator(dss_container_context, accessible_file)


def test_write_socket_known_gid(socket_manipulator):
    with socket_manipulator.context() as testee:
        gid = testee.get_gid("ubuntu")
        testee.chgrp_of_docker_socket_on_host(gid)

    with socket_manipulator.context() as testee:
        testee.assert_jupyter_member_of("ubuntu")
        testee.assert_write_to_socket()


def test_write_socket_unknown_gid(socket_manipulator):
    with socket_manipulator.context() as testee:
        gid = testee.get_unassigned_gid()
        testee.chgrp_of_docker_socket_on_host(gid)

    with socket_manipulator.context() as testee:
        assert gid == testee.get_gid("docker")
        testee.assert_jupyter_member_of("docker")
        testee.assert_write_to_socket()
