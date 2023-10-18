from typing import Optional, List, Dict


class Ami:
    """
    Simplifies access to objects returned from:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_images
    """

    def __init__(self, aws_object):
        self._aws_object = aws_object

    @property
    def id(self) -> str:
        return self._aws_object["ImageId"]

    @property
    def description(self) -> str:
        return self._aws_object["Description"]

    @property
    def state(self) -> str:
        return self._aws_object["State"]

    @property
    def name(self) -> str:
        return self._aws_object["Name"]

    @property
    def is_pending(self) -> bool:
        return self.state == "pending"

    @property
    def is_available(self) -> bool:
        return self.state == "available"

    @property
    def is_public(self) -> bool:
        return self._aws_object["Public"]

    @property
    def image_location(self) -> str:
        return self._aws_object["ImageLocation"]

    @property
    def creation_date(self) -> str:
        return self._aws_object["CreationDate"]

    @property
    def tags(self) -> Optional[List[Dict[str, str]]]:
        if "Tags" in self._aws_object:
            return self._aws_object["Tags"]
