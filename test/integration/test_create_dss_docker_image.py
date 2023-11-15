import docker
import pytest
import re
import requests
import tenacity
import time
import typing

from tenacity.retry import retry_if_exception_type
from tenacity.wait import wait_fixed
from tenacity.stop import stop_after_delay
from typing import Set
from datetime import datetime, timedelta
from exasol.ds.sandbox.lib.dss_docker import DssDockerImage
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib import pretty_print


@pytest.fixture(scope="session")
def dss_docker_image():
    testee = DssDockerImage(
        "my-repo/dss-test-image",
        version=f"{DssDockerImage.timestamp()}",
        publish=False,
        keep_container=False,
    )
    testee.create()
    try:
        yield testee
    finally:
        docker.from_env().images.remove(testee.image_name)


@pytest.fixture
def dss_docker_container(dss_docker_image):
    client = docker.from_env()
    mapped_ports = {'8888/tcp': 8888}
    container = client.containers.create(
        image=dss_docker_image.image_name,
        name=dss_docker_image.container_name,
        command="sleep infinity",
        detach=True,
        ports=mapped_ports,
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


def test_jupyterlab(dss_docker_container):
    """"
    Test that jupyterlab is configured properly
    """
    jupyter_command = (
        "/root/jupyterenv/bin/jupyter-lab"
        " --notebook-dir=/root/notebooks"
        " --no-browser"
        " --allow-root"
    )
    container = dss_docker_container
    container.exec_run(jupyter_command, detach=True)
    container.reload()
    ip_address = container.attrs['NetworkSettings']['IPAddress']
    url = f"http://{ip_address}:8888/lab"

    @retry(requests.exceptions.ConnectionError, timedelta(seconds=5))
    def request_with_retry(url: str) -> requests.Response:
        return requests.get(url)

    start = datetime.now()
    response = request_with_retry(url)
    print(f'{url} responded after {pretty_print.elapsed(start)}.')
    assert response.status_code == 200


def test_install_notebook_connector(dss_docker_container):
    container = dss_docker_container
    command = '/root/jupyterenv/bin/python -c "import exasol.secret_store"'
    exit_code, output = container.exec_run(command)
    output = output.decode('utf-8').strip()
    assert exit_code == 0, f'Got output "{output}".'


def test_install_notebooks(dss_docker_container):
    def filename_set(string: str) -> Set[str]:
        return set(re.split(r'\s+', string.strip()))

    exit_code, output = dss_docker_container.exec_run("ls -p /root/notebooks")
    output = output.decode('utf-8').strip()
    assert exit_code == 0, f'Got output "{output}".'

    actual = filename_set(output)
    expected = filename_set("""
        access_store_ui.ipynb
        sklearn/
        cloud/
        sagemaker/
    """)
    assert actual.issuperset(expected)
