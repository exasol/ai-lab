class StackResource:
    """
    Simplifies access to objects returned from:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_stack_resources
    """

    def __init__(self, aws_object):
        self._aws_object = aws_object

    @property
    def logica_id(self) -> str:
        return self._aws_object["LogicalResourceId"]

    @property
    def physical_id(self) -> str:
        return self._aws_object["PhysicalResourceId"]

    @property
    def resource_type(self) -> str:
        return self._aws_object["ResourceType"]

    @property
    def status(self) -> str:
        return self._aws_object["ResourceStatus"]

    @property
    def is_ec2_instance(self) -> bool:
        return self.resource_type == "AWS::EC2::Instance"

    @property
    def is_s3_bucket(self) -> bool:
        return self.resource_type == "AWS::S3::Bucket"

    @property
    def is_iam_role(self) -> bool:
        return self.resource_type == "AWS::IAM::Role"

    @property
    def is_security_group(self) -> bool:
        return self.resource_type == "AWS::EC2::SecurityGroup"

    @property
    def is_code_build(self) -> bool:
        return self.resource_type == "AWS::CodeBuild::Project"

    @property
    def is_complete(self) -> bool:
        return self.status == "CREATE_COMPLETE"


