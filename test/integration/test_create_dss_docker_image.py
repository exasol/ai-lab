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
from typing import Set, Tuple, Union
from datetime import datetime, timedelta
from exasol.ds.sandbox.lib.dss_docker import DssDockerImage
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib import pretty_print
from test.docker.container import container


DOCKER_SOCKET_HOST = "/var/run/docker.sock"
DOCKER_SOCKET_CONTAINER = "/var/run/docker.sock"


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


def wait_for(
        container,
        log_message: Union[str, Pattern],
        timeout: timedelta = timedelta(seconds=5),
):
    """
    Wait until container log contains the specified string or regular
    expression.
    """
    for attempt in Retrying(
            wait=wait_fixed(timeout/10),
            stop=stop_after_delay(timeout),
    ):
        with attempt:
            logs = container.logs().decode("utf-8").strip()
            if isinstance(log_message, Pattern):
                matches = log_message.search(logs)
            else:
                matches = log_message in logs
            if not matches:
                raise Exception()


def wait_for_socket_access(container):
    wait_for(
        container,
        f"entrypoint.py: Enabled access to {DOCKER_SOCKET_CONTAINER}",
    )


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


def test_install_notebook_connector(dss_docker_container):
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
def socket_on_host(tmp_path):
    socket = tmp_path / "socket.txt"
    socket.touch()
    socket.chmod(0o660)
    return socket


def test_docker_socket_on_host_touched(request, dss_docker_image, socket_on_host):
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

    stat_before = socket_on_host.stat()
    with my_container(socket_on_host) as c:
        wait_for_socket_access(c)
        exit_code, output = c.exec_run(f"docker ps")
    output = output.decode("utf-8").strip()
    assert exit_code == 1 and \
        re.match(r"(Cannot connect|permission denied)", output) and \
        stat_before == socket_on_host.stat()
