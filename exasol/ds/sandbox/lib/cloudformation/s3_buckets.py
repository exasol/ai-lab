from typing import Optional

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.cloudformation_template import (
    CfTemplateSpec,
    CfTemplate,
)
from exasol.ds.sandbox.lib.cloudformation.waf import WafCfTemplate


LOG = get_status_logger(LogType.S3_BUCKETS)


class S3BucketCfTemplate(CfTemplate):
    """
    Template for a Cloudformation stack for an AWS S3 bucket.
    """
    def __init__(self, aws_access: Optional[AwsAccess], spec: CfTemplateSpec):
        super().__init__(aws_access, spec)

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


class VmBucket():
    """
    Enables to instantiate templates for cloudformation stacks for an S3
    bucket and the related Web Application Firewall (WAF) dedicated for AI-Lab
    virtual machine images (VM).
    """
    S3_BUCKET = CfTemplateSpec(
        cf_stack_name="DATA-SCIENCE-SANDBOX-VM-Bucket",
        template="vm_bucket_cloudformation.jinja.yaml",
        outputs={
            "BucketId": "VMBucketId",
            "ExportRoleId": "VMExportRoleId",
            "CfDistributionId": "CfDistributionId",
            "CfDistributionDomainName": "CfDistributionDomainName",
        },
    )

    WAF = CfTemplateSpec(
        cf_stack_name="DATA-SCIENCE-SANDBOX-VM-Bucket-WAF",
        template="waf_cloudformation.jinja.yaml",
        outputs={
            "DownloadACLArn": "VMDownloadACLArn",
        },
    )

    @classmethod
    def s3_bucket(cls, aws_access: Optional[AwsAccess]) -> S3BucketCfTemplate:
        return S3BucketCfTemplate(aws_access, cls.S3_BUCKET)

    @classmethod
    def waf(cls, aws_access: AwsAccess, config: ConfigObject) -> WafCfTemplate:
        return WafCfTemplate(aws_access, cls.WAF, config.waf_region)
