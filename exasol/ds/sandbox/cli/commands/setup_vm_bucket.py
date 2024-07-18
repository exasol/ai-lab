from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.aws_options import aws_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import default_config_object
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib.s3.buckets import S3Bucket
from exasol.ds.sandbox.lib.s3.waf import Waf


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
def setup_vm_bucket(aws_profile: str, log_level: str):
    """
    Command to deploy the VM S3-Bucket
    """
    set_log_level(log_level)
    aws = AwsAccess(aws_profile)
    waf_acl_arn = Waf.vm_bucket(aws, default_config_object).acl_arn
    S3Bucket.vm(aws).setup(waf_acl_arn)
