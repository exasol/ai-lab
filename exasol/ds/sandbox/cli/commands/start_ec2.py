from typing import Optional

import click
from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.aws_options import aws_options
from exasol.ds.sandbox.cli.options.ec2_options import (ec2_instance_options,
                                                       ec2_key_options)
from exasol.ds.sandbox.cli.options.id_options import id_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol.ds.sandbox.lib.ansible.dependency_installer import \
    AnsibleDependencyInstaller
from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import default_config_object
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib.setup_ec2.run_setup_ec2 import run_setup_ec2


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@add_options(ec2_instance_options)
@add_options(ec2_key_options)
@add_options(id_options)
@click.option(
    "--install-dependencies", is_flag=True,
    help="Additionally install dependencies via ansible.",
)
def start_ec2(
    aws_profile: str,
    ec2_instance_type: str,
    ec2_source_ami: Optional[str],
    ec2_key_file: Optional[str],
    ec2_key_name: Optional[str],
    asset_id: str,
    log_level: str,
    install_dependencies: bool,
):
    """
    Developer command starting an EC-2 instance, optionally installing
    dependencies via ansible.
    """
    set_log_level(log_level)
    dependency_installer = (
        AnsibleDependencyInstaller(AnsibleAccess())
        if install_dependencies else None
    )
    run_setup_ec2(
        aws_access=AwsAccess(aws_profile),
        ec2_instance_type=ec2_instance_type,
        ec2_source_ami=ec2_source_ami,
        ec2_key_file=ec2_key_file,
        ec2_key_name=ec2_key_name,
        asset_id=AssetId(asset_id),
        configuration=default_config_object,
        dependency_installer=dependency_installer,
    )
