import docker
import pytest

from exasol.ds.sandbox.lib.dss_docker import DssDockerImage


def pytest_addoption(parser):
    parser.addoption(
        "--dss-docker-image", default=None,
        help="Name and version of existing Docker image to use for tests",
    )
    parser.addoption(
        "--docker-registry", default=None, metavar="HOST:PORT",
        help="Docker registry for pushing Docker images to",
    )


@pytest.fixture(scope="session")
def dss_docker_image(request):
    """
    If dss_docker_image_name is provided then don't create an image but
    reuse the existing image as specified by cli option
    --ds-docker-image-name.
    """
    existing = request.config.getoption("--dss-docker-image")
    if existing and ":" in existing:
        name, version = existing.split(":")
        yield DssDockerImage(name, version)
        return

    testee = DssDockerImage(
        "my-repo/dss-test-image",
        version=f"{DssDockerImage.timestamp()}",
        keep_container=False,
    )
    testee.create()
    try:
        yield testee
    finally:
        docker.from_env().images.remove(testee.image_name)
