import exasol.ansible as ansible
import exasol.ds.sandbox.lib.cli_api as cli_api
from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.ec2_options import ec2_host_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.lib.config import default_config_object

@cli.command()
@add_options(logging_options)
@add_options(ec2_host_options)
def install_dependencies(
            host_name: str,
            ssh_private_key: str,
            log_level: str):
    """
    Developer command installing dependencies via ansible onto an EC-2 instance.
    """
    cli_api.set_log_level(log_level)
    cli_api.run_install_dependencies(
        default_config_object,
        (ansible.Host(host_name, ssh_private_key),),
    )
