import logging

from exasol.ds.sandbox.lib.dss_docker import DssDockerImage


def test_for_production():
    testee = DssDockerImage.for_production()
    assert testee.container_name == DssDockerImage.DEFAULT_CONTAINER_NAME
    assert testee.image_name == DssDockerImage.DEFAULT_IMAGE_NAME
    assert testee.log_level == logging.INFO


def test_constructor():
    testee = DssDockerImage("cont", "img", logging.ERROR)
    assert testee.container_name == "cont"
    assert testee.image_name == "img"
    assert testee.log_level == logging.ERROR
