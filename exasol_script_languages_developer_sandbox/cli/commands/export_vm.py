from typing import Tuple

import click

from exasol_script_languages_developer_sandbox.cli.cli import cli
from exasol_script_languages_developer_sandbox.cli.common import add_options
from exasol_script_languages_developer_sandbox.cli.options.aws_options import aws_options
from exasol_script_languages_developer_sandbox.cli.options.id_options import id_options
from exasol_script_languages_developer_sandbox.cli.options.logging import logging_options
from exasol_script_languages_developer_sandbox.cli.options.vm_options import vm_options
from exasol_script_languages_developer_sandbox.lib.asset_id import AssetId
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.export_vm.run_export_vm import run_export_vm
from exasol_script_languages_developer_sandbox.lib.logging import set_log_level


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@click.option('--stack-name', required=True,
              type=str,
              help="Existing cloudformation stack containing the EC2 instance.")
@add_options(vm_options)
@add_options(id_options)
def export_vm(
            aws_profile: str,
            stack_name: str,
            vm_image_format: Tuple[str, ...],
            no_vm: bool,
            asset_id: str,
            log_level: str):
    """
    Debug command which creates a new VM image from a running EC2-Instance.
    """
    current_vm_image_formats = tuple() if no_vm else vm_image_format
    set_log_level(log_level)
    run_export_vm(AwsAccess(aws_profile), stack_name, current_vm_image_formats, AssetId(asset_id))
