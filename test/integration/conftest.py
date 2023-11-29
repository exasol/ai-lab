
def pytest_addoption(parser):
    parser.addoption(
        "--dss-docker-image", default=None,
        help="Name and version of existing Docker image to use for tests",
    )
