import docker
import contextlib
import json
import logging
import requests
import time

from typing import Dict, List
from test.ports import find_free_port
from exasol.ds.sandbox.lib.dss_docker import DssDockerImage, DockerRegistry


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class LocalDockerRegistry(DockerRegistry):
    """
    Simulate Docker registry by running a local Docker container and using
    the registry inside.

    Please note for pushing images to a Docker registry with host or port
    differing from the official address requires to tag images in advance.

    So host and port must be prepended to property ``repository`` of the
    image.
    """
    def __init__(self, host_and_port: str):
        super().__init__(username=None, password=None, host_and_port=host_and_port)

    @property
    def url(self):
        return f'http://{self.host_and_port}'

    def images(self, repo_name: str) -> Dict[str, any]:
        url = f"{self.url}/v2/{repo_name}/tags/list"
        result = requests.request("GET", url)
        images = json.loads(result.content.decode("UTF-8"))
        return images

    @property
    def repositories(self) -> List[str]:
        url = f"{self.url}/v2/_catalog/"
        result = requests.request("GET", url)
        repos = json.loads(result.content.decode("UTF-8"))["repositories"]
        return repos
