import pytest
from unittest.mock import MagicMock, create_autospec

from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint
from pathlib import Path


def entrypoint_method(name: str) -> str:
    return (
        "exasol.ds.sandbox.runtime.ansible.roles"
        f".entrypoint.files.entrypoint.{name}"
    )


def test_no_args(mocker):
    mocker.patch("sys.argv", ["app"])
    mocker.patch(entrypoint_method("sleep_infinity"))
    entrypoint.main()
    assert entrypoint.sleep_infinity.called


def test_user_arg(mocker):
    mocker.patch("sys.argv", [
        "app",
        "--user", "jennifer",
        "--group", "users",
        "--docker-group", "docker",
    ])
    user = create_autospec(entrypoint.User)
    mocker.patch(entrypoint_method("User"), return_value=user)
    user.own.return_value = user
    mocker.patch(entrypoint_method("sleep_infinity"))
    entrypoint.main()
    assert entrypoint.User.called
    args = entrypoint.User.call_args = mocker.call(
        "jennifer",
        entrypoint.Group("users"),
        entrypoint.Group("docker"),
    )
    assert user.own.called
    assert user.own.call_args == mocker.call("/var/run/docker.sock")
    assert user.switch_to.called


@pytest.mark.parametrize("warning_as_error", [True, False])
def test_copy_args_valid(mocker, warning_as_error ):
    extra_args = ["--warning-as-error"] if warning_as_error else []
    mocker.patch("sys.argv", [
        "app",
        "--notebook-defaults", "source",
        "--notebooks", "destination",
    ] + extra_args)
    mocker.patch(entrypoint_method("copy_rec"))
    mocker.patch(entrypoint_method("sleep_infinity"))
    entrypoint.main()
    assert entrypoint.copy_rec.called
    expected = mocker.call(Path("source"), Path("destination"), warning_as_error)
    assert entrypoint.copy_rec.call_args == expected


def test_jupyter(mocker):
    jupyter = "/root/jupyterenv/bin/jupyter-lab"
    port = "1234"
    notebook_folder = Path("/root/notebooks")
    logfile = Path("/root/jupyter-server.log")
    mocker.patch("sys.argv", [
        "app",
        "--home", "home-directory",
        "--notebooks", str(notebook_folder),
        "--jupyter-server", jupyter,
        "--port", port,
        "--user", "usr",
        "--password", "pwd",
        "--jupyter-logfile", str(logfile),
    ])
    mocker.patch(entrypoint_method("User"))
    mocker.patch(entrypoint_method("start_jupyter_server"))
    mocker.patch(entrypoint_method("sleep_infinity"))
    entrypoint.main()
    assert entrypoint.start_jupyter_server.called
    expected = mocker.call(
        "home-directory",
        jupyter,
        int(port),
        notebook_folder,
        logfile,
        "usr",
        "pwd",
    )
    assert entrypoint.start_jupyter_server.call_args == expected
    assert not entrypoint.sleep_infinity.called
