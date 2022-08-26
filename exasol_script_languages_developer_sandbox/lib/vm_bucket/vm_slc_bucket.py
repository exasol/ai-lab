from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.logging import get_status_logger, LogType
from exasol_script_languages_developer_sandbox.lib.render_template import render_template

STACK_NAME = "VM-SLC-Bucket"
BUCKET_NAME = "VMSLCBucket"
ROLE_NAME = "VMImportRole"

LOG = get_status_logger(LogType.VM_BUCKET)


def run_setup_vm_bucket(aws_access: AwsAccess) -> None:
    yml = render_template("vm_bucket_cloudformation.jinja.yaml", bucket_name=BUCKET_NAME, role_name=ROLE_NAME)
    aws_access.upload_cloudformation_stack(yml, STACK_NAME)
    LOG.info(f"Deployed cloudformation stack {STACK_NAME}")


def find_vm_bucket(aws_access: AwsAccess) -> str:
    stack_resources = aws_access.get_all_stack_resources(STACK_NAME)
    for stack_resource in stack_resources:
        if stack_resource.is_s3_bucket and \
           stack_resource.logica_id == BUCKET_NAME and \
           stack_resource.is_complete:
            return stack_resource.physical_id
    raise RuntimeError("bucket not found")


def find_vm_import_role(aws_access: AwsAccess) -> str:
    stack_resources = aws_access.get_all_stack_resources(STACK_NAME)
    for stack_resource in stack_resources:
        if stack_resource.is_iam_role and \
           stack_resource.logica_id == ROLE_NAME and \
           stack_resource.is_complete:
            return stack_resource.physical_id
    raise RuntimeError("role not found")
