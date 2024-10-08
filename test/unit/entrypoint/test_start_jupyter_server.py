import pytest


from pathlib import Path
from inspect import cleandoc
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
        self.script.write_text(cleandoc(f"""
            #!/bin/bash
            echo "first log message"
            sleep .2
            {before}
            echo "[I 2024-01-22 13:27:48.808 ServerApp] Jupyter Server 2.12.15 is running at:"
            {after}
            sleep .4
            echo "last log message"
        """))
        self.script.chmod(0o744)
        return self

    def run(self):
        entrypoint.start_jupyter_server(
            "home",
            self.script,
            "port",
            "notebooks",
            self.logfile,
            "user",
            "password",
            Path("venv"),
            poll_sleep = 0.1,
        )
        return self


def test_success(tmp_path, caplog):
    testee = Testee(tmp_path).create_script().run()
    assert "Server for Jupyter has been started successfully." in caplog.text


def test_early_error(tmp_path, caplog):
    with pytest.raises(SystemExit) as ex:
        testee = Testee(tmp_path).create_script(before="exit 22").run()
    assert ex.value.code == 22
    assert "Server for Jupyter has been started successfully." not in caplog.text
    assert "Jupyter Server terminated with error code 22" in caplog.text


def test_late_error(tmp_path, caplog):
    with pytest.raises(SystemExit) as ex:
        testee = Testee(tmp_path).create_script(after="exit 23").run()
    assert ex.value.code == 23
    assert "Changed environment variable PATH to venv/bin:" in caplog.text
    assert "Server for Jupyter has been started successfully." in caplog.text
    assert "Jupyter Server terminated with error code 23" in caplog.text
