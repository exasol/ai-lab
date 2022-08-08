import pathlib
from collections import namedtuple
from typing import Callable, Optional

import pytest

from exasol_script_languages_developer_sandbox.lib.ansible.ansible_repository import default_repositories, \
    AnsibleResourceRepository
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_run_context import AnsibleRunContext, \
    default_ansible_run_context
from exasol_script_languages_developer_sandbox.lib.host_info import HostInfo
from exasol_script_languages_developer_sandbox.lib.run_install_dependencies import run_install_dependencies

import test.ansible
import test.ansible_conflict


class AnsibleTestAccess:

    def __init__(self, delegate: Optional[Callable[[str, AnsibleRunContext], None]] = None):
        self.call_arguments = None
        self.arguments = namedtuple("Arguments", "private_data_dir run_ctx")
        self.delegate = delegate

    def run(self, private_data_dir: str, run_ctx: AnsibleRunContext, printer: Callable[[str], None]):

        self.call_arguments = self.arguments(private_data_dir, run_ctx)
        if self.delegate is not None:
            self.delegate(private_data_dir, run_ctx)


def test_run_ansible_default_values():
    """
    Test which executes run_install_dependencies with default values (default playbook and default ansible variables)
    """
    ansible_access = AnsibleTestAccess()
    run_install_dependencies(ansible_access)
    expected_ansible_run_context = AnsibleRunContext(playbook="slc_setup.yml", extra_vars={"slc_version": "master"})
    assert ansible_access.call_arguments.private_data_dir.startswith("/tmp")
    assert ansible_access.call_arguments.run_ctx == expected_ansible_run_context


def test_run_ansible_custom_playbook():
    """
    Test which executes run_install_dependencies with default ansible variable, but a custom playbook
    """
    ansible_access = AnsibleTestAccess()
    ansible_run_context = AnsibleRunContext(playbook="my_playbook.yml", extra_vars=dict())
    run_install_dependencies(ansible_access, host_infos=tuple(), ansible_run_context=ansible_run_context)

    expected_ansible_run_context = AnsibleRunContext(playbook="my_playbook.yml", extra_vars={"slc_version": "master"})
    assert ansible_access.call_arguments.private_data_dir.startswith("/tmp")
    assert ansible_access.call_arguments.run_ctx == expected_ansible_run_context


def test_run_ansible_custom_variables():
    """
    Test which executes run_install_dependencies with custam playbook and custom ansible variables
    """
    ansible_access = AnsibleTestAccess()
    ansible_run_context = AnsibleRunContext(playbook="my_playbook.yml", extra_vars={"my_var": True})
    run_install_dependencies(ansible_access, host_infos=tuple(), ansible_run_context=ansible_run_context)

    expected_ansible_run_context = AnsibleRunContext(playbook="my_playbook.yml",
                                                     extra_vars={"slc_version": "master", "my_var": True})
    assert ansible_access.call_arguments.private_data_dir.startswith("/tmp")
    assert ansible_access.call_arguments.run_ctx == expected_ansible_run_context


def test_run_ansible_check_inventory_empty_host():
    empty_inventory = "[ec2]\n\n"

    def check_inventory(work_dir: str, ansible_run_context: AnsibleRunContext):
        with open(f"{work_dir}/inventory", ) as f:
            inventory_content = f.read()
        assert inventory_content == empty_inventory

    run_install_dependencies(AnsibleTestAccess(check_inventory))


def test_run_ansible_check_inventory_custom_host():
    custom_inventory = "[ec2]\n\nmy_host ansible_ssh_private_key_file=my_key\n\n"

    def check_inventory(work_dir: str, ansible_run_context: AnsibleRunContext):
        with open(f"{work_dir}/inventory", ) as f:
            inventory_content = f.read()
        assert inventory_content == custom_inventory

    run_install_dependencies(AnsibleTestAccess(check_inventory), host_infos=(HostInfo("my_host", "my_key"),))


def test_run_ansible_check_default_repository():
    """
    Test that default repository is being copied correctly.
    For simplicity, we check only if:
     1. the playbook of the default repository exists on target.
     2. One of the role files exists (Validate deep copy)
    """
    def check_playbook(work_dir: str, ansible_run_context: AnsibleRunContext):
        p = pathlib.Path(work_dir) / "slc_setup.yml"
        assert p.exists()
        p = pathlib.Path(work_dir) / "roles" / "script_languages" / "tasks" / "main.yml"
        assert p.exists()

    run_install_dependencies(AnsibleTestAccess(check_playbook))


def test_run_ansible_check_multiple_repositories():
    """
    Test that multiple repositories are being copied correctly.
    For simplicity, we check only if the playbook of the repositories exists on target.
    """
    def check_playbooks(work_dir: str, ansible_run_context: AnsibleRunContext):
        p = pathlib.Path(f"{work_dir}/slc_setup.yml")
        assert p.exists()
        p = pathlib.Path(f"{work_dir}/slc_setup_test.yml")
        assert p.exists()

    test_repositories = default_repositories + (AnsibleResourceRepository(test.ansible),)
    run_install_dependencies(AnsibleTestAccess(check_playbooks), host_infos=tuple(),
                             ansible_run_context=default_ansible_run_context, ansible_repositories=test_repositories)


def test_run_ansible_check_multiple_repositories_with_same_content_causes_exception():
    """
    Test that multiple repositories containing same files raises an runtime exception.
    """
    test_repositories = default_repositories + (AnsibleResourceRepository(test.ansible_conflict),)
    with pytest.raises(RuntimeError):
        run_install_dependencies(AnsibleTestAccess(), host_infos=tuple(),
                                 ansible_run_context=default_ansible_run_context,
                                 ansible_repositories=test_repositories)
