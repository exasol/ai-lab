import json
import subprocess
from pathlib import Path
from typing import NamedTuple

import pytest
from jinja2 import Template


jupyter_update_msg_heading = """__TEST_JUPYTER_PASSWORD_HEADING___"""

@pytest.fixture()
def motd_file(tmp_path):
    jupyter_server_config_file = tmp_path / "jupyter_server_config.json"
    python_file = tmp_path / "999_jupyter.py"

    src_path = Path(__file__).parent.parent / "exasol.ds.sandbox" / "runtime" / \
               "ansible" / "roles" / "jupyter" / "templates" / "etc" /"update-motd.d" / "999-jupyter"
    with open(src_path, "r") as f:
        python_code_template = f.read()
    python_template = Template(python_code_template)

    class jupyterlab(NamedTuple):
        virtualenv = "dummy_env"
        password = "dummy_password"

    python_code = python_template.render(user_name="test_user", jupyterlab=jupyterlab(),
                                         jupyter_server_config_file=str(jupyter_server_config_file),
                                         jupyter_server_hashed_password="dummy_password_hash",
                                         heading_jupyter_update_password=jupyter_update_msg_heading)
    with open(python_file, "w") as f:
        f.write(python_code)
    yield python_file, jupyter_server_config_file


def test_motd_jupyter_template_prints_password_message(motd_file):
    """
    Test which runs the motd jupyter template and validates that the message is printed
    because the password matches.
    """
    python_file, jupyter_server_config_file = motd_file
    mock_data = {
        "ServerApp": {
        "password": "dummy_password_hash"
        }
    }
    with open(jupyter_server_config_file, "w") as f:
        json.dump(mock_data, f)

    result = subprocess.run(["python3", python_file], capture_output=True)
    assert jupyter_update_msg_heading in result.stdout.decode("utf-8")


def test_motd_jupyter_template_prints_password_message_not_if_passward_was_changed(motd_file):
    """
    Test which runs the motd jupyter template and validates that the message is not printed
    because the password does not match.
    """
    python_file, jupyter_server_config_file = motd_file
    mock_data = {
        "ServerApp": {
        "password": "NOT_MATCHING_PASSWORD"
        }
    }
    with open(jupyter_server_config_file, "w") as f:
        json.dump(mock_data, f)

    result = subprocess.run(["python3", python_file], capture_output=True)
    assert result.stdout.decode("utf-8") == ""
