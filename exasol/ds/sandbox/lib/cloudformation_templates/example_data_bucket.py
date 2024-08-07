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


class ExampleDataCfTemplate(S3BucketCfTemplate):
    """
    Enables to instantiate templates for cloudformation stacks for an S3
    bucket and the related Web Application Firewall (WAF) dedicated for AI-Lab
    example-data.
    """
    S3_BUCKET = CfTemplateSpec(
        cf_stack_name="Ai-Lab-Example-Data-Bucket",
        template="cloudformation/example-data/s3-bucket.jinja.yaml",
        outputs={
            "BucketId": "ExampleDataBucketId",
            "ExportRoleId": "n/a",
            "CfDistributionId": "CfDistributionId",
            "CfDistributionDomainName": "CfDistributionDomainName",
        },
    )
    WAF = CfTemplateSpec(
        cf_stack_name="AI-Lab-Example-Data-Bucket-WAF",
        template="cloudformation/example-data/waf.jinja.yaml",
        outputs={
            "DownloadACLArn": "AiLabExampleDataDownloadACLArn",
        },
    )

    def __init__(self, aws_access: Optional[AwsAccess]):
        super().__init__(aws_access, self.S3_BUCKET, self.WAF)
