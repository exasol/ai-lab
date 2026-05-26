import click

import exasol.ansible as ansible
import exasol.ds.sandbox.lib.cli_api as cli_api
from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.ec2_options import ec2_host_options
from exasol.ds.sandbox.cli.options.logging import logging_options


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
    cli_api.set_log_level(log_level)
    cli_api.run_reset_password(default_password, (ansible.Host(host_name, ssh_private_key),))
