import os

# We need to manually import all fixtures that we use, directly or indirectly,
# since the pytest won't do this for us.
from notebook_test_utils import (
    backend_setup,
    notebook_runner,
    set_log_level_for_libraries,
)


set_log_level_for_libraries()


def test_quickstart(notebook_runner, monkeypatch) -> None:
    monkeypatch.setenv("EXASOL_HOST", "localhost")
    monkeypatch.setenv("EXASOL_PORT", "8563")
    monkeypatch.setenv("EXASOL_USER", "sys")
    monkeypatch.setenv("EXASOL_PASSWORD", "exasol")
    monkeypatch.setenv("EXASOL_SCHEMA", "AI_LAB")

    current_dir = os.getcwd()
    try:
        notebook_runner('main_config.ipynb')
        os.chdir('../jupysql')
        notebook_runner('quickstart.ipynb')
    finally:
        os.chdir(current_dir)
