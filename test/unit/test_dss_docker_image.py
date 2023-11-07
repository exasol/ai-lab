import logging
import pytest

from exasol.ds.sandbox.lib.dss_docker.create_image import (
    DssDockerImage,
    CONTAINER_NAME as DOCKER_CONTAINER_NAME,
    DSS_VERSION,
)


@pytest.fixture
def sample_repo():
    return "avengers/tower"


def test_constructor_defaults(sample_repo):
    testee = DssDockerImage(sample_repo)
    assert testee.container_name == DOCKER_CONTAINER_NAME
    assert testee.image_name == f"{sample_repo}:{DSS_VERSION}"
    assert testee.publish == False
    assert testee.log_level == logging.INFO


def test_constructor(sample_repo):
    version = "1.2.3"
    testee = DssDockerImage(sample_repo, version, True, logging.ERROR)
    assert testee.image_name == f"{sample_repo}:{version}"
    assert testee.publish == True
    assert testee.log_level == logging.ERROR
