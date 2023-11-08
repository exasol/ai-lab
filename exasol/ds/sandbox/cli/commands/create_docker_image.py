import click

from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.lib.dss_docker import DssDockerImage


_options = [
    click.option(
        '--repository', type=str, metavar="ORG/REPO", show_default=True,
        default="exasol/data-science-sandbox",
        help="Organization and repository on hub.docker.com to publish the docker image to."),
    click.option(
        '--publish', type=bool, default=False, show_default=True,
        help="Whether to publish the created Docker image"),
]


@cli.command()
@add_options(_options)
def create_docker_image(repository: str, publish: bool):
    """
    Create a Docker image for data-science-sandbox and deploy
    it to a Docker repository.
    """
    print("Hello this is create_docker_image, using")
    print(f'- publish: {publish}')
    print(f'- repository: "{repository}"')
    DssDockerImage(
        repository=repository,
        publish=publish,
    ).create()
