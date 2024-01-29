from typing import Optional, Tuple, Callable, Union, Iterator, cast, Dict, Mapping

from docker.models.containers import Container


def decode_bytes(bytes):
    return bytes.decode("utf-8").strip()


def exec_command(
        command: str,
        container: Container,
        print_output: bool = False,
        workdir: Optional[str] = None,
        environment: Optional[Mapping[str, str]] = None,
        user: str = ''
) -> Optional[str]:
    exit_code, output = exec_run(container, command, stream=print_output,
                                 workdir=workdir, environment=environment, user=user)
    output_string = handle_output(output, print_output)
    handle_error_during_exec(command, exit_code, output_string)
    return output_string


def exec_run(container: Container, cmd, stream=False, environment=None, workdir=None, user='') \
        -> Tuple[Callable[[], Optional[int]], Union[bytes, Iterator[bytes]]]:
    """
    Run a command in the provided Docker container and return 
    a function to inquire the exit code and the stdout as stream or byte array.
    """
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
