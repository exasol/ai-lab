from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.aws_options import aws_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.setup_ci_codebuild.ci_codebuild import run_setup_ci_codebuild
from exasol.ds.sandbox.lib.logging import set_log_level


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
def setup_ci_codebuild(
            aws_profile: str,
            log_level: str):
    """
    Command to deploy the CI CodeBuild stack
    """
    set_log_level(log_level)
    run_setup_ci_codebuild(AwsAccess(aws_profile))
