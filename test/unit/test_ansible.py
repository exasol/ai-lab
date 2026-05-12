from typing import Any
from unittest.mock import Mock

import exasol.ansible as ansible
import pytest

from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.setup_ec2 import run_install_dependencies as module
from exasol.ds.sandbox.lib.setup_ec2.ansible_execution import DEFAULT_REPOSITORIES
from exasol.ds.sandbox.lib.setup_ec2.run_install_dependencies import run_install_dependencies


class RecordingRunner:
    instances = []
    runner_result = {"facts": True}

    def __init__(
        self,
        repositories: tuple[ansible.Repository, ...],
    ):
        self.repositories = repositories
        self.calls = []
        self.instances.append(self)

    def run(
        self,
        playbook: ansible.Playbook,
        hosts: tuple[ansible.Host, ...],
        retrieve_facts_from: str,
    ):
        self.calls.append((playbook, hosts, retrieve_facts_from))
        return self.runner_result


@pytest.fixture
def recording_runner(monkeypatch):
    RecordingRunner.instances = []
    monkeypatch.setattr(module.ansible, "Runner", RecordingRunner)
    return RecordingRunner


def _extra_vars(config: ConfigObject) -> dict[str, Any]:
    return {
        "ai_lab_version": config.ai_lab_version,
        "work_in_progress_notebooks": False,
    }


def test_run_ansible_default_values(test_config, recording_runner):
    result = run_install_dependencies(test_config)

    expected_playbook = ansible.Playbook("ec2_playbook.yml", _extra_vars(test_config))
    runner = recording_runner.instances[0]
    assert result == recording_runner.runner_result
    assert runner.repositories == DEFAULT_REPOSITORIES
    assert runner.calls == [(expected_playbook, tuple(), "")]


def test_run_ansible_custom_playbook(test_config, recording_runner):
    playbook = ansible.Playbook("my_playbook.yml")

    run_install_dependencies(
        test_config,
        host_infos=tuple(),
        playbook=playbook,
    )

    expected_playbook = ansible.Playbook("my_playbook.yml", _extra_vars(test_config))
    runner = recording_runner.instances[0]
    assert runner.calls == [(expected_playbook, tuple(), "")]


def test_run_ansible_custom_variables(test_config, recording_runner):
    playbook = ansible.Playbook("my_playbook.yml", {"my_var": True})

    run_install_dependencies(
        test_config,
        host_infos=tuple(),
        playbook=playbook,
    )

    extra_vars = _extra_vars(test_config)
    extra_vars.update({"my_var": True})
    expected_playbook = ansible.Playbook("my_playbook.yml", extra_vars)
    runner = recording_runner.instances[0]
    assert runner.calls == [(expected_playbook, tuple(), "")]


def test_run_ansible_forwards_hosts_and_repositories(test_config, recording_runner):
    host_infos = (ansible.Host("my_host", "my_key"),)
    repositories = (Mock(),)

    run_install_dependencies(
        test_config,
        host_infos=host_infos,
        ansible_repositories=repositories,
    )

    runner = recording_runner.instances[0]
    assert runner.repositories == repositories
    assert runner.calls[0][1] == (ansible.Host("my_host", "my_key"),)


def test_run_ansible_does_not_use_docker_container_for_fact_retrieval(test_config, recording_runner):
    playbook = ansible.Playbook("my_playbook.yml", {"docker_container": "container"})
    host = ansible.Host("host")

    run_install_dependencies(
        test_config,
        host_infos=(host,),
        playbook=playbook,
        retrieve_facts_from=host.name,
    )

    runner = recording_runner.instances[0]
    assert runner.calls[0][2] == "host"
