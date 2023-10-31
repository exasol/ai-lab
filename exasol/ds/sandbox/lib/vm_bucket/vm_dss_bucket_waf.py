from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.render_template import render_template

STACK_NAME = "DATA-SCIENCE-SANDBOX-VM-Bucket-WAF"

LOG = get_status_logger(LogType.VM_BUCKET)

OUTPUT_KEY_VM_DOWNLOAD_ACL_ARN = "VMDownloadACLArn"


def get_cloudformation_template(allowed_ip: str) -> str:
    return render_template("waf_cloudformation.jinja.yaml", allowed_ip=allowed_ip,
                          VMDownloadACLArn=OUTPUT_KEY_VM_DOWNLOAD_ACL_ARN)


def run_setup_vm_bucket_waf(aws_access: AwsAccess, allowed_ip: str, config: ConfigObject) -> None:
    """
    Deploys the WAF Cloudformation stack.
    It automatically deploys to AWS region indicated by configuration parameter "waf_region".
    """

    yml = get_cloudformation_template(allowed_ip=allowed_ip)
    aws_access.instantiate_for_region(region=config.waf_region).upload_cloudformation_stack(yml, STACK_NAME)
    LOG.info(f"Deployed cloudformation stack '{STACK_NAME}' in region '{config.waf_region}'")


def _find_vm_bucket_stack_output(aws_access: AwsAccess, output_key: str):
    stack = [stack for stack in aws_access.describe_stacks() if stack.name == STACK_NAME]
    if len(stack) != 1:
        raise RuntimeError(f"stack {STACK_NAME} not found")
    output = [output for output in stack[0].outputs if output.output_key == output_key]
    if len(output) != 1:
        raise RuntimeError(f"Output key '{output_key}' in output for stack {STACK_NAME} not found")
    return output[0].output_value


def find_acl_arn(aws_access: AwsAccess, config: ConfigObject) -> str:
    """
    Finds the Arn of the WAF Acl which should be used for the Cloudfront distribution of the VM Bucket.
    Assumes, that the WAF Cloudformation stack is correctly deployed.
    """
    return _find_vm_bucket_stack_output(aws_access.instantiate_for_region(region=config.waf_region),
                                        OUTPUT_KEY_VM_DOWNLOAD_ACL_ARN)
