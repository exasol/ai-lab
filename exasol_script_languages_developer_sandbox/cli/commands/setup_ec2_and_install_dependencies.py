from typing import Optional

from exasol_script_languages_developer_sandbox.cli.cli import cli
from exasol_script_languages_developer_sandbox.cli.common import add_options
from exasol_script_languages_developer_sandbox.cli.options.aws_options import aws_options
from exasol_script_languages_developer_sandbox.cli.options.ec2_options import ec2_key_options
from exasol_script_languages_developer_sandbox.cli.options.id_options import id_options
from exasol_script_languages_developer_sandbox.cli.options.logging import logging_options
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol_script_languages_developer_sandbox.lib.asset_id import AssetId
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.logging import set_log_level
from exasol_script_languages_developer_sandbox.lib.config import default_config_object
from exasol_script_languages_developer_sandbox.lib.setup_ec2.run_setup_ec2_and_install_dependencies import \
    run_setup_ec2_and_install_dependencies


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@add_options(ec2_key_options)
@add_options(id_options)
def setup_ec2_and_install_dependencies(
            aws_profile: str,
            ec2_key_file: Optional[str],
            ec2_key_name: Optional[str],
            asset_id: str,
            log_level: str):
    """
    Debug command to check setup and installation of an EC-2 instance.
    """
    set_log_level(log_level)
    run_setup_ec2_and_install_dependencies(AwsAccess(aws_profile), ec2_key_file, ec2_key_name,
                                           AssetId(asset_id), AnsibleAccess(), default_config_object)
