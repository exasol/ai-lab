import re

import docker
from datetime import timedelta

from re import Pattern
from tenacity import Retrying
from tenacity.wait import wait_fixed
from tenacity.stop import stop_after_delay
from typing import Generator, Union
from docker.models.containers import Container
from docker.models.images import Image


def sanitize_test_name(test_name: str):
    test_name = re.sub('[^0-9a-zA-Z]+', '_', test_name)
    test_name = re.sub('_+', '_', test_name)
    return test_name


def container(request, base_name: str, image: Union[Image, str], start: bool = True, **kwargs) \
        -> Generator[Container, None, None]:
    """
    Create a Docker container based on the specified Docker image.
    """
    client = docker.from_env()
    base_container_name = base_name.replace("-", "_")
    test_name = sanitize_test_name(str(request.node.name))
    container_name = f"{base_container_name}_{test_name}"
    try:
        image_name = image.id if hasattr(image, "id") else image
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
