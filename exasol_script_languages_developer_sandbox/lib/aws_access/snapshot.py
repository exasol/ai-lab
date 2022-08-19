from datetime import datetime
from typing import Optional, List, Dict

from exasol_script_languages_developer_sandbox.lib.aws_access.common import get_value_safe


class Snapshot:
    """
    Simplifies access to objects returned from:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_snapshots
    """

    def __init__(self, aws_object):
        self._aws_object = aws_object

    @property
    def id(self) -> str:
        return self._aws_object["SnapshotId"]

    @property
    def description(self) -> str:
        return get_value_safe("Description", self._aws_object)

    @property
    def state(self) -> str:
        return get_value_safe("State", self._aws_object)

    @property
    def progress(self) -> str:
        return get_value_safe("Progress", self._aws_object)

    @property
    def volume_id(self) -> str:
        return self._aws_object["VolumeId"]

    @property
    def start_time(self) -> datetime:
        return self._aws_object["StartTime"]

    @property
    def tags(self) -> Optional[List[Dict[str, str]]]:
        if "Tags" in self._aws_object:
            return self._aws_object["Tags"]
