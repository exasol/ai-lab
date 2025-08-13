from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.ec2_options import ec2_host_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol.ds.sandbox.lib.config import default_config_object
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib.setup_ec2.host_info import HostInfo
from exasol.ds.sandbox.lib.setup_ec2.run_install_dependencies import run_install_dependencies


@cli.command()
@add_options(logging_options)
@add_options(ec2_host_options)
def install_dependencies(
            host_name: str,
            ssh_private_key: str,
            log_level: str):
    """
    Debug command to ansible-installation onto an EC-2 instance.
    """
    set_log_level(log_level)
    run_install_dependencies(
        AnsibleAccess(),
        default_config_object,
        (HostInfo(host_name, ssh_private_key),),
    )
