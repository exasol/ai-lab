import logging

from exasol.ds.sandbox.lib.aws_access.ami import Ami
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import ConfigObject


def find_source_ami(aws_access: AwsAccess, filters: dict[str, str]) -> Ami:
    amis = aws_access.list_amis(filters=[{"Name": key, "Values": [value]} for key, value in filters.items()])
    latest_ami = max(amis, key=lambda ami: ami.creation_date)
    return latest_ami


def source_ami_id_with_logging(
    aws_access: AwsAccess,
    filters: dict[str, str],
    logger: logging.Logger,
) -> str:
    ami = find_source_ami(aws_access, filters)
    logger.info(f"Using source ami: '{ami.name}' from {ami.creation_date}")
    return ami.id
