from typing import Optional

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.cloudformation_templates import (
    CfTemplate,
    CfTemplateSpec,
    S3BucketCfTemplate,
)
from exasol.ds.sandbox.lib.config import ConfigObject


class ExampleDataCfTemplate(S3BucketCfTemplate):
    """
    Enables to instantiate templates for cloudformation stacks for an S3
    bucket and the related Web Application Firewall (WAF) dedicated for AI-Lab
    example-data-http.
    """
    S3_BUCKET = CfTemplateSpec(
        cf_stack_name="Ai-Lab-Example-Data-Bucket",
        template="cloudformation/example-data-http/s3-bucket.jinja.yaml",
        outputs={
            "BucketId": "ExampleDataBucketId",
            "ExportRoleId": "n/a",
            "CfDistributionId": "CfDistributionId",
            "CfDistributionDomainName": "CfDistributionDomainName",
        },
    )
    WAF = CfTemplateSpec(
        cf_stack_name="AI-Lab-Example-Data-Bucket-WAF",
        template="cloudformation/example-data-http/waf.jinja.yaml",
        outputs={
            "DownloadACLArn": "AiLabExampleDataDownloadACLArn",
        },
    )

    def __init__(self, aws_access: Optional[AwsAccess]):
        super().__init__(aws_access, self.S3_BUCKET, self.WAF)


class ExampleDataS3CfTemplate(S3BucketCfTemplate):
    """
    Enables to instantiate templates for cloudformation stacks for an S3
    bucket and the related Web Application Firewall (WAF) dedicated for AI-Lab
    example-data-s3.
    """
    S3_BUCKET = CfTemplateSpec(
        cf_stack_name="Ai-Lab-Example-Data-Bucket-S3",
        template="cloudformation/example-data-s3/s3-bucket.jinja.yaml",
        outputs={
            "BucketId": "ExampleDataBucketId",
            "ExportRoleId": "n/a",
            "CfDistributionId": "CfDistributionId",
            "CfDistributionDomainName": "CfDistributionDomainName",
        },
    )
    WAF = CfTemplateSpec(
        cf_stack_name="AI-Lab-Example-Data-Bucket-S3-WAF",
        template="cloudformation/example-data-s3/waf.jinja.yaml",
        outputs={},
    )

    def __init__(self, aws_access: Optional[AwsAccess]):
        super().__init__(aws_access, self.S3_BUCKET, self.WAF)

    def setup(self, config: ConfigObject) -> None:
        CfTemplate.setup(self)
