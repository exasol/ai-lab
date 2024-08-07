from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.render_template import render_template
from exasol.ds.sandbox.lib.cloudformation_templates import VmBucketCfTemplate
from exasol.ds.sandbox.lib.asset_id import AssetId

RELEASE_CODE_BUILD_STACK_NAME = "DATA-SCIENCE-SANDBOX-RELEASE-CODEBUILD"

LOG = get_status_logger(LogType.SETUP_RELEASE_BUILD)


def run_setup_release_codebuild(aws_access: AwsAccess) -> None:
    secret_arn = aws_access.read_dockerhub_secret_arn()
    vm_s3_bucket = VmBucketCfTemplate(aws_access)
    yml = render_template(
        "release_code_build.jinja.yaml",
        vm_bucket=vm_s3_bucket.id,
        path_in_bucket=AssetId.BUCKET_PREFIX,
        dockerhub_secret_arn=secret_arn,
    )
    aws_access.upload_cloudformation_stack(yml, RELEASE_CODE_BUILD_STACK_NAME)
    LOG.info(f"Deployed cloudformation stack {RELEASE_CODE_BUILD_STACK_NAME}")

