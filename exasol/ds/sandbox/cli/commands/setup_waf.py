import click

from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.aws_options import aws_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import default_config_object
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib.cloudformation_templates import (
    VmBucketCfTemplate,
    ExampleDataCfTemplate,
)


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@click.option(
    '--allowed-ip', type=str,
    help="The allowed IP address for which CAPTCHA will not be applied.")
@click.option(
    '--purpose', required=True,
    type=click.Choice(['vm', 'example-data-http'], case_sensitive=False, ),
    help="""Purpose of the S3 bucket behind the WAF: vm = AI-Lab virtual
    machine images, example-data-http = AI-Lab example data.""")
def setup_waf(aws_profile: str, allowed_ip: str, log_level: str, purpose: str):
    """
    Deployment command for one of the AI-Lab Web Application Firewalls (WAFs)
    for S3 buckets. Needs to run before deploying the S3 bucket itself.
    PURPOSE:\n
    * vm: WAF for S3 bucket for virtual machine images\n
    * example-data-http: WAF for S3 bucket for Example-Data
    """
    set_log_level(log_level)
    aws = AwsAccess(aws_profile)
    config = default_config_object
    if purpose == "vm":
        VmBucketCfTemplate(aws).waf(config).setup(allowed_ip)
    elif purpose == "example-data-http":
        ExampleDataCfTemplate(aws).waf(config).setup()
