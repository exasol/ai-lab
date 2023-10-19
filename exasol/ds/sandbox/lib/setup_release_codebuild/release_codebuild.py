from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.render_template import render_template
from exasol.ds.sandbox.lib.vm_bucket.vm_dss_bucket import find_vm_bucket

RELEASE_CODE_BUILD_STACK_NAME = "DATA-SCIENCE-SANDBOX-RELEASE-CODEBUILD"

LOG = get_status_logger(LogType.SETUP_RELEASE_BUILD)


def run_setup_release_codebuild(aws_access: AwsAccess) -> None:
    yml = render_template("release_code_build.jinja.yaml", vm_bucket=find_vm_bucket(aws_access))
    aws_access.upload_cloudformation_stack(yml, RELEASE_CODE_BUILD_STACK_NAME)
    LOG.info(f"Deployed cloudformation stack {RELEASE_CODE_BUILD_STACK_NAME}")

