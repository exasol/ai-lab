from typing import Any
from unittest.mock import Mock

import exasol.ansible as ansible
import pytest

from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.setup_ec2 import run_install_dependencies as module
from exasol.ds.sandbox.lib.setup_ec2.ansible_execution import DEFAULT_REPOSITORIES
from exasol.ds.sandbox.lib.setup_ec2.host_info import HostInfo
from exasol.ds.sandbox.lib.setup_ec2.run_install_dependencies import run_install_dependencies


class RecordingRunner:
    def __init__(self, result: dict[str, Any]):
        self.result = result
        self.calls = []

    def run(self, playbook: ansible.Playbook, host_infos: tuple[Any, ...]):
        self.calls.append((playbook, host_infos))
        return self.result


class RecordingContext:
    instances = []
    runner_result = {"facts": True}

    def __init__(
        self,
        ansible_access: ansible.Access,
        repositories: tuple[ansible.Repository, ...],
    ):
        self.ansible_access = ansible_access
        self.repositories = repositories
        self.runner = RecordingRunner(self.runner_result)
        self.instances.append(self)

    def __enter__(self) -> RecordingRunner:
        return self.runner

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass


@pytest.fixture
def recording_context(monkeypatch):
    RecordingContext.instances = []
    monkeypatch.setattr(module.ansible, "Context", RecordingContext)
    return RecordingContext


def _extra_vars(config: ConfigObject) -> dict[str, Any]:
    return {
        "ai_lab_version": config.ai_lab_version,
        "work_in_progress_notebooks": False,
    }


def test_run_ansible_default_values(test_config, recording_context):
    ansible_access = Mock()

    result = run_install_dependencies(ansible_access, test_config)

    expected_playbook = ansible.Playbook("ec2_playbook.yml", _extra_vars(test_config))
    context = recording_context.instances[0]
    assert result == recording_context.runner_result
    assert context.ansible_access is ansible_access
    assert context.repositories == DEFAULT_REPOSITORIES
    assert context.runner.calls == [(expected_playbook, tuple())]


def test_run_ansible_custom_playbook(test_config, recording_context):
    ansible_access = Mock()
    playbook = ansible.Playbook("my_playbook.yml")

    run_install_dependencies(
        ansible_access,
        test_config,
        host_infos=tuple(),
        playbook=playbook,
    )

    expected_playbook = ansible.Playbook("my_playbook.yml", _extra_vars(test_config))
    context = recording_context.instances[0]
    assert context.runner.calls == [(expected_playbook, tuple())]


def test_run_ansible_custom_variables(test_config, recording_context):
    ansible_access = Mock()
    playbook = ansible.Playbook("my_playbook.yml", {"my_var": True})

    run_install_dependencies(
        ansible_access,
        test_config,
        host_infos=tuple(),
        playbook=playbook,
    )

    extra_vars = _extra_vars(test_config)
    extra_vars.update({"my_var": True})
    expected_playbook = ansible.Playbook("my_playbook.yml", extra_vars)
    context = recording_context.instances[0]
    assert context.runner.calls == [(expected_playbook, tuple())]


def test_run_ansible_forwards_hosts_and_repositories(test_config, recording_context):
    ansible_access = Mock()
    host_infos = (HostInfo("my_host", "my_key"),)
    repositories = (Mock(),)

    run_install_dependencies(
        ansible_access,
        test_config,
        host_infos=host_infos,
        ansible_repositories=repositories,
    )

    context = recording_context.instances[0]
    assert context.repositories == repositories
    assert context.runner.calls[0][1] == host_infos
