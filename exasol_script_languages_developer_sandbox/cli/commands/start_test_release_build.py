import os
from typing import Optional

import click

from exasol_script_languages_developer_sandbox.cli.cli import cli
from exasol_script_languages_developer_sandbox.cli.common import add_options
from exasol_script_languages_developer_sandbox.cli.options.aws_options import aws_options
from exasol_script_languages_developer_sandbox.cli.options.logging import logging_options
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.logging import set_log_level
from exasol_script_languages_developer_sandbox.lib.github_release_access import GithubReleaseAccess
from exasol_script_languages_developer_sandbox.lib.release_build.run_release_build import run_start_test_release_build


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
    This command  triggers the AWS release Codebuild to generate a new developer sandbox test version.
    """
    set_log_level(log_level)
    gh_token = os.getenv("GITHUB_TOKEN")
    run_start_test_release_build(AwsAccess(aws_profile), GithubReleaseAccess(gh_token),
                                 branch, release_title, gh_token)
