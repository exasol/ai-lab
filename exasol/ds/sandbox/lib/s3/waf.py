from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.render_template import render_template

VM_BUCKET_WAF_STACK_NAME = "DATA-SCIENCE-SANDBOX-VM-Bucket-WAF"

LOG = get_status_logger(LogType.VM_BUCKET)

OUTPUT_KEY_VM_DOWNLOAD_ACL_ARN = "VMDownloadACLArn"


class Waf:
    def __init__(
            self,
            aws_access: Optional[AwsAccess],
            config: ConfigObject,
            stack_name: str,
            template: str,
            allowed_ip: str,
            download_acl_arn: str,
    ):
        self.aws = aws_access
        self.config = config
        self.stack_name = stack_name
        self.template = template
        self.allowed_ip = allowed_ip: str
        self.download_acl_arn = download_acl_arn

    @classmethod
    def vm_bucket(
            cls,
            aws_access: Optional[AwsAccess],
            config: ConfigObject,
    ) -> "Waf":
        return S3Bucket(
            aws_access,
            config,
            VM_BUCKET_WAF_STACK_NAME,
            "waf_cloudformation.jinja.yaml",
            OUTPUT_KEY_VM_DOWNLOAD_ACL_ARN,
            allowed_ip="",
        )

    @property
    def cloudformation_template(self) -> str:
        return render_template(
            self.template,
            allowed_ip=self.allowed_ip,
            VMDownloadACLArn=self.download_acl_arn,
        )

    @property
    def _region_aws(self) -> AwsAccess:
        return self.aws.instantiate_for_region(region=self.config.waf_region)

    # run_setup_vm_bucket_waf
    def setup(self) -> None:
        """
        Deploys the WAF Cloudformation stack.  It automatically deploys to
        AWS region indicated by configuration parameter "waf_region".
        """
        yml = self.cloudformation_template
        self._region_aws.upload_cloudformation_stack(yml, self.stack_name)
        LOG.info(f"Deployed cloudformation stack '{self.stack_name}' in region '{self.config.waf_region}'")

    # _find_vm_bucket_stack_output
    def _stack_output(output_key: str):
        stack = [stack for stack in self._region_aws.describe_stacks() if stack.name == self.stack_name]
        if len(stack) != 1:
            raise RuntimeError(f"stack {self.stack_name} not found")
        output = [output for output in stack[0].outputs if output.output_key == output_key]
        if len(output) != 1:
            raise RuntimeError(f"Output key '{output_key}' in output for stack {self.stack_name} not found")
        return output[0].output_value

    # find_acl_arn
    @property
    def acl_arn(self) -> str:
        """
        Finds the Arn of the WAF Acl which should be used for the
        Cloudfront distribution of the VM Bucket.  Assumes, that the WAF
        Cloudformation stack is correctly deployed.
        """
        # _find_vm_bucket_stack_output(
        return self._stack_output(self.download_acl_arn)
