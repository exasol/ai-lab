from typing import Optional

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.cloudformation_templates import (
    CfTemplateSpec,
    CfTemplate,
    WafCfTemplate,
)


LOG = get_status_logger(LogType.S3_BUCKETS)


class S3BucketCfTemplate(CfTemplate):
    """
    Template for a Cloudformation stack for an AWS S3 bucket.
    """
    def __init__(self, aws_access: Optional[AwsAccess], spec: CfTemplateSpec):
        super().__init__(aws_access, spec)

    def setup(self, config: ConfigObject) -> None:
        waf_acl_arn = self.waf(config).acl_arn
        super().setup(
            acl_arn=waf_acl_arn,
            path_in_bucket=AssetId.BUCKET_PREFIX,
        )
        LOG.info(f"Deployed cloudformation stack {self.stack_name}")

    def waf(self, spec: CfTemplateSpec, region: str) -> WafCfTemplate:
        return WafCfTemplate(self._aws, spec, region)

    @property
    def id(self) -> str:
        return self.stack_output("BucketId")

    @property
    def url(self) -> str:
        return self.stack_output("CfDistributionDomainName")

    @property
    def import_role(self) -> str:
        return self.stack_output("ExportRoleId")
