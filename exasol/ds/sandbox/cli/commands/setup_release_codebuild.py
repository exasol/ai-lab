from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.aws_options import aws_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib.setup_release_codebuild.release_codebuild import \
    run_setup_release_codebuild


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
def setup_release_codebuild(
            aws_profile: str,
            log_level: str):
    """
    Command to deploy the Release CodeBuild stack
    """
    set_log_level(log_level)
    run_setup_release_codebuild(AwsAccess(aws_profile))
