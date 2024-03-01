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
