from typing import Optional

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.cloudformation_templates import (
    CfTemplateSpec,
    S3BucketWithWAFCfTemplate,
    WafCfTemplate,
)


class VmBucketCfTemplate(S3BucketWithWAFCfTemplate):
    """
    Enables to instantiate templates for cloudformation stacks for an S3
    bucket and the related Web Application Firewall (WAF) dedicated for AI-Lab
    virtual machine images (VM).
    """
    S3_BUCKET = CfTemplateSpec(
        cf_stack_name="DATA-SCIENCE-SANDBOX-VM-Bucket",
        template="cloudformation/vm-images/s3-bucket.jinja.yaml",
        outputs={
            "BucketId": "VMBucketId",
            "ExportRoleId": "VMExportRoleId",
            "CfDistributionId": "CfDistributionId",
            "CfDistributionDomainName": "CfDistributionDomainName",
        },
    )
    WAF = CfTemplateSpec(
        cf_stack_name="DATA-SCIENCE-SANDBOX-VM-Bucket-WAF",
        template="cloudformation/vm-images/waf.jinja.yaml",
        outputs={
            "DownloadACLArn": "VMDownloadACLArn",
        },
    )

    def __init__(self, aws_access: Optional[AwsAccess]):
        super().__init__(aws_access, self.S3_BUCKET, self.WAF)
