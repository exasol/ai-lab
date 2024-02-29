import os
import pytest
import subprocess
import shlex

from importlib.metadata import version

@pytest.fixture(scope="session")
def local_stack():
    """
    This fixture starts/stops localstack as a context manager.
    """
    command = "localstack start -d"

    image_version = version('localstack')
    # See https://github.com/localstack/localstack/issues/8254
    # and https://github.com/localstack/localstack/issues/9939
    #
    # Until an official release of localstack Docker image with a concrete
    # version is available incl. a fix for issue 9939 we only can use version
    # "latest".
    #
    # See https://github.com/exasol/ai-lab/issues/200 for replacing this with
    # a concrete version in order to make CI tests more robust.
    image_version = "3.2.0"
    image_name = {"IMAGE_NAME": f"localstack/localstack:{image_version}"}
    env_variables = {**os.environ, **image_name}

    process = subprocess.run(shlex.split(command), env=env_variables)
    assert process.returncode == 0

    command = "localstack wait -t 30"

    process = subprocess.run(shlex.split(command), env=env_variables)
    assert process.returncode == 0
    yield None

    command = "localstack stop"
    subprocess.run(shlex.split(command), env=env_variables)
