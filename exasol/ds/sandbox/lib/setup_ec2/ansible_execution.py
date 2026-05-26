from dataclasses import dataclass, field

import exasol.ansible as ansible
import exasol.ds.sandbox.runtime.ansible as runtime_ansible

DEFAULT_REPOSITORIES = (ansible.ImportlibRepository(runtime_ansible),)
DEFAULT_INSTALL_DEPENDENCIES_PLAYBOOK = ansible.Playbook(file="ec2_playbook.yml")
DEFAULT_RESET_PASSWORD_PLAYBOOK = ansible.Playbook(file="reset_password.yml")


@dataclass
class AnsibleDependencyInstaller:
    playbook: ansible.Playbook = field(default_factory=lambda: DEFAULT_INSTALL_DEPENDENCIES_PLAYBOOK)
    repositories: tuple[ansible.Repository, ...] = DEFAULT_REPOSITORIES
