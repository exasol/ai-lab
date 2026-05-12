from typing import Any

import exasol.ansible as ansible

from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.setup_ec2.ansible_execution import (
    DEFAULT_REPOSITORIES,
    DEFAULT_INSTALL_DEPENDENCIES_PLAYBOOK,
)


def run_install_dependencies(
    configuration: ConfigObject,
    host_infos: tuple[ansible.Host, ...] = tuple(),
    playbook: ansible.Playbook = DEFAULT_INSTALL_DEPENDENCIES_PLAYBOOK,
    ansible_repositories: tuple[ansible.Repository, ...] = DEFAULT_REPOSITORIES,
    retrieve_facts_from: str = "",
) -> dict[str, Any]:
    """
    Runs ansible installation. The ansible working dir is created dynamically and removed afterwards.
    Any hosts, given by variable host_infos, are added to the ansible inventory in the dynamic working directory.
    All ansible repositories, given by variable ansible_repositories,
    are copied as flat copy to the dynamic working copy, too.
    The playbook parameter indicates which playbook to run and can contain additional Ansible variables.
    """
    extra_vars = {
        "ai_lab_version": configuration.ai_lab_version,
        "work_in_progress_notebooks": False
    }
    extra_vars.update(playbook.vars)
    enhanced_playbook = ansible.Playbook(playbook.file, extra_vars)
    runner = ansible.Runner(ansible_repositories)
    return runner.run(
        enhanced_playbook,
        hosts=host_infos,
        retrieve_facts_from=retrieve_facts_from,
    )
