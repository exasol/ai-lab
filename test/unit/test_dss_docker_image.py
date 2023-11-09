import pytest

from exasol.ds.sandbox.lib.dss_docker.create_image import (
    DssDockerImage,
    DSS_VERSION,
)


@pytest.fixture
def sample_repo():
    return "avengers/tower"


def test_constructor_defaults(sample_repo):
    testee = DssDockerImage(sample_repo)
    assert testee.image_name == f"{sample_repo}:{DSS_VERSION}"
    assert testee.publish == False
    assert testee.keep_container == False


def test_constructor(sample_repo):
    version = "1.2.3"
    testee = DssDockerImage(
        repository=sample_repo,
        version=version,
        publish=True,
        keep_container=True,
    )
    assert testee.image_name == f"{sample_repo}:{version}"
    assert testee.publish == True
    assert testee.keep_container == True
