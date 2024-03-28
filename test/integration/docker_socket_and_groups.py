from datetime import datetime
from inspect import cleandoc
from pathlib import Path
from contextlib import contextmanager
from test.docker.in_memory_build_context import InMemoryBuildContext
from test.docker.image import image
from test.docker.container import (
    container_context,
    DOCKER_SOCKET_CONTAINER,
    wait_for_socket_access,
    assert_exec_run,
)


def numeric_gid(group_entry: str) -> int:
    """group_entry is "ubuntu:x:971:", for example"""
    return int(group_entry.split(':')[2])


class SocketInspector:
    def __init__(self, request, image_name: str, socket_on_host: Path):
        self.request = request
        self.image_name = image_name
        self.socket_on_host = socket_on_host
        self._container = None
        self._context = None

    def __enter__(self):
        self._context = container_context(
            self.request,
            image_name=self.image_name,
            volumes={ self.socket_on_host: {
                'bind': DOCKER_SOCKET_CONTAINER,
                'mode': 'rw', }, },
        )
        self._container = self._context.__enter__()
        wait_for_socket_access(self._container)
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self._container = None
        self._context.__exit__(exc_type, exc, exc_tb)

    def run(self, command: str, **kwargs) -> str:
        return assert_exec_run(self._container, command, **kwargs)

    def get_gid(self, group_name: str) -> int:
        output = self.run(f"getent group {group_name}")
        return numeric_gid(output)

    def assert_jupyter_member_of(self, group_name: str):
        output = self.run(f"getent group {group_name}")
        members = output.split(":")[3].split(",")
        assert "jupyter" in members

    def assert_write_to_socket(self):
        signal = f"Is there anybody out there {datetime.now()}?"
        self.run(
            f'bash -c "echo {signal} > {DOCKER_SOCKET_CONTAINER}"',
            user="jupyter")
        assert signal == self.socket_on_host.read_text().strip()


class GroupChanger:
    def __init__(self, context_provider):
        self._context_provider = context_provider

    def chgrp(self, gid: int, path_on_host: Path):
        path_in_container = "/mounted"
        with self._context_provider(path_on_host, path_in_container) as container:
            assert_exec_run(container, f"chgrp {gid} {path_in_container}")

    def chown_chmod_recursive(
            self,
            owner: str,
            permissions: str,
            path_on_host: Path,
    ):
        """`owner` may be specifed as user or user:group"""
        path_in_container = "/mounted"
        with self._context_provider(path_on_host, path_in_container) as container:
            assert_exec_run(container, f"chown -R {owner} {path_in_container}")
            assert_exec_run(container, f"chmod -R {permissions} {path_in_container}")


@contextmanager
def dss_image_with_added_group(request, base_image, gid, group_name):
    dockerfile_content = cleandoc(
        f"""
        FROM {base_image}
        RUN sudo groupadd --gid {gid} {group_name}
        """
    )
    with InMemoryBuildContext() as context:
        context.add_string_to_file(name="Dockerfile", string=dockerfile_content)
    yield from image(
        request,
        name=f"ai_lab_with_additional_group",
        fileobj=context.fileobj,
        custom_context=True,
    )
