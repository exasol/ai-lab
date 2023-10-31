from typing import Tuple, Optional

import click

from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.aws_options import aws_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.asset_printing.print_assets import all_asset_types, print_assets
from exasol.ds.sandbox.lib.logging import set_log_level


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@click.option('--asset-id', type=str, default=None,
              help="The asset-id used to create the AWS resources during the other commands. "
                   "If not set, all resources will be printed. "
                   "The value might contain wildcards.")
@click.option('--asset-type', default=all_asset_types(),
              type=click.Choice(list(all_asset_types())), multiple=True,
              help="The asset types to print. Can be declared multiple times.")
@click.option('--out-file', default=None, type=click.Path(exists=False, file_okay=True, dir_okay=False),
              help="If given, writes the AWS assets to this file in markdown format.")
def show_aws_assets(
            aws_profile: str,
            asset_id: Optional[str],
            asset_type: Tuple[str, ...],
            out_file: Optional[str],
            log_level: str):
    """
    Shows all AWS assets.
    """
    set_log_level(log_level)
    _asset_id = AssetId(asset_id) if asset_id is not None else None
    print_assets(AwsAccess(aws_profile=aws_profile), asset_id=_asset_id,
                 outfile=out_file, asset_types=asset_type)
