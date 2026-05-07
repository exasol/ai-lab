import crypt
from typing import Any

import exasol.ansible as ansible

from exasol.ds.sandbox.lib.setup_ec2.ansible_execution import (
    DEFAULT_REPOSITORIES,
    default_reset_password_playbook,
)


def run_reset_password(
    ansible_access: ansible.Access,
    default_password: str,
    host_infos: tuple[Any, ...] = tuple(),
    playbook: ansible.Playbook | None = None,
    ansible_repositories: tuple[ansible.Repository, ...] = DEFAULT_REPOSITORIES,
) -> None:
    """
    Resets the password and removes the .ssh directory via ansible.
    The ansible working dir is created dynamically and removed afterwards.
    Any hosts, given by variable host_infos, are added to the ansible inventory in the dynamic working directory.
    All ansible repositories, given by variable ansible_repositories,
    are copied as flat copy to the dynamic working copy, too.
    The playbook parameter indicates which playbook to run and can contain additional Ansible variables.
    The default password will be used to set a default password for the default user in the VM; however it will be
    set a 'expired', thus the user is required to set a new password during the first login.
    The parameter ansible_access is used to interact with Ansible (dependency injection).
    """
    password_hash = crypt.crypt(default_password, salt=crypt.METHOD_SHA512)
    new_extra_vars = {"default_vm_password_hash": password_hash}
    playbook = playbook or default_reset_password_playbook()
    new_extra_vars.update(playbook.vars)
    playbook = ansible.Playbook(playbook.file, new_extra_vars)
    with ansible.Context(ansible_access, ansible_repositories) as runner:
        runner.run(playbook, host_infos=host_infos)
