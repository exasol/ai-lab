import re

import docker
from datetime import datetime, timedelta

from contextlib import contextmanager
from re import Pattern
from tenacity import Retrying
from tenacity.wait import wait_fixed
from tenacity.stop import stop_after_delay
from typing import Generator, Union
from docker.models.containers import Container
from docker.models.images import Image


def sanitize_container_name(test_name: str):
    test_name = re.sub('[^0-9a-zA-Z-]+', '_', test_name)
    test_name = re.sub('_+', '_', test_name)
    return test_name


def timestamp() -> str:
    return f'{datetime.now().timestamp():.0f}'


def container(
        request,
        image: Union[Image, str],
        suffix: str = None,
        start: bool = True,
        **kwargs,
) -> Generator[Container, None, None]:
    """
    Create a Docker container based on the specified Docker image.
    """
    if suffix is not None:
        suffix = f"_{suffix}"
    image_name = image.id if hasattr(image, "id") else image
    container_name = sanitize_container_name(f"{image_name}_{request.node.name}{suffix}")
    client = docker.from_env()
    try:
        container = client.containers.create(
            image=image_name,
            name=container_name,
            detach=True,
            **kwargs
        )
        if start:
            container.start()
        yield container
    finally:
        client.containers.get(container_name).remove(force=True)
        client.close()


@contextmanager
def container_context(request, image_name: str, **kwargs):
    yield from container(request, image_name, **kwargs)


def wait_for(
        container: Container,
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

DOCKER_SOCKET_CONTAINER = "/var/run/docker.sock"

def wait_for_socket_access(container: Container):
    wait_for(
        container,
        f"entrypoint.py: Enabled access to {DOCKER_SOCKET_CONTAINER}",
    )


def assert_exec_run(container: Container, command: str, **kwargs) -> str:
    """
    Execute command in container and verify success.
    """
    exit_code, output = container.exec_run(command, **kwargs)
    output = output.decode("utf-8").strip()
    assert exit_code == 0, output
    return output
