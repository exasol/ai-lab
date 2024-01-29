import json
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

import docker
from docker.errors import BuildError
from docker.models.images import Image


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


def image(request, name: str, print_log=False, **kwargs) -> Image:
    base_command_line = name.replace("_", "-")
    image_tag = request.config.getoption(f"--docker-image-{base_command_line}")
    keep_image = request.config.getoption(f"--keep-docker-image-{base_command_line}")
    client = docker.from_env()
    if image_tag:
        return client.images.get(image_tag)
    timestamp = f'{datetime.now().timestamp():.0f}'
    image_name = name.replace("-", "_")
    image_tag = f"{image_name}:{timestamp}"
    try:
        log_generator = client.api.build(tag=image_tag, **kwargs)
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
