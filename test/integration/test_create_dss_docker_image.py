import docker
import pytest
import requests
import time

from datetime import datetime, timedelta
from exasol.ds.sandbox.lib.dss_docker import DssDockerImage
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib import pretty_print


@pytest.fixture(scope="session")
def dss_docker_image():
    set_log_level("info")
    testee = DssDockerImage(
        "my-repo/dss-test-image",
        version=f"{DssDockerImage.timestamp()}",
        publish=False,
        keep_container=False,
    )
    # print(
    #     "\n- Using"
    #     f' Docker container {testee.container_name}'
    #     f' with image {testee.image_name}'
    # )
    testee.create()
    try:
        yield testee
    finally:
        docker.from_env().images.remove(testee.image_name)


@pytest.fixture(scope="session")
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


def request_with_retry(url: str, timeout: timedelta, verbose:bool = False) -> requests.Response:
    start = datetime.now()
    stop = start + timeout
    interval = (timeout / 10).total_seconds()
    while datetime.now() < stop:
        try:
            result = requests.get(url)
            if verbose:
                elapsed = pretty_print.elapsed(start)
                print(f'{url} responded after {elapsed}.')
            return result
        except requests.exceptions.ConnectionError as ex:
            err = ex
            time.sleep(interval)
    raise err


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
    response = request_with_retry(
        f"http://{ip_address}:8888/lab",
        timeout=timedelta(seconds=5),
    )
    assert response.status_code == 200


def test_install_notebook_connector(dss_docker_container):
    container = dss_docker_container
    command = '/root/jupyterenv/bin/python -c "import exasol.secret_store"'
    exit_code, output = container.exec_run(command)
    output = output.decode('utf-8').strip()
    assert exit_code == 0, f'Got output "{output}".'
