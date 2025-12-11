import json
import logging

from pathlib import Path
from typing import Tuple

from exasol.ds.sandbox.lib.ansible.ansible.facts import AnsibleFacts
from exasol.ds.sandbox.lib.ansible.ansible_access import (
    AnsibleAccess,
    AnsibleEvent,
)
from exasol.ds.sandbox.lib.ansible.ansible_run_context import AnsibleRunContext
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.setup_ec2.host_info import HostInfo
from exasol.ds.sandbox.lib.render_template import render_template

LOG = get_status_logger(LogType.ANSIBLE)


class DurationHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        self.setFormatter(logging.Formatter('%(message)s'))


class AnsibleRunner:
    """
    Encapsulates invocation ansible access. It creates the inventory file,
    writing the host info, during run.
    """
    def __init__(self, ansible_access: AnsibleAccess, work_dir: Path):
        self._ansible_access = ansible_access
        self._work_dir = work_dir
        self._duration_logger = AnsibleRunner.duration_logger()

    @classmethod
    def duration_logger(cls) -> logging.Logger:
        logger = logging.getLogger(f"{__name__}:{cls.__name__}")
        for h in logger.handlers:
            if isinstance(h, DurationHandler):
                return logger
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        logger.addHandler(DurationHandler())
        return logger

    def event_handler(self, event: AnsibleEvent) -> bool:
        if not "event_data" in event:
            return True
        duration = event["event_data"].get("duration", 0)
        if duration > 1.5:
            self._duration_logger.debug(f"duration: {round(duration)} seconds")
        return True

    def run(
            self,
            ansible_run_context: AnsibleRunContext,
            host_infos: Tuple[HostInfo],
    ) -> AnsibleFacts:
        inventory_content = render_template("inventory.jinja", host_infos=host_infos)
        with open(self._work_dir / "inventory", "w") as f:
            f.write(inventory_content)
        event_handler = self.event_handler if LOG.isEnabledFor(logging.INFO) else None
        return self._ansible_access.run(
            str(self._work_dir),
            ansible_run_context,
            event_logger=LOG.debug,
            event_handler=self.event_handler,
        )
