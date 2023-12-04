import contextlib
import docker
import json
import logging
import pytest
import re
import requests
import time

from docker.client import DockerClient
from typing import Callable, Optional

from test.ports import find_free_port
from exasol.ds.sandbox.lib.dss_docker.push_image import DockerRegistry
from exasol.ds.sandbox.lib.dss_docker import DssDockerImage

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def normalize_request_name(name: str):
    name = re.sub(r"[\[\]._]+", "_", name)
    return re.sub(r"^_+|_+$", "", name)


class LocalDockerRegistry(DockerRegistry):
    """
    Simulate Docker registry by running a local Docker container and using
    the registry inside.

    Please note for pushing images to a Docker registry with host or port
    differing from the official address requires to tag images in advance.

    So host and port must be prepended to property ``repository`` of the
    image.
    """
    def __init__(self, host_and_port: str, repo_name: str):
        super().__init__(
            f'{host_and_port}/{repo_name}',
            username=None,
            password=None,
        )
        self.host_and_port = host_and_port
        self.repo_name = repo_name

    @property
    def url(self):
        return f'http://{self.host_and_port}'

    @property
    def images(self):
        url = f"{self.url}/v2/{self.repo_name}/tags/list"
        result = requests.request("GET", url)
        images = json.loads(result.content.decode("UTF-8"))
        return images

    @property
    def repositories(self):
        url = f"{self.url}/v2/_catalog/"
        result = requests.request("GET", url)
        repos = json.loads(result.content.decode("UTF-8"))["repositories"]
        return repos

    def tag_image(self, image_name: str, tag: str):
        image = self.client().images.get(image_name)
        _logger.info(f'tagging image to {self.repository}:{tag}')
        image.tag(self.repository, tag)


@pytest.fixture(scope="session")
def docker_registry(request):
    """
    Provide a context for creating a LocalDockerRegistry accepting
    parameter ``repository``.

    You can provide cli option ``--docker-registry HOST:PORT`` to pytest in
    order reuse an already running Docker container as registry.
    """
    def make_context(host_and_port: str) -> Callable[[str], LocalDockerRegistry]:
        @contextlib.contextmanager
        def context(repository: str) -> DockerRegistry:
            yield LocalDockerRegistry(host_and_port, repository)
        return context

    existing = request.config.getoption("--docker-registry")
    if existing is not None:
        yield make_context(existing)
        return

    test_name = normalize_request_name(request.node.name)
    container_name = f"{test_name}_registry"
    port = find_free_port()

    _logger.debug("Pulling Docker image with Docker registry")
    client = docker.from_env()
    client.images.pull(repository="registry", tag="2")
    _logger.debug(f"Start container of {container_name}")
    try:
        client.containers.get(container_name).remove(force=True)
    except:
        pass
    container = client.containers.run(
        image="registry:2",
        name=container_name,
        ports={5000: port},
        detach=True
    )
    time.sleep(10)
    _logger.debug(f"Finished start container of {container_name}")
    try:
        yield make_context(f"localhost:{port}")
    finally:
        _logger.debug("Stopping container")
        container.stop()
        _logger.debug("Removing container")
        container.remove()


def test_push(dss_docker_image, docker_registry):
    tag = "999.9.9"
    with docker_registry(dss_docker_image.repository) as registry:
        registry.tag_image(dss_docker_image.image_name, tag)
        registry.push(tag)
        assert dss_docker_image.repository in registry.repositories
        assert tag in registry.images["tags"]


def test_push_via_image(dss_docker_image, docker_registry):
    repo = dss_docker_image.repository
    tag = dss_docker_image.version
    with docker_registry(repo) as registry:
        dss_docker_image.registry = registry
        registry.tag_image(dss_docker_image.image_name, tag)
        dss_docker_image._push()
        assert repo in registry.repositories
        assert tag in registry.images["tags"]
