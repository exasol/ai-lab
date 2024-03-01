import pytest

from unittest.mock import MagicMock
from exasol.ds.sandbox.lib.aws_access.ec2_instance import EC2Instance
from exasol.ds.sandbox.lib.aws_access.stack_resource import StackResource
from exasol.ds.sandbox.lib.setup_ec2.run_setup_ec2 import (
    run_lifecycle_for_ec2,
    EC2StackLifecycleContextManager,
)



def ec2_instance(state: str):
    return EC2Instance({
        "InstanceId": "abc",
        "State": { "Name": state },
        "PublicDnsName": "public_host",
    })


INSTANCES_STATES = [
    ec2_instance("pending"),
    ec2_instance("pending"),
    ec2_instance("running"),
]


def test_run_lifecycle_for_ec2(default_asset_id, test_dummy_ami_id):
    """
    Test that the EC2 deployment and cleanup works as expected. The test
    calls execute_setup_ec2() and simulates the return states from AWS (2x
    pending, 1x running) for the EC2 instance.  At the end it expects that the
    AWS Cloudformation stack was deleted.
    """
    aws_access_mock = MagicMock()

    stack_resources_mock = [
        StackResource({
            "ResourceType": "AWS::EC2::Instance",
            "ResourceStatus": "CREATE_COMPLETE",
            "PhysicalResourceId": "abc",
        })
    ]

    aws_access_mock.get_all_stack_resources.return_value = stack_resources_mock
    aws_access_mock.stack_exists.return_value = False
    aws_access_mock.describe_instance.side_effect = INSTANCES_STATES
    res_gen = run_lifecycle_for_ec2(aws_access_mock, "test_key_file_loc", "test_key",
                                    default_asset_id, test_dummy_ami_id, user_name=None)
    res = next(res_gen)
    ec2_instance_description, key_file_loc = res

    assert not aws_access_mock.create_new_ec2_key_pair.called
    assert aws_access_mock.upload_cloudformation_stack.called
    assert ec2_instance_description.id == "abc" and\
           ec2_instance_description.public_dns_name == "public_host" and\
           ec2_instance_description.is_pending and\
           key_file_loc == "test_key_file_loc"
    res = next(res_gen)
    ec2_instance_description, key_file_loc = res
    assert ec2_instance_description.id == "abc" and\
           ec2_instance_description.public_dns_name == "public_host" and\
           ec2_instance_description.is_pending and\
           key_file_loc == "test_key_file_loc"
    res = next(res_gen)
    ec2_instance_description, key_file_loc = res
    assert ec2_instance_description.id == "abc" and\
           ec2_instance_description.public_dns_name == "public_host" and\
           ec2_instance_description.is_running and\
           key_file_loc == "test_key_file_loc"

    # Check cleanup
    assert not aws_access_mock.delete_stack.called
    next(res_gen)
    assert aws_access_mock.delete_stack.called

    with pytest.raises(StopIteration):
        next(res_gen)


def test_run_lifecycle_for_ec2_with_context_manager(default_asset_id, test_dummy_ami_id, test_config):
    """
    Test that the EC2 deployment and cleanup works as expected, by using
    the context manager helper class.  The test calls execute_setup_ec2() and
    simulates the return states from AWS (2x pending, 1x running) for the EC2
    instance.  At the end it expects that the AWS Cloudformation stack was
    deleted.
    """
    aws_access_mock = MagicMock()

    stack_resources_mock = [
        StackResource({
            "ResourceType": "AWS::EC2::Instance",
            "ResourceStatus": "CREATE_COMPLETE",
            "PhysicalResourceId": "abc",
        })
    ]

    aws_access_mock.get_all_stack_resources.return_value = stack_resources_mock
    aws_access_mock.stack_exists.return_value = False
    aws_access_mock.describe_instance.side_effect = INSTANCES_STATES
    res_gen = run_lifecycle_for_ec2(
        aws_access_mock,
        "test_key_file_loc",
        "test_key",
        default_asset_id,
        test_dummy_ami_id,
        user_name=None,
    )
    with EC2StackLifecycleContextManager(res_gen, test_config) as res:
        ec2_instance_description, key_file_location = res
        assert not aws_access_mock.create_new_ec2_key_pair.called
        assert aws_access_mock.upload_cloudformation_stack.called
        assert ec2_instance_description.is_running
        assert ec2_instance_description.public_dns_name == "public_host"
        assert ec2_instance_description.id == "abc"
        assert key_file_location == "test_key_file_loc"
    # Check cleanup
    assert aws_access_mock.delete_stack.called

    with pytest.raises(StopIteration):
        next(res_gen)
