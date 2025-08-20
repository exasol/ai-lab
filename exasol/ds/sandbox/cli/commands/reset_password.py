import click

from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.ec2_options import ec2_host_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib.setup_ec2.host_info import HostInfo
from exasol.ds.sandbox.lib.setup_ec2.run_reset_password import run_reset_password


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
    Developer command resetting the password on a remote EC-2-instance via
    Ansible.
    """
    set_log_level(log_level)
    run_reset_password(AnsibleAccess(), default_password, (HostInfo(host_name, ssh_private_key),))
