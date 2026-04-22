from dataclasses import (
    dataclass,
    field,
)

from exasol.ds.sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol.ds.sandbox.lib.ansible.ansible_repository import (
    AnsibleRepository,
    default_repositories,
)
from exasol.ds.sandbox.lib.ansible.ansible_run_context import (
    AnsibleRunContext,
    default_ansible_run_context,
)


@dataclass
class AnsibleDependencyInstaller:
    ansible_access: AnsibleAccess
    run_context: AnsibleRunContext = field(default_factory=lambda: default_ansible_run_context)
    repositories: tuple[AnsibleRepository, ...] = default_repositories
