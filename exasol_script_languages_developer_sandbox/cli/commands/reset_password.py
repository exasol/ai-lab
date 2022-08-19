import click

from exasol_script_languages_developer_sandbox.cli.cli import cli
from exasol_script_languages_developer_sandbox.cli.common import add_options
from exasol_script_languages_developer_sandbox.cli.options.ec2_options import ec2_host_options
from exasol_script_languages_developer_sandbox.cli.options.logging import logging_options, set_log_level
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol_script_languages_developer_sandbox.lib.setup_ec2.host_info import HostInfo
from exasol_script_languages_developer_sandbox.lib.setup_ec2.run_reset_password import run_reset_password


@cli.command()
@add_options(logging_options)
@add_options(ec2_host_options)
@click.option('--default-password', required=True, type=str,
              help="The new (temporary) default password.")
def reset_password(
            host_name: str,
            ssh_private_key: str,
            default_password: str,
            log_level: str):
    """
    Debug command to reset password on a remote EC-2-instance via ansible.
    """
    set_log_level(log_level)
    run_reset_password(AnsibleAccess(), default_password, (HostInfo(host_name, ssh_private_key),))
