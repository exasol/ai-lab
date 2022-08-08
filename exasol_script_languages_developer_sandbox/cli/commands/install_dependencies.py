import click

from exasol_script_languages_developer_sandbox.cli.cli import cli
from exasol_script_languages_developer_sandbox.cli.common import add_options
from exasol_script_languages_developer_sandbox.cli.options.logging import logging_options, set_log_level
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol_script_languages_developer_sandbox.lib.host_info import HostInfo
from exasol_script_languages_developer_sandbox.lib.run_install_dependencies import run_install_dependencies


@cli.command()
@add_options(logging_options)
@click.option('--host-name', required=True, type=str,
              help="The remote hostname on which the setup needs to be executed.")
@click.option('--ssh-private-key', required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False),
              help="The private key file which can be used to login to the server via ssh.")
def install_dependencies(
            host_name: str,
            ssh_private_key: str,
            log_level: str):
    """
    Debug command to ansible-installation onto an EC-2 instance.
    """
    set_log_level(log_level)
    run_install_dependencies(AnsibleAccess(), (HostInfo(host_name, ssh_private_key),))
