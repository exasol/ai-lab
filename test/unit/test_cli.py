from pathlib import Path
from unittest.mock import (
    Mock,
    call,
    patch,
)

import exasol.ansible as ansible
import exasol.ds.sandbox.cli.commands as commands
import exasol.ds.sandbox.lib.cli_api as cli_api
import pytest

from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.config import default_config_object
from exasol.ds.sandbox.lib.setup_ec2.ansible_execution import AnsibleDependencyInstaller
from test.unit.cli import CliRunner


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


@patch.object(cli_api, "set_log_level")
@patch.object(cli_api, "run_install_dependencies")
def test_install_dependencies(
    mock_run_install_dependencies,
    mock_set_log_level,
    private_key,
):
    cli = CliRunner(commands.install_dependencies)
    cli.run(
        "--host-name",
        "host",
        "--ssh-private-key",
        str(private_key),
        "--log-level",
        "debug",
    )

    assert cli.succeeded
    assert mock_set_log_level.call_args == call("debug")
    assert mock_run_install_dependencies.call_args == call(
        default_config_object,
        (ansible.Host("host", str(private_key)),),
    )


@patch.object(cli_api, "set_log_level")
@patch.object(cli_api, "run_reset_password")
def test_reset_password(
    mock_run_reset_password,
    mock_set_log_level,
    private_key,
):
    cli = CliRunner(commands.reset_password)
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
    assert mock_set_log_level.call_args == call("debug")
    assert mock_run_reset_password.call_args == call(
        "secret",
        (ansible.Host("host", str(private_key)),),
    )


@patch.object(cli_api, "set_log_level")
@patch.object(cli_api, "AwsAccess")
@patch.object(cli_api, "run_setup_ec2")
def test_start_ec2_command(
    mock_run_setup_ec2,
    mock_aws_access_factory,
    mock_set_log_level,
    private_key,
):
    aws_access = Mock()
    mock_aws_access_factory.return_value = aws_access

    cli = CliRunner(commands.start_ec2)
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
    assert mock_set_log_level.call_args == call("debug")
    assert mock_aws_access_factory.call_args == call("profile")
    assert mock_run_setup_ec2.call_args == call(
        aws_access=aws_access,
        ec2_instance_type="m5.large",
        ec2_source_ami="ami-123",
        ec2_key_file=str(private_key),
        ec2_key_name="key-name",
        asset_id=AssetIdMatcher("asset-id"),
        configuration=default_config_object,
        dependency_installer=AnsibleDependencyInstaller(),
    )


@patch.object(cli_api, "set_log_level")
@patch.object(cli_api, "AwsAccess")
@patch.object(cli_api, "run_create_vm")
def test_create_vm_command(
    mock_run_create_vm,
    mock_aws_access_factory,
    mock_set_log_level,
    private_key,
):
    aws_access = Mock()
    mock_aws_access_factory.return_value = aws_access

    cli = CliRunner(commands.create_vm, env={"AWS_USER_NAME": "user-name"})
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
    assert mock_set_log_level.call_args == call("debug")
    assert mock_aws_access_factory.call_args == call("profile")
    assert mock_run_create_vm.call_args == call(
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
