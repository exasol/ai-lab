from dataclasses import (
    dataclass,
    field,
)

import exasol.ansible as ansible
import exasol.ds.sandbox.runtime.ansible as runtime_ansible

DEFAULT_REPOSITORIES = (ansible.ImportlibRepository(runtime_ansible),)


def default_install_dependencies_playbook() -> ansible.Playbook:
    return ansible.Playbook(file="ec2_playbook.yml")


def default_reset_password_playbook() -> ansible.Playbook:
    return ansible.Playbook(file="reset_password.yml")


@dataclass
class AnsibleDependencyInstaller:
    ansible_access: ansible.Access
    playbook: ansible.Playbook = field(
        default_factory=default_install_dependencies_playbook,
    )
    repositories: tuple[ansible.Repository, ...] = DEFAULT_REPOSITORIES
