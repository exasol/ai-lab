from enum import Enum
from typing import Optional

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.render_template import render_template
from exasol.ds.sandbox.lib.vm_bucket.vm_dss_bucket_waf import find_acl_arn
from exasol.ds.sandbox.lib.asset_id import AssetId


# TODO: rename to a more general term, e.g. S3_BUCKETS
LOG = get_status_logger(LogType.VM_BUCKET)

VM_BUCKET_STACK = "DATA-SCIENCE-SANDBOX-VM-Bucket"


# TODO: rename to a more general term, e.g. S3_BUCKETS
class OutputKey(Enum):
    VMBucketId = "VMBucketId"
    VMExportRoleId = "VMExportRoleId"
    CfDistributionId = "CfDistributionId"
    CfDistributionDomainName = "CfDistributionDomainName"


class S3Bucket:
    def __init__(self, aws_access: Optional[AwsAccess], stack_name: str, template: str):
        self.aws = aws_access
        self.stack_name = stack_name
        self.template = template
        # All output keys (class OutputKey) are parameters in the template.
        # Simply map the output key enums values to themselves and pass them
        # to jinja.  Thus, we ensure that the AWS output keys in the
        # cloudformation match with the values the dict.
        self._output_keys_dict = {k.value: k.value for k in OutputKey}

    @classmethod
    def vm(cls, aws_access: Optional[AwsAccess]) -> "S3Bucket":
        return S3Bucket(aws_access, VM_BUCKET_STACK, "vm_bucket_cloudformation.jinja.yaml")

    # create_vm_bucket_cf_template
    def cloudformation_template(self, waf_webacl_arn: str) -> str:
        return render_template(
            self.template, # "vm_bucket_cloudformation.jinja.yaml",
            acl_arn=waf_webacl_arn,
            path_in_bucket=AssetId.BUCKET_PREFIX,
            **self._output_keys_dict,
        )

    # _find_vm_bucket_stack_output
    def _stack_output(self, output_key: OutputKey):
        stack = [stack for stack in self.aws.describe_stacks() if stack.name == self.stack_name]
        if len(stack) != 1:
            raise RuntimeError(f"stack {self.stack_name} not found")
        output = [output for output in stack[0].outputs if output.output_key == output_key.value]
        if len(output) != 1:
            raise RuntimeError(f"Output key '{output_key}' in output for stack {self.stack_name} not found")
        return output[0].output_value

    # run_setup_vm_bucket
    def setup(self, config: ConfigObject) -> None:
        acl_arn = find_acl_arn(self.aws, config)
        yml = self.cloudformation_template(acl_arn)
        self.aws.upload_cloudformation_stack(yml, self.stack_name)
        LOG.info(f"Deployed cloudformation stack {self.stack_name}")

    # find_vm_bucket
    @property
    def id(self) -> str:
        return self._stack_output(OutputKey.VMBucketId)

    # find_url_for_bucket
    @property
    def url(self) -> str:
        return self._stack_output(OutputKey.CfDistributionDomainName)

    # find_vm_import_role
    @property
    def import_role(self) -> str:
        return self._stack_output(OutputKey.VMExportRoleId)
