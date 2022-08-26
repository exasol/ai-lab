from typing import Optional, Tuple

import click

from exasol_script_languages_developer_sandbox.cli.cli import cli
from exasol_script_languages_developer_sandbox.cli.common import add_options
from exasol_script_languages_developer_sandbox.cli.options.aws_options import aws_options
from exasol_script_languages_developer_sandbox.cli.options.ec2_options import ec2_key_options
from exasol_script_languages_developer_sandbox.cli.options.id_options import id_options
from exasol_script_languages_developer_sandbox.cli.options.logging import logging_options
from exasol_script_languages_developer_sandbox.cli.options.vm_options import vm_options
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol_script_languages_developer_sandbox.lib.asset_id import AssetId
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.logging import set_log_level
from exasol_script_languages_developer_sandbox.lib.run_create_vm import run_create_vm


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@add_options(ec2_key_options)
@click.option('--default-password', required=True, type=str,
              help="The new (temporary) default password.")
@add_options(vm_options)
@add_options(id_options)
def create_vm(
            aws_profile: str,
            ec2_key_file: Optional[str],
            ec2_key_name: Optional[str],
            default_password: str,
            vm_image_format: Tuple[str, ...],
            no_vm: bool,
            asset_id: str,
            log_level: str):
    """
    Creates a new VM image from a fresg EC-2 Ubuntu AMI.
    """
    current_vm_image_formats = tuple() if no_vm else vm_image_format
    set_log_level(log_level)
    run_create_vm(AwsAccess(aws_profile), ec2_key_file, ec2_key_name,
                  AnsibleAccess(), default_password, current_vm_image_formats, AssetId(asset_id))
