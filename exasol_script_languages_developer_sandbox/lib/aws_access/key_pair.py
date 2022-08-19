from datetime import datetime
from typing import Optional, List, Dict


class KeyPair:
    """
    Simplifies access to objects returned from:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_key_pairs
    """

    def __init__(self, aws_object):
        self._aws_object = aws_object

    @property
    def id(self) -> str:
        return self._aws_object["KeyPairId"]

    @property
    def created_time(self) -> datetime:
        return self._aws_object["CreateTime"]

    @property
    def key_name(self) -> str:
        return self._aws_object["KeyName"]

    @property
    def tags(self) -> Optional[List[Dict[str, str]]]:
        if "Tags" in self._aws_object:
            return self._aws_object["Tags"]
