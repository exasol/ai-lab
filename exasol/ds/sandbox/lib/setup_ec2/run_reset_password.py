from typing import Tuple

from exasol.ds.sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol.ds.sandbox.lib.ansible.ansible_context_manager import AnsibleContextManager
from exasol.ds.sandbox.lib.ansible.ansible_repository import AnsibleRepository, \
    default_repositories
from exasol.ds.sandbox.lib.ansible.ansible_run_context import AnsibleRunContext, \
    reset_password_ansible_run_context

from exasol.ds.sandbox.lib.setup_ec2.host_info import HostInfo
import crypt


def run_reset_password(ansible_access: AnsibleAccess, default_password: str,
                       host_infos: Tuple[HostInfo, ...] = tuple(),
                       ansible_run_context: AnsibleRunContext = reset_password_ansible_run_context,
                       ansible_repositories: Tuple[AnsibleRepository, ...] = default_repositories) -> None:
    """
    Resets the password and removes the .ssh directory via ansible.
    The ansible working dir is created dynamically and removed afterwards.
    Any hosts, given by variable host_infos, are added to the ansible inventory in the dynamic working directory.
    All ansible repositories, given by variable ansible_repositories,
    are copied as flat copy to the dynamic working copy, too.
    The playbook is indicated by variable ansible_run_context, which also might contain additional ansible variables.
    The default password will be used to set a default password for the default user in the VM; however it will be
    set a 'expired', thus the user is required to set a new password during the first login.
    The parameter ansible_access is used to interact with Ansible (dependency injection).
    """
    hash = crypt.crypt(default_password, salt=crypt.METHOD_SHA512)
    new_extra_vars = { "default_vm_password": hash }

    if ansible_run_context.extra_vars is not None:
        new_extra_vars.update(ansible_run_context.extra_vars)
    new_ansible_run_context = AnsibleRunContext(ansible_run_context.playbook, new_extra_vars)
    with AnsibleContextManager(ansible_access, ansible_repositories) as ansible_runner:
        ansible_runner.run(new_ansible_run_context, host_infos=host_infos)
