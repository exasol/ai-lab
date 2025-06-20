from copy import copy

import pytest

from exasol.ds.sandbox.lib.config import default_config_object

pytest_plugins = (
    "test.docker.dss_docker_image",
    "test.aws.fixtures",
)


@pytest.fixture
def jupyter_port():
    return 49494


@pytest.fixture(scope="session")
def test_config():
    test_config = copy(default_config_object)
    test_config.time_to_wait_for_polling = 0.1
    return test_config
