from inspect import cleandoc
from test.unit.entrypoint.entrypoint_mock import entrypoint_method
from unittest.mock import (
    Mock,
    call,
)

from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint


def test_success(mocker, caplog):
    mocker.patch(entrypoint_method("subprocess.run"))
    entrypoint.subprocess.run.return_value = Mock(returncode=0)
    entrypoint.change_jupyter_password("jupyter_core", "new-pwd", env={})
    call_args = entrypoint.subprocess.run.call_args
    assert call_args.args[0] == ["jupyter_core", "server", "password"]
    assert call_args.kwargs["input"] == "new-pwd\nnew-pwd\n"
    assert "Successfully changed the password" in caplog.text


def test_failure(mocker, caplog):
    mocker.patch(entrypoint_method("subprocess.run"))
    mocker.patch(entrypoint_method("sys.exit"))
    rc = 123
    entrypoint.subprocess.run.return_value = Mock(returncode=rc, stdout="some error")
    entrypoint.change_jupyter_password("jcore", "new-pwd", env={})
    entrypoint.sys.exit.call_args == call(rc)
    expected = cleandoc(
        f"""
        Failed to change password.
        jcore exited with return code {rc} and output:
        some error
        """
    )
    assert expected in caplog.text
