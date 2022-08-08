from typing import Tuple

from exasol_script_languages_developer_sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_context_manager import AnsibleContextManager
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_repository import AnsibleRepository, \
    default_repositories
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_run_context import AnsibleRunContext, \
    default_ansible_run_context

from exasol_script_languages_developer_sandbox.lib.host_info import HostInfo


def run_install_dependencies(ansible_access: AnsibleAccess, host_infos: Tuple[HostInfo, ...] = tuple(),
                             ansible_run_context: AnsibleRunContext = default_ansible_run_context,
                             ansible_repositories: Tuple[AnsibleRepository, ...] = default_repositories) -> None:
    """
    Runs ansible installation. The ansible working dir is created dynamically and removed afterwards.
    Any hosts, given by variable host_infos, are added to the ansible inventory in the dynamic working directory.
    All ansible repositories, given by variable ansible_repositories,
    are copied as flat copy to the dynamic working copy, too.
    The playbook is indicated by variable ansible_run_context, which also might contain additional ansible variables.
    """
    # TODO: Awaiting release 5.0.0 of slc!!!
    # Check https://github.com/exasol/script-languages-developer-sandbox/issues/12)
    # new_extra_vars = {"slc_version": meta.version("exasol_script_languages_release")}
    new_extra_vars = {"slc_version": "master"}
    if ansible_run_context.extra_vars is not None:
        new_extra_vars.update(ansible_run_context.extra_vars)
    new_ansible_run_context = AnsibleRunContext(ansible_run_context.playbook, new_extra_vars)
    with AnsibleContextManager(ansible_access, ansible_repositories) as ansible_runner:
        ansible_runner.run(new_ansible_run_context, host_infos=host_infos)
