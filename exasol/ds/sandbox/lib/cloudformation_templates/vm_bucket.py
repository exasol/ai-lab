from typing import Optional

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.cloudformation_templates import (
    CfTemplateSpec,
    S3BucketCfTemplate,
    WafCfTemplate,
)


class VmBucketCfTemplate(S3BucketCfTemplate):
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

    def __init__(self, aws_access: Optional[AwsAccess]):
        super().__init__(aws_access, self.S3_BUCKET)

    def waf(self, config: ConfigObject) -> WafCfTemplate:
        return super().waf(self.WAF, config.waf_region)
