from typing import Dict

from exasol_script_languages_developer_sandbox.lib.aws_access.ami import Ami
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess


def find_source_ami(aws_access: AwsAccess, filters: Dict[str, str]) -> Ami:
    amis = aws_access.list_amis(filters=[{"Name": key, "Values": [value]} for key, value in filters.items()])
    latest_ami = max(amis, key=lambda ami: ami.creation_date)
    return latest_ami
