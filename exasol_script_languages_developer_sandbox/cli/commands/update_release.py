import os
from typing import Optional

import click

from exasol_script_languages_developer_sandbox.cli.cli import cli
from exasol_script_languages_developer_sandbox.cli.common import add_options
from exasol_script_languages_developer_sandbox.cli.options.aws_options import aws_options
from exasol_script_languages_developer_sandbox.cli.options.id_options import id_options
from exasol_script_languages_developer_sandbox.cli.options.logging import logging_options
from exasol_script_languages_developer_sandbox.lib.asset_id import AssetId
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.logging import set_log_level
from exasol_script_languages_developer_sandbox.lib.github_release_access import GithubReleaseAccess
from exasol_script_languages_developer_sandbox.lib.update_release.run_update_release import run_update_release


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@click.option('--release-id', type=int, required=True,
              help="""The Github release id which will be updated.""")
@add_options(id_options)
def update_release(
        aws_profile: Optional[str],
        release_id: int,
        asset_id: str,
        log_level: str):
    """
    This command attaches the links of the release assets (AMI, VM images) to the Github release,
    indicated by parameter 'release-id'.
    """
    set_log_level(log_level)
    run_update_release(AwsAccess(aws_profile), GithubReleaseAccess(os.getenv("GITHUB_TOKEN")),
                       release_id, AssetId(asset_id))
