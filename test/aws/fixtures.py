import pytest

from exasol.ds.sandbox.lib.tags import DEFAULT_TAG_KEY
from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.vm_bucket.vm_dss_bucket import create_vm_bucket_cf_template
from exasol.ds.sandbox.lib.vm_bucket.vm_dss_bucket_waf import get_cloudformation_template
from exasol.ds.sandbox.lib.render_template import render_template
from test.aws.local_stack_access import AwsLocalStackAccess

TEST_DUMMY_AMI_ID = "ami-123"
DEFAULT_ASSET_ID = AssetId("test", stack_prefix="test-stack", ami_prefix="test-ami")
TEST_ACL_ARN = "TEST-DOWNLOAD-ACL"
TEST_IP = "1.1.1.1"


@pytest.fixture
def default_asset_id():
    return DEFAULT_ASSET_ID


@pytest.fixture()
def test_dummy_ami_id():
    return TEST_DUMMY_AMI_ID


def vm_bucket_template():
    return create_vm_bucket_cf_template(TEST_ACL_ARN)


@pytest.fixture
def vm_bucket_cloudformation_yml():
    return vm_bucket_template()


def ec2_template():
    return render_template(
        "ec2_cloudformation.jinja.yaml",
        key_name="test_key",
        user_name="test_user",
        trace_tag=DEFAULT_TAG_KEY,
        trace_tag_value=DEFAULT_ASSET_ID.tag_value,
        ami_id=TEST_DUMMY_AMI_ID,
    )


@pytest.fixture
def ec2_cloudformation_yml():
    return ec2_template()


def waf_template():
    return get_cloudformation_template(TEST_IP)


@pytest.fixture
def waf_cloudformation_yml():
    return waf_template()


def ci_codebuild_template():
    return render_template(
        "ci_code_build.jinja.yaml",
        vm_bucket="test-bucket-123",
    )


def release_codebuild_template():
    return render_template(
        "release_code_build.jinja.yaml",
        vm_bucket="test-bucket-123",
        path_in_bucket=AssetId.BUCKET_PREFIX,
        dockerhub_secret_arn="secret_arn",
    )


@pytest.fixture(scope="session")
def local_stack_aws_access(local_stack):
    return AwsLocalStackAccess().with_user("default_user")
