from typing import Optional, List, Dict

from exasol_script_languages_developer_sandbox.lib.aws_access.common import get_value_safe


class ExportImageTask:
    """
    Simplifies access to objects returned from:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_export_image_tasks
    """

    def __init__(self, aws_object):
        self._aws_object = aws_object

    @property
    def id(self) -> str:
        return self._aws_object["ExportImageTaskId"]

    @property
    def description(self) -> str:
        return self._aws_object["Description"]

    @property
    def status(self) -> str:
        return self._aws_object["Status"]

    @property
    def status_message(self) -> str:
        return get_value_safe("StatusMessage", self._aws_object)

    @property
    def progress(self) -> str:
        return get_value_safe("Progress", self._aws_object)

    @property
    def s3_bucket(self):
        return self._aws_object["S3ExportLocation"]["S3Bucket"]

    @property
    def s3_prefix(self) -> str:
        return self._aws_object["S3ExportLocation"]["S3Prefix"]

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def is_completed(self) -> bool:
        return self.status == "completed"

    @property
    def tags(self) -> Optional[List[Dict[str, str]]]:
        if "Tags" in self._aws_object:
            return self._aws_object["Tags"]
