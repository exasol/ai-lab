import click

from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.lib.dss_docker import DssDockerImage
from exasol.ds.sandbox.lib.logging import SUPPORTED_LOG_LEVELS
from exasol.ds.sandbox.lib.logging import set_log_level


@cli.command()
@add_options([
    click.option(
        '--repository', type=str, metavar="ORG/REPO", show_default=True,
        default="exasol/data-science-sandbox",
        help="Organization and repository on hub.docker.com to publish the docker image to"),
    click.option('--version', type=str, help="Docker image version tag"),
    click.option(
        '--publish', type=bool, is_flag=True,
        help="Whether to publish the created Docker image"),
    click.option(
        '--keep-container', type=bool, is_flag=True,
        help="""Keep the Docker Container running after creating the image.
        Otherwise stop and remove the container."""),
])
@add_options(logging_options)
def create_docker_image(
        repository: str,
        version: str,
        publish: bool,
        keep_container: bool,
        log_level: str,
):
    """
    Create a Docker image for data-science-sandbox and deploy
    it to a Docker repository.
    """
    set_log_level(log_level)
    DssDockerImage(
        repository=repository,
        version=version,
        publish=publish,
        keep_container=keep_container,
    ).create()
