import docker
import os
import pytest
import stat

from exasol.ds.sandbox.lib.dss_docker import (
    DssDockerImage,
    USER_ENV,
    PASSWORD_ENV,
)


def pytest_addoption(parser):
    def add_options_for_docker_image(base_name: str, test_group: str = None):
        if test_group is None:
            test_group = f"tests with {base_name}"
        parser.addoption(
            f"--docker-image-{base_name}", default=None,
            help="Name and version of existing Docker image to use for {test_group}",
        )
        parser.addoption(
            f"--keep-docker-image-{base_name}", action="store_true", default=False,
            help=f"Keep the created Docker image for {test_group} for subsequent inspection or reuse.",
        )

    parser.addoption(
        "--dss-docker-image", default=None,
        help="Name and version of existing Docker image to use for tests",
    )
    parser.addoption(
        "--keep-dss-docker-image", action="store_true", default=False,
        help="Keep the created dss docker image for inspection or reuse."
    )
    add_options_for_docker_image("notebook-test", "Notebook testing")
    add_options_for_docker_image("ai-lab-with-additional-group")
    parser.addoption(
        "--docker-registry", default=None, metavar="HOST:PORT",
        help="Docker registry for pushing Docker images to",
    )


@pytest.fixture(scope="session")
def docker_auth():
    username = os.environ.get(USER_ENV, None)
    password = os.environ.get(PASSWORD_ENV, None)
    if not (username and password):
        return None
    return {
        "username": username,
        "password": password,
    }


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


@pytest.fixture
def fake_docker_socket_on_host(tmp_path):
    socket = tmp_path / "socket.txt"
    socket.touch()
    os.chmod(socket, 0o660)
    return socket


@pytest.fixture
def accessible_file(fake_docker_socket_on_host):
    socket = fake_docker_socket_on_host
    mode = os.stat(socket).st_mode | stat.S_IRGRP | stat.S_IWGRP
    os.chmod(socket, mode)
    return socket


@pytest.fixture
def non_accessible_file(fake_docker_socket_on_host):
    socket = fake_docker_socket_on_host
    mode = stat.S_IRUSR | stat.S_IWUSR
    os.chmod(socket, mode)
    return socket
