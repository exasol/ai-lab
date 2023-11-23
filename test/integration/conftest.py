
def pytest_addoption(parser):
    parser.addoption(
        "--dss-docker-image", default=None,
        help="Name and version of existing Docker image to use for tests",
    )


def pytest_generate_tests(metafunc):
    if "dss_docker_image_name" in metafunc.fixturenames:
        value = metafunc.config.getoption("--dss-docker-image")
        metafunc.parametrize("dss_docker_image_name", [value])
