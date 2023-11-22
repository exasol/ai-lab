import ansible_runner
import json
import logging

from dataclasses import dataclass
from typing import Callable, Dict, Optional

from exasol.ds.sandbox.lib.ansible.ansible_run_context import AnsibleRunContext
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType


class AnsibleException(RuntimeError):
    pass


AnsibleEvent = Dict[str, any]
AnsibleFacts = Dict[str, any]

class AnsibleAccess:
    """
    Provides access to ansible runner.
    @raises: AnsibleException if ansible execution fails
    """
    @staticmethod
    def run(
            private_data_dir: str,
            run_ctx: AnsibleRunContext,
            event_logger: Callable[[str], None],
            event_handler: Callable[[AnsibleEvent], bool] = None,
    ) -> AnsibleFacts:
        quiet = not get_status_logger(LogType.ANSIBLE).isEnabledFor(logging.INFO)
        r = ansible_runner.run(
            private_data_dir=private_data_dir,
            playbook=run_ctx.playbook,
            quiet=quiet,
            event_handler=event_handler,
            extravars=run_ctx.extra_vars,
        )
        for e in r.events:
            event_logger(json.dumps(e, indent=2))

        if r.rc != 0:
            raise AnsibleException(r.rc)

        if not "docker_container" in run_ctx.extra_vars:
            return {}

        host = run_ctx.extra_vars["docker_container"]
        fact_cache = r.get_fact_cache(host)
        return fact_cache
