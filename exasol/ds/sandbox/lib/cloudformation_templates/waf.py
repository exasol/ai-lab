from typing import Optional
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.cloudformation_templates.cf_template import (
    CfTemplateSpec,
    CfTemplate,
)

LOG = get_status_logger(LogType.S3_BUCKETS)


class WafCfTemplate(CfTemplate):
    """
    Template for a Cloudformation stack for a Web Application Firewall (WAF).
    """
    def __init__(
            self,
            aws_access: Optional[AwsAccess],
            spec: CfTemplateSpec,
            region: Optional[str],
    ):
        aws = (
            aws_access.instantiate_for_region(region)
            if region and aws_access
            else aws_access
        )
        super().__init__(aws, spec)
        self.region = region

    def setup(self, allowed_ip: str) -> None:
        super().setup(allowed_ip=allowed_ip)
        LOG.info(f"Deployed cloudformation stack {self.stack_name}")

    @property
    def acl_arn(self) -> str:
        """
        Finds the Arn of the WAF Acl which should be used for the
        Cloudfront distribution of the VM Bucket.  Assumes, that the WAF
        Cloudformation stack is correctly deployed.
        """
        return self.stack_output("DownloadACLArn")
