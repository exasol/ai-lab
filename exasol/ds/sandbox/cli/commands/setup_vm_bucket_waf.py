import click

from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.aws_options import aws_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import default_config_object
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib.s3.waf import Waf


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@click.option('--allowed-ip', type=str,
              help="The allowed IP address for which CAPTCHA will not be applied.")
def setup_vm_bucket_waf(aws_profile: str, allowed_ip: str, log_level: str):
    """
    Command to deploy the VM S3-Bucket Web Application Firewall. Needs to run before deploying the VM Bucket itself.
    """
    set_log_level(log_level)
    Waf.vm_bucket(AwsAccess(aws_profile), default_config_object).setup(allowed_ip)
