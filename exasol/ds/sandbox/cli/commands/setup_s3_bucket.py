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
    '--purpose', required=True,
    type=click.Choice(['vm', 'example-data-http'], case_sensitive=False),
    help="""Purpose of the S3 bucket: vm = AI-Lab virtual machine images,
    example-data-http = AI-Lab example data accessed via HTTP.""")
def setup_s3_bucket(aws_profile: str, log_level: str, purpose: str):
    """
    Command to deploy one of the AI-Lab S3-Buckets for the specified
    PURPOSE:\n
    * vm: S3 bucket for virtual machine images\n
    * example-data-http: S3 bucket for Example-Data to be accessed via HTTP
    """
    set_log_level(log_level)
    aws = AwsAccess(aws_profile)
    config = default_config_object
    if purpose == "vm":
        VmBucketCfTemplate(aws).setup(config)
    elif purpose == "example-data-http":
        ExampleDataCfTemplate(aws).setup(config)
