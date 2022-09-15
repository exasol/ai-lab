import os
from typing import Optional

import click

from exasol_script_languages_developer_sandbox.cli.cli import cli
from exasol_script_languages_developer_sandbox.cli.common import add_options
from exasol_script_languages_developer_sandbox.cli.options.aws_options import aws_options
from exasol_script_languages_developer_sandbox.cli.options.logging import logging_options
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.config import default_config
from exasol_script_languages_developer_sandbox.lib.logging import set_log_level
from exasol_script_languages_developer_sandbox.lib.release_build.run_release_build import run_start_release_build


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@click.option('--upload-url', type=str, required=False,
              help="""The URL of the Github release where artifacts will be stored.""")
@click.option('--branch', type=str, required=True,
              help="""The branch of the repository which will be used.""")
def start_release_build(
        aws_profile: Optional[str],
        log_level: str,
        upload_url: str,
        branch: str):
    """
    This command  triggers the AWS release Codebuild to generate a new developer sandbox version.
    """
    set_log_level(log_level)
    run_start_release_build(AwsAccess(aws_profile), default_config, upload_url, branch, os.getenv("GITHUB_TOKEN"))
