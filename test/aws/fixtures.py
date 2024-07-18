import pytest

from exasol.ds.sandbox.lib.s3.waf import Waf

from test.aws.templates import (
    ec2_template,
    vm_bucket_template,
    waf_template,
    DEFAULT_ASSET_ID,
    TEST_DUMMY_AMI_ID,
)

@pytest.fixture
def default_asset_id():
    return DEFAULT_ASSET_ID


@pytest.fixture()
def test_dummy_ami_id():
    return TEST_DUMMY_AMI_ID


@pytest.fixture
def vm_bucket_cloudformation_yml():
    return vm_bucket_template()


@pytest.fixture
def ec2_cloudformation_yml():
    return ec2_template()


@pytest.fixture
def waf_cloudformation_yml():
    return Waf.vm_bucket(aws_access=None, config=None).cloudformation_template
