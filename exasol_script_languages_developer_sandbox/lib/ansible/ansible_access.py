from typing import Callable

import ansible_runner

from exasol_script_languages_developer_sandbox.lib.ansible.ansible_run_context import AnsibleRunContext


class AnsibleException(RuntimeError):
    pass


class AnsibleAccess:

    """
    Provides access to ansible runner.
    @raises: AnsibleException if ansible execution fails
    """
    @staticmethod
    def run(private_data_dir: str, run_ctx: AnsibleRunContext, printer: Callable[[str], None]):
        r = ansible_runner.run(private_data_dir=private_data_dir,
                               playbook=run_ctx.playbook,
                               extravars=run_ctx.extra_vars)
        for e in r.events:
            printer(e)
        if r.rc != 0:
            raise AnsibleException(r.rc)
