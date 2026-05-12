from pathlib import Path
from unittest.mock import Mock

import exasol.ansible as ansible
import pytest

from exasol.ds.sandbox.cli.commands.create_vm import create_vm
from exasol.ds.sandbox.cli.commands.install_dependencies import install_dependencies
from exasol.ds.sandbox.cli.commands.reset_password import reset_password
from exasol.ds.sandbox.cli.commands.start_ec2 import start_ec2
from exasol.ds.sandbox.lib.config import default_config_object
from exasol.ds.sandbox.lib.setup_ec2.ansible_execution import AnsibleDependencyInstaller
from test.unit.cli import CliRunner


@pytest.fixture
def private_key(tmp_path) -> Path:
    key = tmp_path / "key.pem"
    key.write_text("private-key")
    return key


def test_install_dependencies(monkeypatch, private_key):
    mock = Mock()
    set_log_level = Mock()
    monkeypatch.setitem(
        install_dependencies.callback.__globals__,
        "run_install_dependencies",
        mock,
    )
    monkeypatch.setitem(
        install_dependencies.callback.__globals__,
        "set_log_level",
        set_log_level,
    )

    cli = CliRunner(install_dependencies)
    cli.run(
        "--host-name",
        "host",
        "--ssh-private-key",
        str(private_key),
        "--log-level",
        "debug",
    )

    assert cli.succeeded
    assert set_log_level.call_args.args == ("debug",)
    assert mock.call_args.args == (
        default_config_object,
        (ansible.Host("host", str(private_key)),),
    )


def test_reset_password(monkeypatch, private_key):
    run_reset_password = Mock()
    set_log_level = Mock()
    monkeypatch.setitem(
        reset_password.callback.__globals__,
        "run_reset_password",
        run_reset_password,
    )
    monkeypatch.setitem(
        reset_password.callback.__globals__,
        "set_log_level",
        set_log_level,
    )

    cli = CliRunner(reset_password)
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
    assert set_log_level.call_args.args == ("debug",)
    assert run_reset_password.call_args.args == (
        "secret",
        (ansible.Host("host", str(private_key)),),
    )


def test_start_ec2_command(
    monkeypatch,
    private_key,
):
    aws_access = Mock()
    aws_access_factory = Mock(return_value=aws_access)
    run_setup_ec2 = Mock()
    set_log_level = Mock()
    monkeypatch.setitem(
        start_ec2.callback.__globals__,
        "run_setup_ec2",
        run_setup_ec2,
    )
    monkeypatch.setitem(
        start_ec2.callback.__globals__,
        "AwsAccess",
        aws_access_factory,
    )
    monkeypatch.setitem(
        start_ec2.callback.__globals__,
        "set_log_level",
        set_log_level,
    )

    cli = CliRunner(start_ec2)
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
    assert set_log_level.call_args.args == ("debug",)
    assert aws_access_factory.call_args.args == ("profile",)
    actual = run_setup_ec2.call_args.kwargs
    assert actual["aws_access"] == aws_access
    assert actual["ec2_instance_type"] == "m5.large"
    assert actual["ec2_source_ami"] == "ami-123"
    assert actual["ec2_key_file"] == str(private_key)
    assert actual["ec2_key_name"] == "key-name"
    assert actual["asset_id"].tag_value == "asset-id"
    assert actual["configuration"] == default_config_object
    assert isinstance(actual["dependency_installer"], AnsibleDependencyInstaller)


def test_create_vm_command(
    monkeypatch,
    private_key,
):
    aws_access = Mock()
    aws_access_factory = Mock(return_value=aws_access)
    run_create_vm = Mock()
    set_log_level = Mock()
    monkeypatch.setitem(
        create_vm.callback.__globals__,
        "run_create_vm",
        run_create_vm,
    )
    monkeypatch.setitem(
        create_vm.callback.__globals__,
        "AwsAccess",
        aws_access_factory,
    )
    monkeypatch.setitem(
        create_vm.callback.__globals__,
        "set_log_level",
        set_log_level,
    )

    cli = CliRunner(create_vm, env={"AWS_USER_NAME": "user-name"})
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
    assert set_log_level.call_args.args == ("debug",)
    assert aws_access_factory.call_args.args == ("profile",)
    actual = run_create_vm.call_args.kwargs
    assert actual["aws_access"] == aws_access
    assert actual["ec2_instance_type"] == "m5.large"
    assert actual["ec2_source_ami"] == "ami-123"
    assert actual["ec2_key_file"] == str(private_key)
    assert actual["ec2_key_name"] == "key-name"
    assert actual["default_password"] == "secret"
    assert actual["vm_image_formats"] == ("RAW", "VHD")
    assert actual["asset_id"].tag_value == "asset-id"
    assert actual["configuration"] == default_config_object
    assert actual["user_name"] == "user-name"
    assert actual["make_ami_public"] is True
    assert "ansible_access" not in actual
