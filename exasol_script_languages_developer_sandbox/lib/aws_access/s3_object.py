class S3Object:
    """
    Simplifies access to objects returned from:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_objects_v2
    """

    def __init__(self, aws_object):
        self._aws_object = aws_object

    @property
    def key(self) -> str:
        return self._aws_object["Key"]

    @property
    def size(self) -> int:
        return self._aws_object["Size"]
