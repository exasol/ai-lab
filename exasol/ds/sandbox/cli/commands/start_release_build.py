import click

from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.lib.config import default_config_object
from exasol.ds.sandbox.lib.dss_docker import DEFAULT_ORG_AND_REPOSITORY
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib.release_build.run_release_build import run_start_release_build


@cli.command()
@add_options(logging_options)
@click.option(
    "--publish/--no-publish",
    default=False,
    help="Publish the release Docker image after building it.",
)
@click.option(
    "--repository",
    type=str,
    default=DEFAULT_ORG_AND_REPOSITORY,
    show_default=True,
    help="Docker repository used for the release image.",
)
def start_release_build(
        log_level: str,
        publish: bool,
        repository: str):
    """
    Release command building the AI Lab release artifacts in the current
    environment.
    """
    set_log_level(log_level)
    run_start_release_build(default_config_object, publish=publish, repository=repository)
