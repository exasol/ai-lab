from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.config import ConfigObject
from exasol_script_languages_developer_sandbox.lib.logging import get_status_logger, LogType
from exasol_script_languages_developer_sandbox.lib.render_template import render_template
from enum import Enum

from exasol_script_languages_developer_sandbox.lib.vm_bucket.vm_slc_bucket_waf import find_acl_arn

STACK_NAME = "DATA-SCIENCE-SANDBOX-VM-SLC-Bucket"


class OutputKey(Enum):
    VMBucketId = "VMBucketId"
    VMExportRoleId = "VMExportRoleId"
    CfDistributionId = "CfDistributionId"
    CfDistributionDomainName = "CfDistributionDomainName"


LOG = get_status_logger(LogType.VM_BUCKET)


def create_vm_bucket_cf_template(waf_webacl_arn: str) -> str:
    # All output keys (class OutputKey) are parameters in the vm_bucket_cloudformation.jinja.yaml
    # Simply map the output key enums values to them self and pass them to jinja.
    # Thus, we ensure that the output keys in the cloudformation match with the values in class OutputKey
    output_keys_dict = {output_key.value: output_key.value for output_key in OutputKey}
    return render_template("vm_bucket_cloudformation.jinja.yaml", acl_arn=waf_webacl_arn, **output_keys_dict)


def _find_vm_bucket_stack_output(aws_access: AwsAccess, output_key: OutputKey):
    stack = [stack for stack in aws_access.describe_stacks() if stack.name == STACK_NAME]
    if len(stack) != 1:
        raise RuntimeError(f"stack {STACK_NAME} not found")
    output = [output for output in stack[0].outputs if output.output_key == output_key.value]
    if len(output) != 1:
        raise RuntimeError(f"Output key '{output_key.value}' in output for stack {STACK_NAME} not found")
    return output[0].output_value


def run_setup_vm_bucket(aws_access: AwsAccess, config: ConfigObject) -> None:
    acl_arn = find_acl_arn(aws_access, config)
    yml = create_vm_bucket_cf_template(acl_arn)
    aws_access.upload_cloudformation_stack(yml, STACK_NAME)
    LOG.info(f"Deployed cloudformation stack {STACK_NAME}")


def find_vm_bucket(aws_access: AwsAccess) -> str:
    return _find_vm_bucket_stack_output(aws_access, OutputKey.VMBucketId)


def find_url_for_bucket(aws_access: AwsAccess) -> str:
    return _find_vm_bucket_stack_output(aws_access, OutputKey.CfDistributionDomainName)


def find_vm_import_role(aws_access: AwsAccess) -> str:
    return _find_vm_bucket_stack_output(aws_access, OutputKey.VMExportRoleId)
