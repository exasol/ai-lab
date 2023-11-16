import logging
from pathlib import Path
from typing import Dict, Tuple

from exasol.ds.sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol.ds.sandbox.lib.ansible.ansible_run_context import AnsibleRunContext
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.setup_ec2.host_info import HostInfo
from exasol.ds.sandbox.lib.render_template import render_template

LOG = get_status_logger(LogType.ANSIBLE)


class AnsibleRunner:
    """
    Encapsulates invocation ansible access. It creates the inventory file, writing the host info, during run.
    """
    def __init__(self, ansible_access: AnsibleAccess, work_dir: Path):
        self._ansible_access = ansible_access
        self._work_dir = work_dir

    @staticmethod
    def printer(msg: str):
        LOG.debug(msg)

    @staticmethod
    def event_handler(event: Dict[str, any]) -> bool:
        try:
            duration = event["event_data"]["duration"]
            if duration is not None and duration > 0.5:
                print(f"duration: {round(duration)} seconds")
        except KeyError as ex:
            pass
        return True

    def run(self, ansible_run_context: AnsibleRunContext, host_infos: Tuple[HostInfo]):
        inventory_content = render_template("inventory.jinja", host_infos=host_infos)
        with open(self._work_dir / "inventory", "w") as f:
            f.write(inventory_content)
        event_handler = self.event_handler if LOG.isEnabledFor(logging.INFO) else None
        self._ansible_access.run(
            str(self._work_dir),
            ansible_run_context,
            self.printer,
            event_handler,
        )
