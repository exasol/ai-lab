import importlib
from unittest.mock import Mock

import pytest

from exasol.ds.sandbox.lib.setup_ec2.ansible_execution import AnsibleDependencyInstaller
from test.unit.cli import CliRunner


def _module(name: str):
    return importlib.import_module(f"exasol.ds.sandbox.cli.commands.{name}")


@pytest.fixture
def private_key(tmp_path):
    key = tmp_path / "key.pem"
    key.write_text("private-key")
    return key


def test_install_dependencies_command_passes_configuration_and_host_info(
    mocker,
    private_key,
):
    module = _module("install_dependencies")
    run_install_dependencies = mocker.patch.object(module, "run_install_dependencies")

    cli = CliRunner(module.install_dependencies)
    cli.run("--host-name", "host", "--ssh-private-key", str(private_key))

    assert cli.succeeded
    assert run_install_dependencies.call_count == 1
    assert len(run_install_dependencies.call_args.args) == 2


def test_reset_password_command_passes_password_and_host_info(mocker, private_key):
    module = _module("reset_password")
    run_reset_password = mocker.patch.object(module, "run_reset_password")

    cli = CliRunner(module.reset_password)
    cli.run(
        "--host-name",
        "host",
        "--ssh-private-key",
        str(private_key),
        "--default-password",
        "secret",
    )

    assert cli.succeeded
    assert run_reset_password.call_count == 1
    assert len(run_reset_password.call_args.args) == 2


def test_start_ec2_command_passes_dependency_installer_when_requested(mocker):
    module = _module("start_ec2")
    aws_access = Mock()
    run_setup_ec2 = mocker.patch.object(module, "run_setup_ec2")
    mocker.patch.object(module, "AwsAccess", return_value=aws_access)

    cli = CliRunner(module.start_ec2)
    cli.run("--install-dependencies")

    assert cli.succeeded
    installer = run_setup_ec2.call_args.kwargs["dependency_installer"]
    assert isinstance(installer, AnsibleDependencyInstaller)


def test_create_vm_command_does_not_pass_ansible_internal_state(mocker):
    module = _module("create_vm")
    run_create_vm = mocker.patch.object(module, "run_create_vm")
    mocker.patch.object(module, "AwsAccess", return_value=Mock())

    cli = CliRunner(module.create_vm)
    cli.run("--default-password", "secret")

    assert cli.succeeded
    assert "ansible_access" not in run_create_vm.call_args.kwargs
