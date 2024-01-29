import re
from typing import Union

import docker
from docker.models.containers import Container
from docker.models.images import Image


def sanitize_test_name(test_name: str):
    test_name = re.sub('[^0-9a-zA-Z]+', '_', test_name)
    test_name = re.sub('_+', '_', test_name)
    return test_name


def container(request, base_name: str, image: Union[Image, str], start: bool = True, **kwargs) -> Container:
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
