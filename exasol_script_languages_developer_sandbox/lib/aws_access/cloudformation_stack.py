from datetime import datetime
from typing import List, Dict, Optional

from exasol_script_languages_developer_sandbox.lib.aws_access.common import get_value_safe


class CloudformationStack:
    """
    Simplifies access to objects returned from:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks
    """

    def __init__(self, aws_object):
        self._aws_object = aws_object

    @property
    def id(self) -> str:
        return self._aws_object["StackId"]

    @property
    def description(self) -> str:
        return get_value_safe("Description", self._aws_object)

    @property
    def name(self) -> str:
        return self._aws_object["StackName"]

    @property
    def state(self) -> str:
        return self._aws_object["State"]

    @property
    def creation_time(self) -> datetime:
        return self._aws_object["CreationTime"]

    @property
    def status(self) -> str:
        return self._aws_object["StackStatus"]

    @property
    def tags(self) -> Optional[List[Dict[str, str]]]:
        if "Tags" in self._aws_object:
            return self._aws_object["Tags"]

