from inspect import cleandoc
from pathlib import Path
from unittest.mock import Mock

import pytest

from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint


class Testee:
    __test__ = False # suppress: PytestCollectionWarning

    def __init__(self, dir: Path):
        self.script = dir / "script.sh"
        self.logfile = dir / "log.log"

    def create_script(self, before="", after=""):
        """
        Parameters :before: and :after: will be inserted into the sample
        script before and after reporting Jupyter Server to be running.
        """
        prefix = "[I 2024-01-22 13:27:48.808 ServerApp]"
        self.script.write_text(cleandoc(f"""
            #!/bin/bash
            echo "first log message"
            sleep .2
            {before}
            echo "{prefix} Jupyter Server 2.12.15 is running at:"
            {after}
            sleep .4
            echo "last log message"
        """))
        self.script.chmod(0o744)
        return self

    def run(self):
        args = Mock(
            home="home",
            jupyter_server=self.script,
            jupyter_core="core",
            port=123,
            notebooks="notebooks",
            jupyter_logfile=self.logfile,
            user="user",
            password="default-pwd",
            venv=Path("venv"),
        )
        entrypoint.start_jupyter_server(args, poll_sleep = 0.1)
        return self


def test_success(tmp_path, caplog):
    testee = Testee(tmp_path).create_script().run()
    assert entrypoint.SUCCESS_MESSAGE in caplog.text


def test_early_error(tmp_path, caplog):
    with pytest.raises(SystemExit) as ex:
        testee = Testee(tmp_path).create_script(before="exit 22").run()
    assert ex.value.code == 22
    assert entrypoint.SUCCESS_MESSAGE not in caplog.text
    assert "Jupyter server terminated with error code 22" in caplog.text


def test_late_error(tmp_path, caplog):
    with pytest.raises(SystemExit) as ex:
        testee = Testee(tmp_path).create_script(after="exit 23").run()
    assert ex.value.code == 23
    assert "Changed environment variable PATH to venv/bin:" in caplog.text
    assert entrypoint.SUCCESS_MESSAGE in caplog.text
    assert "Jupyter server terminated with error code 23" in caplog.text
