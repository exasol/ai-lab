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
from test.aws.local_stack_access import AwsLocalStackAccess

# DEFAULT_ASSET_ID = AssetId("test", stack_prefix="test-stack", ami_prefix="test-ami")
# 
# TEST_DUMMY_AMI_ID = "ami-123"

pytest_plugins = (
    "test.docker.dss_docker_image",
)


# @pytest.fixture
# def default_asset_id():
#     return DEFAULT_ASSET_ID


@pytest.fixture
def jupyter_port():
    return 49494


# @pytest.fixture
# def ec2_cloudformation_yml():
#     return render_template(
#         "ec2_cloudformation.jinja.yaml",
#         key_name="test_key",
#         user_name="test_user",
#         trace_tag=DEFAULT_TAG_KEY,
#         trace_tag_value=DEFAULT_ASSET_ID.tag_value,
#         ami_id=TEST_DUMMY_AMI_ID,
#     )


@pytest.fixture(scope="session")
def test_config():
    test_config = copy(default_config_object)
    test_config.time_to_wait_for_polling = 0.1
    return test_config
