from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.render_template import render_template
from exasol.ds.sandbox.lib.tags import DEFAULT_TAG_KEY
from exasol.ds.sandbox.lib.s3.buckets import S3Bucket
from exasol.ds.sandbox.lib.s3.waf import Waf

DEFAULT_ASSET_ID = AssetId("test", stack_prefix="test-stack", ami_prefix="test-ami")
TEST_IP = "1.1.1.1"
TEST_ACL_ARN = "TEST-DOWNLOAD-ACL"
TEST_DUMMY_AMI_ID = "ami-123"


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


def ec2_template():
    return render_template(
        "ec2_cloudformation.jinja.yaml",
        key_name="test_key",
        user_name="test_user",
        trace_tag=DEFAULT_TAG_KEY,
        trace_tag_value=DEFAULT_ASSET_ID.tag_value,
        ami_id=TEST_DUMMY_AMI_ID,
    )


def vm_bucket_template():
    return S3Bucket.vm(aws_access=None).cloudformation_template(
        acl_arn=TEST_ACL_ARN,
        path_in_bucket=AssetId.BUCKET_PREFIX,
    )


def waf_template():
    return Waf.vm_bucket_for_linter().cloudformation_template(allowed_ip=TEST_IP)
