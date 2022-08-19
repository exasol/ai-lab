from exasol_script_languages_developer_sandbox.cli.cli import cli
from exasol_script_languages_developer_sandbox.cli.common import add_options
from exasol_script_languages_developer_sandbox.cli.options.aws_options import aws_options
from exasol_script_languages_developer_sandbox.cli.options.logging import logging_options, set_log_level
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.vm_bucket.vm_slc_bucket import run_setup_vm_bucket


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
def setup_vm_bucket(
            aws_profile: str,
            log_level: str):
    """
    Command to deploy the VM S3-Bucket
    """
    set_log_level(log_level)
    run_setup_vm_bucket(AwsAccess(aws_profile))
