from importlib import import_module
from pathlib import Path
from unittest.mock import (
    Mock,
    call,
)

import exasol.ansible as ansible
import exasol.ds.sandbox.cli.commands as commands
import pytest

from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.config import default_config_object
from exasol.ds.sandbox.lib.setup_ec2.ansible_execution import AnsibleDependencyInstaller
from test.unit.cli import CliRunner


def command_module(name: str):
    return import_module(f".{name}", commands.__name__)


class AssetIdMatcher:
    def __init__(self, tag_value: str):
        self.tag_value = tag_value

    def __eq__(self, other):
        return isinstance(other, AssetId) and other.tag_value == self.tag_value

    def __repr__(self):
        return f"AssetIdMatcher({self.tag_value!r})"


@pytest.fixture
def private_key(tmp_path) -> Path:
    key = tmp_path / "key.pem"
    key.write_text("private-key")
    return key


def test_install_dependencies(monkeypatch, private_key):
    module = command_module("install_dependencies")
    run_install_dependencies = Mock()
    set_log_level = Mock()
    monkeypatch.setattr(
        module,
        "run_install_dependencies",
        run_install_dependencies,
    )
    monkeypatch.setattr(module, "set_log_level", set_log_level)

    cli = CliRunner(module.install_dependencies)
    cli.run(
        "--host-name",
        "host",
        "--ssh-private-key",
        str(private_key),
        "--log-level",
        "debug",
    )

    assert cli.succeeded
    assert set_log_level.call_args == call("debug")
    assert run_install_dependencies.call_args == call(
        default_config_object,
        (ansible.Host("host", str(private_key)),),
    )


def test_reset_password(monkeypatch, private_key):
    module = command_module("reset_password")
    run_reset_password = Mock()
    set_log_level = Mock()
    monkeypatch.setattr(module, "run_reset_password", run_reset_password)
    monkeypatch.setattr(module, "set_log_level", set_log_level)

    cli = CliRunner(module.reset_password)
    cli.run(
        "--host-name",
        "host",
        "--ssh-private-key",
        str(private_key),
        "--default-password",
        "secret",
        "--log-level",
        "debug",
    )

    assert cli.succeeded
    assert set_log_level.call_args == call("debug")
    assert run_reset_password.call_args == call(
        "secret",
        (ansible.Host("host", str(private_key)),),
    )


def test_start_ec2_command(
    monkeypatch,
    private_key,
):
    module = command_module("start_ec2")
    aws_access = Mock()
    aws_access_factory = Mock(return_value=aws_access)
    run_setup_ec2 = Mock()
    set_log_level = Mock()
    monkeypatch.setattr(module, "run_setup_ec2", run_setup_ec2)
    monkeypatch.setattr(module, "AwsAccess", aws_access_factory)
    monkeypatch.setattr(module, "set_log_level", set_log_level)

    cli = CliRunner(module.start_ec2)
    cli.run(
        "--aws-profile",
        "profile",
        "--ec2-instance-type",
        "m5.large",
        "--ec2-source-ami",
        "ami-123",
        "--ec2-key-file",
        str(private_key),
        "--ec2-key-name",
        "key-name",
        "--asset-id",
        "asset-id",
        "--log-level",
        "debug",
        "--install-dependencies",
    )

    assert cli.succeeded
    assert set_log_level.call_args == call("debug")
    assert aws_access_factory.call_args == call("profile")
    assert run_setup_ec2.call_args == call(
        aws_access=aws_access,
        ec2_instance_type="m5.large",
        ec2_source_ami="ami-123",
        ec2_key_file=str(private_key),
        ec2_key_name="key-name",
        asset_id=AssetIdMatcher("asset-id"),
        configuration=default_config_object,
        dependency_installer=AnsibleDependencyInstaller(),
    )


def test_create_vm_command(
    monkeypatch,
    private_key,
):
    module = command_module("create_vm")
    aws_access = Mock()
    aws_access_factory = Mock(return_value=aws_access)
    run_create_vm = Mock()
    set_log_level = Mock()
    monkeypatch.setattr(module, "run_create_vm", run_create_vm)
    monkeypatch.setattr(module, "AwsAccess", aws_access_factory)
    monkeypatch.setattr(module, "set_log_level", set_log_level)

    cli = CliRunner(module.create_vm, env={"AWS_USER_NAME": "user-name"})
    cli.run(
        "--aws-profile",
        "profile",
        "--ec2-instance-type",
        "m5.large",
        "--ec2-source-ami",
        "ami-123",
        "--ec2-key-file",
        str(private_key),
        "--ec2-key-name",
        "key-name",
        "--default-password",
        "secret",
        "--vm-image-format",
        "RAW",
        "--vm-image-format",
        "VHD",
        "--asset-id",
        "asset-id",
        "--make-ami-public",
        "--log-level",
        "debug",
    )

    assert cli.succeeded
    assert set_log_level.call_args == call("debug")
    assert aws_access_factory.call_args == call("profile")
    assert run_create_vm.call_args == call(
        aws_access=aws_access,
        ec2_instance_type="m5.large",
        ec2_source_ami="ami-123",
        ec2_key_file=str(private_key),
        ec2_key_name="key-name",
        default_password="secret",
        vm_image_formats=("RAW", "VHD"),
        asset_id=AssetIdMatcher("asset-id"),
        configuration=default_config_object,
        user_name="user-name",
        make_ami_public=True,
    )
