from enum import Enum
from typing import Optional

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.render_template import render_template
from exasol.ds.sandbox.lib.asset_id import AssetId

VM_BUCKET_STACK = "DATA-SCIENCE-SANDBOX-VM-Bucket"

LOG = get_status_logger(LogType.S3_BUCKETS)


# TODO: rename entries to more general terms, e.g. BucketId, ExportRoleId
class OutputKey(Enum):
    VMBucketId = "VMBucketId"
    VMExportRoleId = "VMExportRoleId"
    CfDistributionId = "CfDistributionId"
    CfDistributionDomainName = "CfDistributionDomainName"


class S3Bucket:
    def __init__(
            self,
            aws_access: Optional[AwsAccess],
            stack_name: str,
            template: str,
    ):
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
        return S3Bucket(
            aws_access,
            VM_BUCKET_STACK,
            "vm_bucket_cloudformation.jinja.yaml",
        )

    def cloudformation_template(self, waf_acl_arn: str) -> str:
        return render_template(
            self.template,
            acl_arn=waf_acl_arn,
            path_in_bucket=AssetId.BUCKET_PREFIX,
            **self._output_keys_dict,
        )

    def _stack_output(self, output_key: OutputKey):
        stack = [stack for stack in self.aws.describe_stacks() if stack.name == self.stack_name]
        if len(stack) != 1:
            raise RuntimeError(f"stack {self.stack_name} not found")
        output = [output for output in stack[0].outputs if output.output_key == output_key.value]
        if len(output) != 1:
            raise RuntimeError(f"Output key '{output_key}' in output for stack {self.stack_name} not found")
        return output[0].output_value

    def setup(self, waf_acl_arn: str) -> None:
        self.aws.upload_cloudformation_stack(self.cloudformation_template(waf_acl_arn), self.stack_name)
        LOG.info(f"Deployed cloudformation stack {self.stack_name}")

    @property
    def id(self) -> str:
        return self._stack_output(OutputKey.VMBucketId)

    @property
    def url(self) -> str:
        return self._stack_output(OutputKey.CfDistributionDomainName)

    @property
    def import_role(self) -> str:
        return self._stack_output(OutputKey.VMExportRoleId)
