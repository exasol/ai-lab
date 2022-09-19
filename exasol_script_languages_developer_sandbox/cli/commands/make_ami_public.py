from exasol_script_languages_developer_sandbox.cli.cli import cli
from exasol_script_languages_developer_sandbox.cli.common import add_options
from exasol_script_languages_developer_sandbox.cli.options.aws_options import aws_options
from exasol_script_languages_developer_sandbox.cli.options.id_options import id_options
from exasol_script_languages_developer_sandbox.cli.options.logging import logging_options
from exasol_script_languages_developer_sandbox.lib.asset_id import AssetId
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.export_vm.run_make_ami_public import run_make_ami_public
from exasol_script_languages_developer_sandbox.lib.logging import set_log_level


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@add_options(id_options)
def make_ami_public(
            aws_profile: str,
            asset_id: str,
            log_level: str):
    """
    Debug command which makes an existing AMI public.
    """
    set_log_level(log_level)
    run_make_ami_public(AwsAccess(aws_profile), AssetId(asset_id))
