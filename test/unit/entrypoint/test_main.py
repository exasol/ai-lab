from pathlib import Path
from test.unit.entrypoint.entrypoint_mock import entrypoint_method
from unittest.mock import (
    Mock,
    create_autospec,
)

import pytest

from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint


def test_no_args(mocker):
    mocker.patch("sys.argv", ["app"])
    mocker.patch(entrypoint_method("sleep_infinity"))
    mocker.patch(entrypoint_method("copy_rec"))
    mocker.patch(entrypoint_method("subprocess.run"))
    mocker.patch(entrypoint_method("start_jupyter_server"))
    user = create_autospec(entrypoint.User, is_specified=False)
    mocker.patch(entrypoint_method("User"), return_value=user)
    entrypoint.main()
    assert not user.enable_group_access.called
    assert not user.chown_recursive.called
    assert not entrypoint.copy_rec.called
    assert not entrypoint.start_jupyter_server.called
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
    user.enable_group_access.return_value = user
    mocker.patch(entrypoint_method("sleep_infinity"))
    entrypoint.main()
    assert entrypoint.User.called
    args = entrypoint.User.call_args = mocker.call(
        "jennifer",
        entrypoint.Group("users"),
        entrypoint.Group("docker"),
    )
    assert user.enable_group_access.called
    assert user.enable_group_access.call_args == mocker.call(Path("/var/run/docker.sock"))
    assert user.switch_to.called


def test_chown_recursive_args(mocker):
    dir = "/path/to/final/notebooks"
    mocker.patch("sys.argv", [
        "app",
        "--user", "jennifer",
        "--group", "users",
        "--docker-group", "docker",
        "--notebooks", dir,
    ])
    user = create_autospec(entrypoint.User)
    mocker.patch(entrypoint_method("User"), return_value=user)
    mocker.patch(entrypoint_method("sleep_infinity"))
    entrypoint.main()
    assert user.chown_recursive.called
    assert user.chown_recursive.call_args == mocker.call(Path(dir))


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
    venv = Path("/root/jupyterenv")
    mocker.patch("sys.argv", [
        "app",
        "--home", "home-directory",
        "--notebooks", str(notebook_folder),
        "--venv", str(venv),
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
    # Args to start_jupyter_server() have been simplified. Hence this test
    # does not make too much sense anymore.
    #
    # expected = mocker.call(
    #     "home-directory",
    #     jupyter,
    #     int(port),
    #     notebook_folder,
    #     logfile,
    #     "usr",
    #     "pwd",
    #     venv,
    # )
    # assert entrypoint.start_jupyter_server.call_args == expected
    assert not entrypoint.sleep_infinity.called
