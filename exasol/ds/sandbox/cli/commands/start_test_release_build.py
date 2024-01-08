from typing import Optional

import click

from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.aws_options import aws_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib.github_release_access import (
    github_token_or_exit,
    GithubReleaseAccess,
)
from exasol.ds.sandbox.lib.release_build.run_release_build import run_start_test_release_build




@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@click.option('--branch', type=str, required=True,
              help="""The branch for which the test release should be created.""")
@click.option('--release-title', type=str, required=True,
              help="""The title of the Github draft release which will be created.""")
def start_test_release_build(
        aws_profile: Optional[str],
        log_level: str,
        branch: str,
        release_title: str
):
    """
    This command triggers the AWS release Codebuild to generate a new
    sandbox test version. GitHub token is expected to be found in environment
    variable GITHUB_TOKEN.
    """
    set_log_level(log_level)
    gh_token = github_token_or_exit()
    run_start_test_release_build(
        AwsAccess(aws_profile),
        GithubReleaseAccess(gh_token),
        branch,
        release_title,
        gh_token,
    )

