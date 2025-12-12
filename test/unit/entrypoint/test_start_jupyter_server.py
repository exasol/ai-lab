from __future__ import annotations

import os
import re
from inspect import cleandoc
from pathlib import Path
from unittest.mock import (
    Mock,
    patch,
)

import pytest

from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint


class Testee:
    __test__ = False # suppress PytestCollectionWarning

    def __init__(self, dir: Path):
        self.server = dir / "server.sh"
        self.core = dir / "core.sh"
        self.logfile = dir / "log.log"

    def _create_script(self, path: Path, content: str) -> Testee:
        path.write_text("#!/bin/bash\n" + cleandoc(content))
        path.chmod(0o744)
        return self

    def core_script(self, event=""):
        """
        Create a script simulating the Jupyter core executable.
        """
        return self._create_script(self.core, event)

    def server_script(self, before="", after=""):
        """
        Create a script simulating the Jupyter server executable.
        Parameters :before: and :after: will be inserted into the script
        before and after reporting Jupyter Server to be running.
        """
        prefix = "[I 2024-01-22 13:27:48.808 ServerApp]"
        return self._create_script(
            self.server,
            f"""
            echo "first log message"
            sleep .2
            {before}
            echo "{prefix} Jupyter Server 2.12.15 is running at:"
            {after}
            sleep .4
            echo "last log message"
            """
        )

    def run(self):
        args = Mock(
            home="home",
            jupyter_server=self.server,
            jupyter_core=self.core,
            port=123,
            notebooks="notebooks",
            jupyter_logfile=self.logfile,
            user="user",
            password="default-pwd",
            venv=Path("venv"),
        )
        entrypoint.start_jupyter_server(args, poll_sleep = 0.1)
        return self


@pytest.mark.parametrize("env, expected_message", [
    ({}, "The default password is .*You can change it by"),
    ({entrypoint.PASSWORD_ENV: "new-pwd"}, ""),
])
def test_success(env, expected_message, tmp_path, caplog, monkeypatch):
    with patch.dict(os.environ, env):
        Testee(tmp_path).server_script().core_script().run()
    assert entrypoint.SUCCESS_MESSAGE in caplog.text
    assert re.search(expected_message, caplog.text, re.DOTALL)


def test_change_password_failed(tmp_path, caplog, mocker):
    testee = Testee(tmp_path).server_script()
    testee.core_script("echo simulated failure; exit 1")
    mocker.patch.dict(os.environ, {entrypoint.PASSWORD_ENV: "new-pwd"})
    with pytest.raises(SystemExit) as ex:
        testee.run()
    expected = cleandoc(
        f"""
        {testee.core} exited with return code 1 and output:
        simulated failure
        """
    )
    assert expected in caplog.text
    assert entrypoint.SUCCESS_MESSAGE not in caplog.text


def test_early_error(tmp_path, caplog):
    with pytest.raises(SystemExit) as ex:
        Testee(tmp_path).server_script(before="exit 22").run()
    assert ex.value.code == 22
    assert entrypoint.SUCCESS_MESSAGE not in caplog.text
    assert "Jupyter server terminated with error code 22" in caplog.text


def test_late_error(tmp_path, caplog):
    with pytest.raises(SystemExit) as ex:
        Testee(tmp_path).server_script(after="exit 23").run()
    assert ex.value.code == 23
    assert "Changed environment variable PATH to venv/bin:" in caplog.text
    assert entrypoint.SUCCESS_MESSAGE in caplog.text
    assert "Jupyter server terminated with error code 23" in caplog.text
