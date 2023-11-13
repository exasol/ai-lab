import ansible_runner
import logging

from typing import Callable

from exasol.ds.sandbox.lib.ansible.ansible_run_context import AnsibleRunContext
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType


class AnsibleException(RuntimeError):
    pass


class AnsibleAccess:
    """
    Provides access to ansible runner.
    @raises: AnsibleException if ansible execution fails
    """
    @staticmethod
    def run(private_data_dir: str, run_ctx: AnsibleRunContext, printer: Callable[[str], None]):
        quiet = not get_status_logger(LogType.ANSIBLE).isEnabledFor(logging.INFO)
        r = ansible_runner.run(private_data_dir=private_data_dir,
                               playbook=run_ctx.playbook,
                               quiet=quiet,
                               extravars=run_ctx.extra_vars)
        for e in r.events:
            printer(e)
        if r.rc != 0:
            raise AnsibleException(r.rc)
