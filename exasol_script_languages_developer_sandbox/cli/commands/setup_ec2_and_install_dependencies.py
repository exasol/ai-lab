from typing import Optional

import click

from exasol_script_languages_developer_sandbox.cli.cli import cli
from exasol_script_languages_developer_sandbox.cli.common import add_options
from exasol_script_languages_developer_sandbox.cli.options.aws_options import aws_options
from exasol_script_languages_developer_sandbox.cli.options.logging import logging_options, set_log_level
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol_script_languages_developer_sandbox.lib.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.run_setup_ec2_and_install_dependencies import \
    run_setup_ec2_and_install_dependencies


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@click.option('--ec2-key-file', required=False, type=click.Path(exists=True, file_okay=True, dir_okay=False),
                 default=None, help="The EC2 key-pair-file to use. If not given a temporary key-pair-file will be created.")
@click.option('--ec2-key-name', required=False, type=str,
             default=None, help="The EC2 key-pair-name to use. Only needs to be set together with ec2-key-file.")
def setup_ec2_and_install_dependencies(
            aws_profile: str,
            ec2_key_file: Optional[str],
            ec2_key_name: Optional[str],
            log_level: str):
    """
    Debug command to check setup and installation of an EC-2 instance.
    """
    set_log_level(log_level)
    run_setup_ec2_and_install_dependencies(AwsAccess(aws_profile), ec2_key_file, ec2_key_name, AnsibleAccess())
