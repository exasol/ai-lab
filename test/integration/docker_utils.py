import io
import json
import re
import tarfile
import time
from datetime import datetime
from typing import Union, Tuple, Any, Dict, List, Optional, Iterator, Callable, cast

import docker
from docker.errors import BuildError
from docker.models.containers import Container
from docker.models.images import Image


class BuildContext:

    def __init__(self):
        super().__init__()
        self.fileobj = io.BytesIO()
        self._tar = tarfile.open(fileobj=self.fileobj, mode="x")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._tar.close()
        self.fileobj.seek(0)

    def __del__(self):
        self._tar.close()

    def add_string_to_file(self, name: str, string: str):
        self.add_bytes_to_file(name, string.encode("UTF-8"))

    def add_bytes_to_file(self, name: str, bytes: bytes):
        file_obj = io.BytesIO(bytes)
        self.add_fileobj_to_file(bytes, file_obj, name)

    def add_fileobj_to_file(self, bytes, file_obj, name):
        tar_info = tarfile.TarInfo(name=name)
        tar_info.mtime = time.time()
        tar_info.size = len(bytes)
        self._tar.addfile(tarinfo=tar_info, fileobj=file_obj)

    def add_host_path(self, host_path: str, path_in_tar: str, recursive: bool):
        self._tar.add(host_path, path_in_tar, recursive)

    def add_directory(self, name: str):
        tar_info = tarfile.TarInfo(name=name)
        tar_info.type = tarfile.DIRTYPE
        self._tar.addfile(tarinfo=tar_info)


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


def sanitize_test_name(test_name: str):
    test_name = re.sub('[^0-9a-zA-Z]+', '_', test_name)
    test_name = re.sub('_+', '_', test_name)
    return test_name


def container(request, base_name: str, image: Union[Image, str], start: bool = True, **kwargs) -> Container:
    client = docker.from_env()
    base_container_name = base_name.replace("-", "_")
    test_name = sanitize_test_name(str(request.node.name))
    container_name = f"{base_container_name}_{test_name}"
    try:
        image_name = image.id if hasattr(image, "id") else image
        container = client.containers.create(
            image=image_name,
            name=container_name,
            detach=True,
            **kwargs
        )
        if start:
            container.start()
        yield container
    finally:
        client.containers.get(container_name).remove(force=True)
        client.close()


def decode_bytes(bytes):
    return bytes.decode("utf-8").strip()


def exec_command(command: str, container: Container, print_output: bool = False) -> Optional[str]:
    exit_code, output = exec_run(container, command, stream=print_output)
    output_string = handle_output(output, print_output)
    handle_error_during_exec(command, exit_code, output_string)
    return output_string


def exec_run(container: Container, cmd, stream=False, environment=None, workdir=None, user='') \
        -> Tuple[Callable[[], Optional[int]], Union[bytes, Iterator[bytes]]]:
    resp = container.client.api.exec_create(
        container.id, cmd, user=user, environment=environment,
        workdir=workdir,
    )
    exec_output = container.client.api.exec_start(
        resp['Id'], stream=stream
    )

    def exit_code() -> Optional[int]:
        return cast(Optional[int], container.client.api.exec_inspect(resp['Id'])['ExitCode'])

    return (
        exit_code,
        cast(Union[bytes, Iterator[bytes]], exec_output)
    )


def handle_output(output: Union[bytes, Iterator[bytes]], print_output: bool):
    output_string = None
    if print_output and isinstance(output, Iterator):
        for chunk in output:
            print(decode_bytes(chunk))
    else:
        output_string = decode_bytes(output)
    return output_string


def handle_error_during_exec(command: str, exit_code: Callable[[], Optional[int]], output_string: str):
    exit_code = exit_code()
    if exit_code != 0:
        if output_string:
            raise RuntimeError(
                f"Command {command} failed with exit_code {exit_code} and output_string:\n {output_string}")

        raise RuntimeError(
            f"Command {command} failed with exit_code {exit_code},")
