import click

from exasol_script_languages_developer_sandbox.cli.cli import cli
from exasol_script_languages_developer_sandbox.cli.common import add_options
from exasol_script_languages_developer_sandbox.cli.options.aws_options import aws_options
from exasol_script_languages_developer_sandbox.cli.options.logging import logging_options
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.config import default_config_object
from exasol_script_languages_developer_sandbox.lib.logging import set_log_level
from exasol_script_languages_developer_sandbox.lib.vm_bucket.vm_slc_bucket_waf import run_setup_vm_bucket_waf


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@click.option('--allowed-ip', type=str,
              help="The allowed IP address for which CAPTCHA will not be applied.")
def setup_vm_bucket_waf(
            aws_profile: str,
            allowed_ip: str,
            log_level: str):
    """
    Command to deploy the VM S3-Bucket Web Application Firewall. Needs to run before deploying the VM Bucket itself.
    """
    set_log_level(log_level)
    run_setup_vm_bucket_waf(AwsAccess(aws_profile), allowed_ip, default_config_object)
