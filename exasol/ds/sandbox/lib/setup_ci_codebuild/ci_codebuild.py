from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.render_template import render_template
from exasol.ds.sandbox.lib.cloudformation_templates import VmBucketCfTemplate

STACK_NAME = "DATA-SCIENCE-SANDBOX-CI-TEST-CODEBUILD"

LOG = get_status_logger(LogType.SETUP_CI_CODEBUILD)


def run_setup_ci_codebuild(aws_access: AwsAccess) -> None:
    vm_bucket = VmBucketCfTemplate(aws_access).id
    yml = render_template("ci_code_build.jinja.yaml", vm_bucket=vm_bucket)
    aws_access.upload_cloudformation_stack(yml, STACK_NAME)
    LOG.info(f"Deployed cloudformation stack {STACK_NAME}")

