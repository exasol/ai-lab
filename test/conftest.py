import os
import shlex
import subprocess

import pytest

from exasol_script_languages_developer_sandbox.lib import config
from exasol_script_languages_developer_sandbox.lib.config import ConfigObject
from exasol_script_languages_developer_sandbox.lib.render_template import render_template
from importlib.metadata import version

from exasol_script_languages_developer_sandbox.lib.tags import DEFAULT_TAG_KEY
from exasol_script_languages_developer_sandbox.lib.vm_bucket.vm_slc_bucket import BUCKET_NAME, ROLE_NAME

from exasol_script_languages_developer_sandbox.lib.asset_id import AssetId

DEFAULT_ASSET_ID = AssetId("test")


@pytest.fixture
def default_asset_id():
    return DEFAULT_ASSET_ID


@pytest.fixture
def ec2_cloudformation_yml():

    return render_template("ec2_cloudformation.jinja.yaml", key_name="test_key", user_name="test_user",
                           trace_tag=DEFAULT_TAG_KEY, trace_tag_value=DEFAULT_ASSET_ID.tag_value,
                           ami_id=config.global_config.source_ami_id)


@pytest.fixture
def vm_bucket_cloudformation_yml():
    return render_template("vm_bucket_cloudformation.jinja.yaml", bucket_name=BUCKET_NAME, role_name=ROLE_NAME)


@pytest.fixture(scope="session")
def local_stack():
    """
    This fixture starts/stops localstack as a context manager.
    """
    command = "localstack start -d"

    # We set the specific version for the docker image for localstack to use ("IMAGE_NAME"),
    # otherwise localstack uses tag "latest" which might break the CI tests.
    image_name = {"IMAGE_NAME": f"localstack/localstack:{version('localstack')}"}
    env_variables = {**os.environ, **image_name}

    process = subprocess.run(shlex.split(command), env=env_variables)
    assert process.returncode == 0

    command = "localstack wait -t 30"

    process = subprocess.run(shlex.split(command), env=env_variables)
    assert process.returncode == 0
    yield None

    command = "localstack stop"
    subprocess.run(shlex.split(command), env=env_variables)


@pytest.fixture(autouse=True)
def override_config():
    test_config = {
        "time_to_wait_for_polling": 0.01,
        "source_ami_id": config.global_config.source_ami_id
    }
    config.global_config = ConfigObject(**test_config)
