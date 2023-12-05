import contextlib
import docker
import json
import logging
import pytest
import re
import requests
import time

from exasol.ds.sandbox.lib.dss_docker import DssDockerImage

from test.integration.local_docker_registry import (
    custom_docker_registry_context,
    LocalDockerRegistry,
    local_docker_registry_context,
)

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def normalize_request_name(name: str):
    name = re.sub(r"[\[\]._]+", "_", name)
    return re.sub(r"^_+|_+$", "", name)


@contextlib.contextmanager
def tagged_image(
        dss_docker_image: DssDockerImage,
        registry: LocalDockerRegistry,
        tag: str = None,
):
    """
    Prepend host and port of LocalDockerRegistry to the repository name of the
    DssDockerImage to enable pushing the image to the local registry.
    """
    new_repo = f"{registry.host_and_port}/{dss_docker_image.repository}"
    client = docker.from_env()
    tag = tag or dss_docker_image.version
    _logger.info(f'tagging image to {new_repo}:{tag}')
    image = client.images.get(dss_docker_image.image_name)
    image.tag(new_repo, tag)
    tagged = DssDockerImage(new_repo, tag)
    tagged.registry = registry
    try:
        yield tagged
    finally:
        docker.from_env().images.remove(tagged.image_name)


@pytest.fixture(scope="session")
def docker_registry(request):
    """
    Provide a context for creating a LocalDockerRegistry accepting
    parameter ``repository``.

    You can provide cli option ``--docker-registry HOST:PORT`` to pytest in
    order reuse an already running Docker container as registry.
    """
    existing = request.config.getoption("--docker-registry")
    if existing is not None:
        yield LocalDockerRegistry(existing)
        return

    test_name = normalize_request_name(request.node.name)
    container_name = f"{test_name}_registry"

    port = find_free_port()
    client = docker.from_env()
    _logger.debug("Pulling Docker image with Docker registry")
    client.images.pull(repository="registry", tag="2")
    _logger.debug(f"Starting container {container_name}")
    try:
        client.containers.get(container_name).remove(force=True)
    except:
        pass
    container = client.containers.run(
        image="registry:2",
        name=container_name,
        ports={5000: port},
        detach=True,
    )
    time.sleep(10)
    _logger.debug(f"Finished starting container {container_name}")
    try:
        yield LocalDockerRegistry(f"localhost:{port}")
    finally:
        _logger.debug("Stopping container")
        container.stop()
        _logger.debug("Removing container")
        container.remove()


def test_push_tag(dss_docker_image, docker_registry):
    repo = dss_docker_image.repository
    tag = "999.9.9"
    with tagged_image(dss_docker_image, docker_registry, tag) as tagged:
        docker_registry.push(tagged.repository, tag)
    assert repo in docker_registry.repositories
    assert tag in docker_registry.images(repo)["tags"]


def test_push_via_image(dss_docker_image, docker_registry):
    repo = dss_docker_image.repository
    tag = dss_docker_image.version
    with tagged_image(dss_docker_image, docker_registry) as tagged:
        tagged._push()
    assert repo in docker_registry.repositories
    assert tag in docker_registry.images(repo)["tags"]
