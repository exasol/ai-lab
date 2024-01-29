import docker
import pytest

from exasol.ds.sandbox.lib.dss_docker import DssDockerImage


def pytest_addoption(parser):
    parser.addoption(
        "--dss-docker-image", default=None,
        help="Name and version of existing Docker image to use for tests",
    )
    parser.addoption(
        "--keep-dss-docker-image", action="store_true", default=False,
        help="Keep the created dss docker image for inspection or reuse."
    )
    parser.addoption(
        "--docker-image-notebook-test", default=None,
        help="Name and version of existing Docker image for Notebook testing to use for tests",
    )
    parser.addoption(
        "--keep-docker-image-notebook-test", action="store_true", default=False,
        help="Keep the created notebook-test docker image for inspection or reuse.",
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
    keep_image = request.config.getoption(f"--keep-dss-docker-image")
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
        if not keep_image:
            docker.from_env().images.remove(testee.image_name, force=True)
