import docker
import logging
import os
import pytest
import re
import requests
import tenacity
import time
import typing

from tenacity.retry import (
    retry_if_exception_type,
    retry_if_not_result,
)
from tenacity import Retrying
from docker.models.containers import Container
from pathlib import Path
from re import Pattern
from tenacity.wait import wait_fixed
from tenacity.stop import stop_after_delay
from typing import Set, Tuple
from datetime import datetime, timedelta

from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib import pretty_print
from test.docker.image import (
    DockerImageSpec,
    pull as pull_docker_image,
)
from test.docker.container import (
    container,
    container_context,
    assert_exec_run,
    DOCKER_SOCKET_CONTAINER,
    sanitize_container_name,
    wait_for,
    wait_for_socket_access,
)
from test.integration.docker_socket_and_groups import (
    numeric_gid,
    SocketInspector,
    GroupChanger,
    dss_image_with_added_group,
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


@pytest.fixture
def unassigned_gid(request, dss_docker_image):
    def max_gid(groups):
        """Return a new gid, that is not used for any other group, yet."""
        gid = 0
        for line in groups.splitlines():
            if not line.startswith("nogroup:"):
                gid = max(gid, numeric_gid(line))
        return gid

    with container_context(request, dss_docker_image.image_name) as container:
        groups = assert_exec_run(container, "cat /etc/group")
        return max_gid(groups) + 1


def test_write_socket_unknown_gid(
        request,
        unassigned_gid,
        accessible_file,
        group_changer,
        dss_docker_image,
):
    gid = unassigned_gid
    socket_on_host = accessible_file
    group_changer.chgrp(gid, socket_on_host)

    with SocketInspector(
            request,
            dss_docker_image.image_name,
            socket_on_host,
    ) as inspector:
        assert gid == inspector.get_gid("docker")
        inspector.assert_jupyter_member_of("docker")
        inspector.assert_write_to_socket()


def test_write_socket_known_gid(
        request,
        unassigned_gid,
        accessible_file,
        dss_docker_image,
        group_changer,
):
    """
    This test first searches for a group ID (GID) that is not used, yet,
    inside the DSS Docker container.

    The test then assigns this GID to be the owning group of the Docker socket
    in the host's file system and creates another Docker image derived from
    the DSS with an additional group using this very GID.

    Running this new image as Docker container the test then mounts the host's
    Docker socket into the Docker container and verifies if the container's
    entrypoint successfully did add the user `jupyter` to the added group and
    is able to write to to the mounted socket.
    """
    gid = unassigned_gid
    socket_on_host = accessible_file
    group_changer.chgrp(gid, socket_on_host)

    base_image = dss_docker_image.image_name
    group_name = "artifical_group"
    with dss_image_with_added_group(request, base_image, gid, group_name) as image:
        with SocketInspector(request, image.id, socket_on_host) as inspector:
            inspector.assert_jupyter_member_of(group_name)
            inspector.assert_write_to_socket()
