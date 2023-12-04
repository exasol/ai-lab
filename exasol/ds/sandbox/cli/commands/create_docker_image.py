import click

from exasol.ds.sandbox.cli.cli import cli, option_with_env_default
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.lib.dss_docker import DssDockerImage, DockerRegistry
from exasol.ds.sandbox.lib.logging import SUPPORTED_LOG_LEVELS
from exasol.ds.sandbox.lib.logging import set_log_level


@cli.command()
@add_options([
    click.option(
        '--repository', type=str, metavar="ORG/REPO", show_default=True,
        default="exasol/data-science-sandbox",
        help="Organization and repository on hub.docker.com to publish the docker image to"),
    click.option(
        '--version', type=str,  metavar="VERSION",
        help="Docker image version tag"),
    option_with_env_default("DOCKER_REGISTRY_USER",
        '--registry-user', type=str, metavar="USER",
        help="Username for publication to Docker registry"),
    option_with_env_default("DOCKER_REGISTRY_PASSWORD",
        '--registry-password', type=str, metavar="PASSWORD",
        help="Password for publication to Docker registry"),
    click.option(
        '--keep-container', type=bool, is_flag=True,
        help="""Keep the Docker Container running after creating the image.
        Otherwise stop and remove the container."""),
])
@add_options(logging_options)
def create_docker_image(
        repository: str,
        version: str,
        registry_user: str,
        registry_password: str,
        keep_container: bool,
        log_level: str,
):
    """
    Create a Docker image for data-science-sandbox.  If username and password
    for the Docker registry are specified then deploy the image to the registry.
    """
    set_log_level(log_level)
    creator = DssDockerImage(
        repository=repository,
        version=version,
        keep_container=keep_container,
    )
    if registry_user and registry_password:
        creator.registry = DockerRegistry(
            creator.repository,
            registry_user,
            registry_password,
        )
    print(f'user {creator.registry.username} password {registry_password}')
    # creator.create()
