class EC2InstanceStatus:
    """
    Simplifies access to objects returned from:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instance_status
    """

    def __init__(self, aws_object):
        self._aws_object = aws_object

    @property
    def id(self) -> str:
        return self._aws_object["InstanceId"]

    @property
    def status(self) -> str:
        return self._aws_object["InstanceStatus"]["Status"]

    @property
    def initializing(self) -> bool:
        return self.status == "initializing"

    @property
    def ok(self) -> bool:
        return self.status == "ok"
