import botocore
import pytest

from exasol.ds.sandbox.lib.setup_ec2.cf_stack import (
    CloudformationStack,
    CloudformationStackContextManager,
)
from exasol.ds.sandbox.lib.setup_ec2.run_setup_ec2 import run_lifecycle_for_ec2
from exasol.ds.sandbox.lib.tags import create_default_asset_tag


def test_ec2_lifecycle_with_local_stack(
        local_stack_aws_access,
        default_asset_id,
        test_dummy_ami_id,
):
    """
    This test uses localstack to simulate lifecycle of an EC-2 instance
    """
    execution_generator = run_lifecycle_for_ec2(
        aws_access=local_stack_aws_access,
        ec2_instance_type="g4dn.xlarge",
        ec2_key_file=None,
        ec2_key_name=None,
        asset_id=default_asset_id,
        ami_id=test_dummy_ami_id,
        user_name=None,
    )
    status = next(execution_generator)
    ec2_instance, key_file_location = status
    while ec2_instance.is_pending:
        status = next(execution_generator)
        ec2_instance, key_file_location = status

    assert ec2_instance.instance_type == "g4dn.xlarge"
    assert ec2_instance.is_running
    status = next(execution_generator)
    ec2_instance, key_file_location = status
    assert ec2_instance is None and key_file_location is None


def test_ec2_manage_keypair_with_local_stack(local_stack_aws_access, default_asset_id):
    """
    This test uses localstack to create/delete a new ec2 key pair
    """
    aws = local_stack_aws_access
    ret = aws.create_new_ec2_key_pair("test", default_asset_id.tag_value)
    assert len(ret) > 0
    aws.delete_ec2_key_pair("test")


def test_cloudformation_with_localstack(
        default_asset_id,
        local_stack_aws_access,
        ec2_cloudformation_yml,
):
    aws = local_stack_aws_access
    aws.upload_cloudformation_stack(
        ec2_cloudformation_yml, stack_name="test_stack",
        tags=create_default_asset_tag(default_asset_id.tag_value)
    )
    stack_resources = aws.get_all_stack_resources(stack_name="test_stack")
    assert len(stack_resources) == 2
    ec2_instance = [i for i in stack_resources if i.is_ec2_instance]
    assert len(ec2_instance) == 1

    sec_group = [i for i in stack_resources if i.is_security_group]
    assert len(sec_group) == 1
    aws.delete_stack(stack_name="test_stack")


def test_validate_cloudformation_template(local_stack_aws_access, ec2_cloudformation_yml):
    local_stack_aws_access.validate_cloudformation_template(ec2_cloudformation_yml)


def test_validate_cloudformation_template_fails_with_local_stack(local_stack_aws_access):
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
          Value: "DataScienceSandbox"
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
              Value: "DataScienceSandbox"
            - Key: "exasol:owner"
              Value: "test"

        """
    with pytest.raises(botocore.exceptions.ClientError):
        local_stack_aws_access.validate_cloudformation_template(wrong_cloudformation_template)


def test_cloudformation_access_with_local_stack(
    local_stack_aws_access,
    default_asset_id,
    test_dummy_ami_id,
    test_ec2_instance_type,
):
    aws = local_stack_aws_access
    stack = CloudformationStack(
        aws_access=aws,
        ec2_key_name="test_key",
        user_name=aws.get_user(),
        asset_id=default_asset_id,
        ami_id=test_dummy_ami_id,
        instance_type=test_ec2_instance_type,
    )
    with CloudformationStackContextManager(stack) as uploaded_stack:
        id = uploaded_stack.get_ec2_instance_id()
        description = aws.describe_instance(id)
        host_name = description.public_dns_name
        assert description.is_running
        assert host_name.endswith(".eu-central-1.compute.amazonaws.com")


def test_user_with_local_stack(local_stack_aws_access):
    user_name = local_stack_aws_access.get_user()
    assert user_name == "default_user"
