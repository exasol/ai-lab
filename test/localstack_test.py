import botocore
import pytest

from exasol_script_languages_developer_sandbox.lib.cf_stack import CloudformationStack, \
    CloudformationStackContextManager
from exasol_script_languages_developer_sandbox.lib.run_setup_ec2 import run_lifecycle_for_ec2, \
    unpack_ec2_instance_description
from test.aws_local_stack_access import AwsLocalStackAccess


def test_ec2_lifecycle_with_local_stack(local_stack):
    """
    This test uses localstack to simulate lifecycle of an EC-2 instance
    """
    print("run ec2_setup!")
    execution_generator = run_lifecycle_for_ec2(AwsLocalStackAccess(None), None, None, None)
    res = next(execution_generator)
    while res[0] == "pending":
        res = next(execution_generator)

    ec2_instance_status, host_name, ec2_instance_id, key_file_location = res
    assert ec2_instance_status == "running"
    print("running!")
    res = next(execution_generator)
    ec2_instance_status, host_name, ec2_instance_id, key_file_location = res
    assert ec2_instance_status == "terminated"


def test_ec2_manage_keypair_with_local_stack(local_stack):
    """
    This test uses localstack to create/delete a new ec2 key pair
    """
    aws_access = AwsLocalStackAccess(None)
    ret = aws_access.create_new_ec2_key_pair("test")
    assert len(ret) > 0
    aws_access.delete_ec2_key_pair("test")


def test_cloudformation_with_localstack(local_stack, ec2_cloudformation_yml):
    aws_access = AwsLocalStackAccess(None)
    aws_access.upload_cloudformation_stack(ec2_cloudformation_yml, stack_name="test_stack")
    stack_resources = aws_access.get_all_stack_resources(stack_name="test_stack")
    assert len(stack_resources) == 2
    ec2_instance = [i for i in stack_resources if i["ResourceType"] == "AWS::EC2::Instance"]
    assert len(ec2_instance) == 1

    sec_group = [i for i in stack_resources if i["ResourceType"] == "AWS::EC2::SecurityGroup"]
    assert len(sec_group) == 1
    aws_access.delete_stack(stack_name="test_stack")


def test_validate_cloudformation_template(local_stack, ec2_cloudformation_yml):
    aws_access = AwsLocalStackAccess(None)
    aws_access.validate_cloudformation_template(ec2_cloudformation_yml)


def test_validate_cloudformation_template_fails_with_local_stack(local_stack):
    wrong_cloudformation_template = \
        """
Resources:
  Ec2SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: EC2 Instance access
      SecurityGroupIngress:
        - CidrIp: 0.0.0.0/0
          FromPort: 22
          IpProtocol: tcp
          ToPort: 22
      Tags:
        - Key: "exasol:project"
          Value: "ScriptLanguages"
        - Key: "exasol:owner"
          Value: "test user"

  {{Here_we_put_an_error}}:
      Type: AWS::EC2::INVALID_TYPE
      Properties:
          ImageId: "ami-0c9354388bb36c088"
          KeyName: "test_key"
          InstanceType: "t2.medium"
          SecurityGroups:
          - !Ref Ec2SecurityGroup
          BlockDeviceMappings:
          -
            DeviceName: /dev/sda1
            Ebs:
              VolumeSize: 100
          Tags:
            - Key: "exasol:project"
              Value: "ScriptLanguages"
            - Key: "exasol:owner"
              Value: "test"

        """
    aws_access = AwsLocalStackAccess(None)

    with pytest.raises(botocore.exceptions.ClientError):
        aws_access.validate_cloudformation_template(wrong_cloudformation_template)


def test_cloudformation_access_with_local_stack(local_stack):
    aws_access = AwsLocalStackAccess(None)
    with CloudformationStackContextManager(CloudformationStack(aws_access, "test_key", aws_access.get_user(), None)) \
            as cf_stack:
        ec2_instance_id = cf_stack.get_ec2_instance_id()
        ec2_instance_description = aws_access.describe_instance(ec2_instance_id)
        status, host_name = unpack_ec2_instance_description(ec2_instance_description)
        assert status == "running"
        assert host_name.endswith(".eu-central-1.compute.amazonaws.com")


def test_user_with_local_stack(local_stack):
    aws_access = AwsLocalStackAccess(None)
    user_name = aws_access.get_user()
    assert user_name == "default_user"

