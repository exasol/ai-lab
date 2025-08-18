import os
from typing import Optional, Tuple

import click

from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.aws_options import aws_options
from exasol.ds.sandbox.cli.options.ec2_options import ec2_instance_options, ec2_key_options
from exasol.ds.sandbox.cli.options.id_options import id_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.cli.options.vm_options import vm_options
from exasol.ds.sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib.config import default_config_object
from exasol.ds.sandbox.lib.run_create_vm import run_create_vm


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@add_options(ec2_instance_options)
@add_options(ec2_key_options)
@click.option('--default-password', required=True, type=str, metavar="PASSWORD",
              help="The new (temporary) default password.")
@click.option('--make-ami-public/--no-make-ami-public', default=False,
              help="If true, the newly created AMI will be publicly available.")
@add_options(vm_options)
@add_options(id_options)
def create_vm(
    aws_profile: str,
    ec2_instance_type: str,
    ec2_source_ami: Optional[str],
    ec2_key_file: Optional[str],
    ec2_key_name: Optional[str],
    default_password: str,
    vm_image_format: Tuple[str, ...],
    no_vm: bool,
    asset_id: str,
    make_ami_public: bool,
    log_level: str,
):
    """
    Creates a new VM image from a fresh EC-2 Ubuntu AMI.
    """
    current_vm_image_formats = tuple() if no_vm else vm_image_format
    set_log_level(log_level)
    run_create_vm(
        aws_access=AwsAccess(aws_profile),
        ec2_instance_type=ec2_instance_type,
        ec2_source_ami=ec2_source_ami,
        ec2_key_file=ec2_key_file,
        ec2_key_name=ec2_key_name,
        ansible_access=AnsibleAccess(),
        default_password=default_password,
        vm_image_formats=current_vm_image_formats,
        asset_id=AssetId(asset_id),
        configuration=default_config_object,
        user_name=os.getenv("AWS_USER_NAME"),
        make_ami_public=make_ami_public,
    )
