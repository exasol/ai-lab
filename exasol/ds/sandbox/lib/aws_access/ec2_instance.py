class EC2Instance:
    """
    Simplifies access to objects returned from:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances
    """

    def __init__(self, aws_object):
        self._aws_object = aws_object

    @property
    def image_id(self) -> str:
        return self._aws_object["ImageId"]

    @property
    def id(self) -> str:
        return self._aws_object["InstanceId"]

    @property
    def state_name(self) -> str:
        return self._aws_object["State"]["Name"]

    @property
    def public_dns_name(self) -> str:
        return self._aws_object["PublicDnsName"]

    @property
    def is_pending(self) -> bool:
        return self.state_name == "pending"

    @property
    def is_running(self) -> bool:
        return self.state_name == "running"
