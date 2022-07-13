import os
import shlex
import subprocess

import pytest

from exasol_script_languages_developer_sandbox.lib.render_template import render_template
from importlib.metadata import version


@pytest.fixture
def ec2_cloudformation_yml():
    return render_template("ec2_cloudformation.jinja.yaml", key_name="test_key", user_name="test_user")


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
