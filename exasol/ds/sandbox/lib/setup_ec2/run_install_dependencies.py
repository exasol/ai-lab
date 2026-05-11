from typing import Any

import exasol.ansible as ansible

from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.setup_ec2.ansible_execution import (
    DEFAULT_REPOSITORIES,
    default_install_dependencies_playbook,
    to_ansible_hosts,
)


def run_install_dependencies(
    configuration: ConfigObject,
    host_infos: tuple[Any, ...] = tuple(),
    playbook: ansible.Playbook | None = None,
    ansible_repositories: tuple[ansible.Repository, ...] = DEFAULT_REPOSITORIES,
    retrieve_facts_from: str | None = None,
) -> dict[str, Any]:
    """
    Runs ansible installation. The ansible working dir is created dynamically and removed afterwards.
    Any hosts, given by variable host_infos, are added to the ansible inventory in the dynamic working directory.
    All ansible repositories, given by variable ansible_repositories,
    are copied as flat copy to the dynamic working copy, too.
    The playbook parameter indicates which playbook to run and can contain additional Ansible variables.
    """
    new_extra_vars = {
        "ai_lab_version": configuration.ai_lab_version,
        "work_in_progress_notebooks": False
    }
    playbook = playbook or default_install_dependencies_playbook()
    new_extra_vars.update(playbook.vars)
    playbook = ansible.Playbook(playbook.file, new_extra_vars)
    facts_host = retrieve_facts_from
    if facts_host is None:
        facts_host = playbook.vars.get("docker_container", "")
    runner = ansible.Runner(ansible_repositories)
    return runner.run(
        playbook,
        hosts=to_ansible_hosts(host_infos),
        retrieve_facts_from=facts_host,
    )
