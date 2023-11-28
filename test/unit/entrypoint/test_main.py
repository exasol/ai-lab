import pytest

from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint
from pathlib import Path


def entrypoint_method(name: str) -> str:
    return (
        "exasol.ds.sandbox.runtime.ansible.roles"
        f".entrypoint.files.entrypoint.{name}"
    )


def test_no_args(mocker):
    mocker.patch("sys.argv", ["app"])
    mocker.patch(entrypoint_method("sleep_inifinity"))
    entrypoint.main()
    assert entrypoint.sleep_inifinity.called


@pytest.mark.parametrize("warning_as_error", [True, False])
def test_copy_args_valid(mocker, warning_as_error ):
    extra_args = ["--warning-as-error"] if warning_as_error else []
    mocker.patch("sys.argv", [
        "app",
        "--notebook-defaults", "source",
        "--notebooks", "destination",
    ] + extra_args)
    mocker.patch(entrypoint_method("copy_rec"))
    mocker.patch(entrypoint_method("sleep_inifinity"))
    entrypoint.main()
    assert entrypoint.copy_rec.called
    expected = mocker.call(Path("source"), Path("destination"), warning_as_error)
    assert entrypoint.copy_rec.call_args == expected


def test_jupyter(mocker):
    jupyter = "/root/jupyterenv/bin/jupyter-lab"
    notebook_folder = Path("/root/notebooks")
    mocker.patch("sys.argv", [
        "app",
        "--notebooks", str(notebook_folder),
        "--jupyter-server", jupyter,
    ])
    mocker.patch(entrypoint_method("start_jupyter_server"))
    mocker.patch(entrypoint_method("sleep_inifinity"))
    entrypoint.main()
    assert entrypoint.start_jupyter_server.called
    expected = mocker.call(jupyter, notebook_folder)
    assert entrypoint.start_jupyter_server.call_args == expected
    assert not entrypoint.sleep_inifinity.called
