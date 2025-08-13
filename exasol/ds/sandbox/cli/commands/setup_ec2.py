from typing import Optional

from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.cli.common import add_options
from exasol.ds.sandbox.cli.options.aws_options import aws_options
from exasol.ds.sandbox.cli.options.ec2_options import ec2_instance_options, ec2_key_options
from exasol.ds.sandbox.cli.options.id_options import id_options
from exasol.ds.sandbox.cli.options.logging import logging_options
from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import default_config_object
from exasol.ds.sandbox.lib.logging import set_log_level
from exasol.ds.sandbox.lib.setup_ec2.run_setup_ec2 import run_setup_ec2


@cli.command()
@add_options(aws_options)
@add_options(logging_options)
@add_options(ec2_key_options)
@add_options(ec2_instance_options)
@add_options(id_options)
def setup_ec2(
    aws_profile: str,
    ec2_key_file: Optional[str],
    ec2_key_name: Optional[str],
    ec2_instance_type: str,
    asset_id: str,
    log_level: str,
):
    """
    Debug command to test setup of an EC-2 instance.
    """
    set_log_level(log_level)
    run_setup_ec2(
        aws_access=AwsAccess(aws_profile),
        ec2_key_file=ec2_key_file,
        ec2_key_name=ec2_key_name,
        asset_id=AssetId(asset_id),
        configuration=default_config_object,
        ec2_instance_type=ec2_instance_type,
    )
