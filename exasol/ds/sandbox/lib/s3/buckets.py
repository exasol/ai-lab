from typing import Optional

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.cloudformation_template import CfStackSpec, CfTemplate


LOG = get_status_logger(LogType.S3_BUCKETS)

VM_BUCKET = CfStackSpec(
    cf_stack_name="DATA-SCIENCE-SANDBOX-VM-Bucket",
    template="vm_bucket_cloudformation.jinja.yaml",
    outputs={
        "BucketId": "VMBucketId",
        "ExportRoleId": "VMExportRoleId",
        "CfDistributionId": "CfDistributionId",
        "CfDistributionDomainName": "CfDistributionDomainName",
    },
)


class S3Bucket(CfTemplate):
    def __init__(self, aws_access: Optional[AwsAccess], spec: CfStackSpec):
        super().__init__(aws_access, spec)

    @classmethod
    def vm(cls, aws_access: Optional[AwsAccess]) -> "S3Bucket":
        return S3Bucket(aws_access, VM_BUCKET)

    def setup(self, waf_acl_arn: str) -> None:
        super().setup(
            acl_arn=waf_acl_arn,
            path_in_bucket=AssetId.BUCKET_PREFIX,
        )
        LOG.info(f"Deployed cloudformation stack {self.stack_name}")

    @property
    def id(self) -> str:
        return self.stack_output("BucketId")

    @property
    def url(self) -> str:
        return self.stack_output("CfDistributionDomainName")

    @property
    def import_role(self) -> str:
        return self.stack_output("ExportRoleId")
