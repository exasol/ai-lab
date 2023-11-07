from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.lib.dss_docker import DssDockerImage

@cli.command()
def create_dss_docker_image():
    """
    Create a Docker image for data-science-sandbox and deploy
    it to https://hub.docker.com/exasol/data-science-sandbox.
    """
    print("Hello this is create_dss_docker_image")
    # DssDockerImage.for_production().create()
