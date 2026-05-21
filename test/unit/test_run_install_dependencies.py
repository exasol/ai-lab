from pathlib import Path
from typing import (
    Any,
    Callable,
)
from unittest.mock import (
    Mock,
    call,
)

import exasol.ansible as ansible_runner_wrapper
import exasol.ds.sandbox.runtime.ansible as runtime_ansible
import pytest
import yaml

from exasol.ansible.inventory import INVENTORY_GROUP
from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.setup_ec2 import run_install_dependencies as lib
from exasol.ds.sandbox.lib.setup_ec2.ansible_execution import DEFAULT_REPOSITORIES


RUNTIME_ANSIBLE_DIR = Path(runtime_ansible.__path__[0])


def _extra_vars(config: ConfigObject) -> dict[str, Any]:
    return {
        "ai_lab_version": config.ai_lab_version,
        "work_in_progress_notebooks": False,
    }


def expected_playbook(filename: str, test_config) -> ansible_runner_wrapper.Playbook:
    return ansible_runner_wrapper.Playbook(filename, _extra_vars(test_config))


def expected_call(
    playbook: ansible_runner_wrapper.Playbook,
    hosts=tuple(),
    retrieve_facts_from="",
):
    return call(
        playbook,
        hosts=hosts,
        retrieve_facts_from=retrieve_facts_from,
    )


@pytest.fixture
def mock_ansible_runner(monkeypatch) -> Callable[[Mock], Mock]:
    """
    Return a callable to mock the constructor of ansible.Runner and
    install the specified run method.
    """

    def func(run_method: Mock):
        runner = Mock(run=run_method)
        mock = Mock(return_value=runner)
        monkeypatch.setattr(lib.ansible, "Runner", mock)
        return mock

    return func


@pytest.fixture
def mocked_run_method(mock_ansible_runner):
    run_method = Mock()
    mock_ansible_runner(run_method)
    return run_method


def test_default_values(mock_ansible_runner, test_config):
    fact_cache = {"a": 1}
    run_method = Mock(return_value=fact_cache)
    constructor = mock_ansible_runner(run_method)

    actual = lib.run_install_dependencies(test_config)
    assert actual == fact_cache
    assert constructor.call_args == call(DEFAULT_REPOSITORIES)
    assert run_method.call_args == expected_call(
        expected_playbook("ec2_playbook.yml", test_config)
    )


def test_custom_playbook(test_config, mocked_run_method):
    playbook = ansible_runner_wrapper.Playbook("my_playbook.yml")
    lib.run_install_dependencies(
        test_config,
        host_infos=tuple(),
        playbook=playbook,
    )
    assert mocked_run_method.call_args == expected_call(
        expected_playbook(playbook.file, test_config)
    )


def test_custom_variables(test_config, mocked_run_method):
    playbook = ansible_runner_wrapper.Playbook("my_playbook.yml", {"my_var": True})
    lib.run_install_dependencies(
        test_config,
        host_infos=tuple(),
        playbook=playbook,
    )
    extravars = _extra_vars(test_config) | {"my_var": True}
    assert mocked_run_method.call_args == expected_call(
        ansible_runner_wrapper.Playbook("my_playbook.yml", extravars),
    )


def test_custom_hosts(test_config, mock_ansible_runner):
    run_method = Mock()
    mock = mock_ansible_runner(run_method)
    host_infos = (ansible_runner_wrapper.Host("my_host", "my_key"),)
    repositories = (Mock(),)
    lib.run_install_dependencies(
        test_config,
        host_infos=host_infos,
        ansible_repositories=repositories,
    )
    assert mock.call_args == call(repositories)
    assert run_method.call_args.kwargs["hosts"] == (ansible_runner_wrapper.Host("my_host", "my_key"),)


def test_fact_retrieval(test_config, mocked_run_method):
    """
    This test also verified, that variable "docker_container" is no longer
    used when retrieving the facts.
    """

    docker_var = {"docker_container": "container"}
    playbook = ansible_runner_wrapper.Playbook("my_playbook.yml", docker_var)
    lib.run_install_dependencies(
        test_config,
        host_infos=tuple(),
        playbook=playbook,
        retrieve_facts_from="host",
    )
    extravars = _extra_vars(test_config) | docker_var
    assert mocked_run_method.call_args == expected_call(
        ansible_runner_wrapper.Playbook(playbook.file, extravars),
        retrieve_facts_from = "host",
    )


@pytest.mark.parametrize(
    "playbook",
    [
        "ec2_playbook.yml",
        "reset_password.yml",
    ],
)
def test_ec2_playbooks_target_runner_inventory_group(playbook):
    plays = yaml.safe_load((RUNTIME_ANSIBLE_DIR / playbook).read_text())

    assert plays[0]["hosts"] == INVENTORY_GROUP
