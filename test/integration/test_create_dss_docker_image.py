import docker
import logging
import pytest
import requests
import time

from exasol.ds.sandbox.lib.dss_docker import DssDockerImage
from datetime import datetime


@pytest.fixture(scope="session")
def dss_docker_container():
    timestamp = f'{datetime.now().timestamp():.0f}'
    # testee = DssDockerImage(f"dss_container_{timestamp}", f"dss_image_{timestamp}", logging.INFO)
    testee = DssDockerImage("ds-sandbox-docker", f"dss_image_{timestamp}", logging.INFO)
    print(
        "\n- Using"
        f' Docker container {testee.container_name}'
        f' with image {testee.image_name}'
    )
    testee.create()
    client = docker.from_env()
    mapped_ports = {'8888/tcp': 8888}
    container = client.containers.create(
        image=testee.image_name,
        name=testee.container_name,
        command="sleep infinity",
        detach=True,
        ports=mapped_ports,
    )
    container.start()
    try:
        yield container
    finally:
        pass
        container.stop()
        container.remove()
        client.images.remove(testee.image_name)


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
    time.sleep(5.0)
    container.reload()
    ip_address = container.attrs['NetworkSettings']['IPAddress']
    http_conn = requests.get(f"http://{ip_address}:8888/lab")
    assert http_conn.status_code == 200


def test_install_notebook_connector(dss_docker_container):
    container = dss_docker_container
    command = '/root/jupyterenv/bin/python -c "import exasol.secret_store"'
    exit_code, output = container.exec_run(command)
    output = output.decode('utf-8').strip()
    assert exit_code == 0, f'Got output "{output}".'
