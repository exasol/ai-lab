from typing import Optional
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.aws_access.cloudformation_template import CfStackSpec, CfTemplate

LOG = get_status_logger(LogType.S3_BUCKETS)

VM_BUCKET_WAF = CfStackSpec(
    cf_stack_name="DATA-SCIENCE-SANDBOX-VM-Bucket-WAF",
    template="waf_cloudformation.jinja.yaml",
    outputs={
        "DownloadACLArn": "VMDownloadACLArn",
    },
)


class Waf(CfTemplate):
    def __init__(
            self,
            aws_access: Optional[AwsAccess],
            spec: CfStackSpec,
            region: Optional[str],
    ):
        super().__init__(aws_access, spec)
        self.region = region

    @staticmethod
    def vm_bucket(
            aws_access: AwsAccess,
            config: ConfigObject,
    ) -> "Waf":
        region = config.waf_region
        return Waf(
            aws_access.instantiate_for_region(region=region),
            VM_BUCKET_WAF,
            region,
        )

    @staticmethod
    def vm_bucket_for_linter():
        return Waf(None, VM_BUCKET_WAF, None)

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
