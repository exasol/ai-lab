import logging

from exasol_script_languages_developer_sandbox.lib.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.render_template import render_template

STACK_NAME = "VM-SLC-Bucket"
BUCKET_NAME = "VMSLCBucket"


def run_setup_vm_bucket(aws_access: AwsAccess) -> None:
    yml = render_template("vm_bucket_cloudformation.jinja.yaml", bucket_name=BUCKET_NAME)
    aws_access.upload_cloudformation_stack(yml, STACK_NAME)
    logging.info(f"Deployed cloudformation stack {STACK_NAME}")


def find_vm_bucket(aws_access: AwsAccess) -> str:
    stack_resources = aws_access.get_all_stack_resources(STACK_NAME)
    for stack_resource in stack_resources:
        if stack_resource["ResourceType"] == "AWS::S3::Bucket" and \
           stack_resource["LogicalResourceId"] == BUCKET_NAME and \
           stack_resource["ResourceStatus"] == "CREATE_COMPLETE":
            return stack_resource["PhysicalResourceId"]
    raise RuntimeError("bucket not found")
