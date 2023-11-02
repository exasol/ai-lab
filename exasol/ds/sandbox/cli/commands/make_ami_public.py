from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.aws_options import aws_options
from exasol.ds.sandbox.cli.options.id_options import id_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.export_vm.run_make_ami_public import run_make_ami_public
from exasol.ds.sandbox.lib.logging import set_log_level


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
