import os
import pytest
import shlex
import subprocess

from copy import copy

from exasol.ds.sandbox.lib.config import default_config_object, ConfigObject
from exasol.ds.sandbox.lib.render_template import render_template
from importlib.metadata import version
from exasol.ds.sandbox.lib.tags import DEFAULT_TAG_KEY
from exasol.ds.sandbox.lib.asset_id import AssetId

pytest_plugins = (
    "test.docker.dss_docker_image",
    "aws.fixtures",
)


@pytest.fixture
def jupyter_port():
    return 49494


@pytest.fixture(scope="session")
def test_config():
    test_config = copy(default_config_object)
    test_config.time_to_wait_for_polling = 0.1
    return test_config
