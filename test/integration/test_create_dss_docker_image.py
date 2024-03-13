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

from tenacity.retry import (
    retry_if_exception_type,
    retry_if_not_result,
)
from tenacity import Retrying
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


# add tests for
# - error for insufficient group permissions on docker.sock
# - docker socket gid matches another group inside container
# - docker socket gid matches no group inside container
# tests require to inspect available groups inside docker container
# docker run -v /home/chku/tmp/a:/aa ubuntu chgrp 1200 /aa

def test_docker_socket_on_host_touched(request, dss_docker_image, fake_docker_socket_on_host):
    """
    Verify that when mounting the docker socket from the host's file
    system into the container, the permissions and owner of the original
    socket in the host's file system remain unchanged.

    The test uses a temp file to increase the chance of potential changes.
    """
    @contextmanager
    def my_container(docker_socket_host):
        yield from container(
            request,
            base_name="C",
            image=dss_docker_image.image_name,
            volumes={docker_socket_host: {
                'bind': DOCKER_SOCKET_CONTAINER,
                'mode': 'rw', }, },
        )

    socket = fake_docker_socket_on_host
    stat_before = socket.stat()
    with my_container(socket) as c:
        wait_for_socket_access(c)

    assert stat_before == socket.stat()
