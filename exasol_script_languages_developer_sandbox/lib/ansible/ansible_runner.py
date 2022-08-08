import logging
from pathlib import Path
from typing import Tuple

from exasol_script_languages_developer_sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_run_context import AnsibleRunContext
from exasol_script_languages_developer_sandbox.lib.host_info import HostInfo
from exasol_script_languages_developer_sandbox.lib.render_template import render_template


class AnsibleRunner:
    """
    Encapsulates invocation ansible access. It creates the inventory file, writing the host info, during run.
    """
    def __init__(self, ansible_access: AnsibleAccess, work_dir: Path):
        self._ansible_access = ansible_access
        self._work_dir = work_dir

    @staticmethod
    def printer(msg: str):
        logging.info(msg)

    def run(self, ansible_run_context: AnsibleRunContext, host_infos: Tuple[HostInfo]):
        inventory_content = render_template("inventory.jinja", host_infos=host_infos)
        with open(self._work_dir / "inventory", "w") as f:
            f.write(inventory_content)
        self._ansible_access.run(str(self._work_dir), ansible_run_context, self.printer)
