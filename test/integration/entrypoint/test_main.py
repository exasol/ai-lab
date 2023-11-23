import pytest

from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint
from pathlib import Path


def test_no_args(capsys, mocker):
    mocker.patch("sys.argv", ["app"])
    entrypoint.main()


def test_copy_args_unbalanced(mocker):
    mocker.patch("sys.argv", [
        "app",
        "--copy-from", "a",
        "--copy-from", "b",
        "--copy-to", "dst",
    ])
    expected = (
        "Found CLI option"
        " --copy-from 2 times and"
        " --copy-to 1 times,"
        " but number must be identical."
    )
    with pytest.raises(RuntimeError, match=expected):
        entrypoint.main()


def entrypoint_method(name: str) -> str:
    return (
        "exasol.ds.sandbox.runtime.ansible.roles"
        f".entrypoint.files.entrypoint.{name}"
    )


def test_copy_args_valid(mocker):
    mocker.patch("sys.argv", [
        "app",
        "--copy-from", "source",
        "--copy-to", "destination",
    ])
    mocker.patch(entrypoint_method("copy_rec"))
    entrypoint.main()
    assert entrypoint.copy_rec.called
    expected = mocker.call(Path("source"), Path("destination"))
    assert entrypoint.copy_rec.call_args == expected


def test_jupyter(mocker):
    mocker.patch("sys.argv", [ "app", "--jupyter-server" ])
    mocker.patch(entrypoint_method("start_jupyter_server"))
    entrypoint.main()
    assert entrypoint.start_jupyter_server.called
