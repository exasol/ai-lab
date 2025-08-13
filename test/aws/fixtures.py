import pytest

from test.aws.templates import (
    ec2_template,
    DEFAULT_ASSET_ID,
    TEST_DUMMY_AMI_ID,
)

@pytest.fixture
def default_asset_id():
    return DEFAULT_ASSET_ID


@pytest.fixture()
def test_dummy_ami_id():
    return TEST_DUMMY_AMI_ID


@pytest.fixture()
def test_ec2_instance_type():
    return "t2.medium"


@pytest.fixture
def ec2_cloudformation_yml():
    return ec2_template()
