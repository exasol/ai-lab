import json
import logging
import re

from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

import docker
from docker.errors import BuildError
from docker.models.images import Image


_logger = logging.getLogger(__name__)


@dataclass
class DockerImageSpec:
    repository: str
    tag: str

    @property
    def name(self) -> str:
        return f"{self.repository}:{self.tag}"


def format_build_log(build_log: List[Dict[str, Any]]):
    def format_entry(entry: Dict[str, Any]):
        if "stream" in entry:
            return entry["stream"]
        if "error" in entry:
            return entry["error"]
        return ""

    return "\n".join(format_entry(entry) for entry in build_log)


class BuildErrorWithLog(BuildError):
    def __init__(self, reason, build_log: List[Dict[str, Any]]):
        super().__init__(f"{reason}\n\n{format_build_log(build_log)}", build_log)


def pull(
    spec: DockerImageSpec,
    auth_config: Optional[Dict[str, str]] = None,
):
    client = docker.from_env()
    if not client.images.list(spec.name):
        _logger.debug(f"Pulling Docker image {spec.name}")
        client.images.pull(
            spec.repository,
            spec.tag,
            auth_config=auth_config,
        )


def image(request, name: str, print_log=False, **kwargs) -> Image:
    """
    Create a Docker image.
    The function supports a pair of pytest cli options with a suffix derived from parameter ``name``:
    Option `--docker-image-(suffix)` specifies the name of an existing image to be used
    instead of creating a new one.
    Option `--keep-docker-image-(suffix)` skips removing the image after test execution.
    """
    base_command_line = name.replace("_", "-")
    image_tag = request.config.getoption(f"--docker-image-{base_command_line}")
    keep_image = request.config.getoption(f"--keep-docker-image-{base_command_line}")
    client = docker.from_env()
    if image_tag:
        yield client.images.get(image_tag)
        return
    timestamp = f'{datetime.now().timestamp():.0f}'
    image_name = name.replace("-", "_")
    image_tag = f"{image_name}:{timestamp}"
    try:
        # rm=True removes intermediate containers after building
        log_generator = client.api.build(tag=image_tag, rm=True, **kwargs)
        image_id, log, error = analyze_build_log(log_generator)
        if image_id is None:
            raise BuildErrorWithLog(error, log)
        if print_log:
            print(format_build_log(log))
        yield client.images.get(image_id)
    finally:
        if not keep_image:
            client.images.remove(image_tag, force=True)
        client.close()


def analyze_build_log(log_generator) -> Tuple[Optional[str], List[Dict[str, Any]], Optional[str]]:
    log = [json.loads(chunk) for chunk in log_generator]  #
    last_event = "Unknown"
    for entry in log:
        if 'error' in entry:
            return None, log, entry["error"]
        if 'stream' in entry:
            match = re.search(
                r'(^Successfully built |sha256:)([0-9a-f]+)$',
                entry['stream']
            )
            if match:
                image_id = match.group(2)
                return image_id, log, None
        last_event = entry
    return None, log, last_event
