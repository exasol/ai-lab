from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.logging import get_status_logger, LogType
from exasol_script_languages_developer_sandbox.lib.render_template import render_template
from exasol_script_languages_developer_sandbox.lib.vm_bucket.vm_slc_bucket import find_vm_bucket

RELEASE_CODE_BUILD_STACK_NAME = "DEVELOPER-SANDBOX-RELEASE-CODEBUILD"

LOG = get_status_logger(LogType.SETUP_RELEASE_BUILD)


def run_setup_release_codebuild(aws_access: AwsAccess) -> None:
    yml = render_template("release_code_build.jinja.yaml", vm_bucket=find_vm_bucket(aws_access))
    aws_access.upload_cloudformation_stack(yml, RELEASE_CODE_BUILD_STACK_NAME)
    LOG.info(f"Deployed cloudformation stack {RELEASE_CODE_BUILD_STACK_NAME}")

