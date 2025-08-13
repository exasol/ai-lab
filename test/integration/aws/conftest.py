import os
import shlex
import subprocess
from importlib.metadata import version
from test.aws.local_stack_access import AwsLocalStackAccess

import pytest


@pytest.fixture(scope="session")
def local_stack(request):
    """
    This fixture starts/stops localstack as a context manager.
    """
    command = "localstack start -d"

    image_version = version('localstack')
    image_version = "3.2.0"
    image_name = {"IMAGE_NAME": f"localstack/localstack:{image_version}"}
    env_variables = {**os.environ, **image_name}
    if request.config.getoption(AwsLocalStackAccess.DOCKER_HOST_OPTION):
        env_variables["GATEWAY_LISTEN"] = f"0.0.0.0:{AwsLocalStackAccess.PORT}"
    process = subprocess.run(shlex.split(command), env=env_variables)
    assert process.returncode == 0

    command = "localstack wait -t 30"
    process = subprocess.run(shlex.split(command), env=env_variables)
    assert process.returncode == 0
    yield None

    command = "localstack stop"
    subprocess.run(shlex.split(command), env=env_variables)


@pytest.fixture(scope="session")
def local_stack_aws_access(local_stack, request):
    docker_host = request.config.getoption(AwsLocalStackAccess.DOCKER_HOST_OPTION)
    params = {"docker_host": docker_host} if docker_host else {}
    return AwsLocalStackAccess(**params).with_user("default_user")
