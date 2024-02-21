import click
import os

from exasol.ds.sandbox.cli.cli import cli, option_with_env_default
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.lib.dss_docker import (
    DEFAULT_ORG_AND_REPOSITORY,
    DssDockerImage,
    DockerRegistry,
)
from exasol.ds.sandbox.lib.logging import SUPPORTED_LOG_LEVELS
from exasol.ds.sandbox.lib.logging import set_log_level


USER_ENV = "DOCKER_REGISTRY_USER"
PASSWORD_ENV = "DOCKER_REGISTRY_PASSWORD"


@cli.command()
@add_options([
    click.option(
        "--repository", type=str, metavar="ORG/REPO",
        show_default=True,
        default=DEFAULT_ORG_AND_REPOSITORY,
        help="Organization and repository to publish the docker image to."),
    click.option(
        "--version", type=str, metavar="VERSION",
        help="Docker image version tag"),
    click.option(
        "--publish", type=bool, is_flag=True,
        help="Whether to publish the created Docker image"),
    click.option(
        "--registry", type=str, metavar="HOST[:PORT]",
        help="""
        Optional host and port of Docker registry. If not specified then the
        command will use hub.docker.com:5000, see
        https://docs.docker.com/engine/reference/commandline/tag.
        """),
    click.option(
        "--registry-user", type=str, metavar="USER",
        default=lambda: os.environ.get(USER_ENV, None),
        help=f"""
        Username for Docker registry [defaults to environment
        variable {USER_ENV}]. If specified then password is read
        from environment variable {PASSWORD_ENV}.
        """
        ),
    click.option(
        "--keep-container", type=bool, is_flag=True,
        help="""Keep the Docker Container running after creating the image.
        Otherwise stop and remove the container."""),
])
@add_options(logging_options)
def create_docker_image(
        repository: str,
        registry: str,
        version: str,
        publish: bool,
        registry_user: str,
        keep_container: bool,
        log_level: str,
):
    """
    Create a Docker image for ai-lab.  If option ``--publish`` is
    specified then deploy the image to the Docker registry using the specified
    user name and reading the password from environment variable
    ``PASSWORD_ENV``.
    """
    def registry_password():
        if registry_user is None:
            return None
        return os.environ.get(PASSWORD_ENV, None)

    set_log_level(log_level)
    creator = DssDockerImage(repository, version, keep_container)
    if publish:
        creator.registry = DockerRegistry(
            registry_user,
            registry_password(),
            host_and_port=registry,
        )
    creator.create()
