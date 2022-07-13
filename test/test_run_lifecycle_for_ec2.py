from unittest.mock import MagicMock

import pytest

from exasol_script_languages_developer_sandbox.lib.run_setup_ec2 import run_lifecycle_for_ec2


def test_run_lifecycle_for_ec2():
    """
    Test that the EC2 deployment and cleanup works as expected. The test calls execute_setup_ec2() and simulates
    the return states from AWS (2x pending, 1x running) for the EC2 instance.
    At the end it expects that the AWS Cloudformation stack was deleted.
    """
    aws_access_mock = MagicMock()

    stack_resources_mock = \
        [
            {"ResourceType": "AWS::EC2::Instance",
             "ResourceStatus": "CREATE_COMPLETE",
             "PhysicalResourceId": "abc"}
        ]

    aws_access_mock.get_all_stack_resources.return_value = stack_resources_mock
    aws_access_mock.stack_exists.return_value = False
    instances_states =\
        [
            {"State": {"Name": "pending"}, "PublicDnsName": "public_host"},
            {"State": {"Name": "pending"}, "PublicDnsName": "public_host"},
            {"State": {"Name": "running"}, "PublicDnsName": "public_host"}
        ]
    aws_access_mock.describe_instance.side_effect = instances_states
    res_gen = run_lifecycle_for_ec2(aws_access_mock, "test_key_file_loc", "test_key", None)
    res = next(res_gen)
    assert not aws_access_mock.create_new_ec2_key_pair.called
    assert aws_access_mock.upload_cloudformation_stack.called
    assert res == ("pending", "public_host", "abc", "test_key_file_loc")
    res = next(res_gen)
    assert res == ("pending", "public_host", "abc", "test_key_file_loc")
    res = next(res_gen)
    assert res == ("running", "public_host", "abc", "test_key_file_loc")

    #Check cleanup
    assert not aws_access_mock.delete_stack.called
    next(res_gen)
    assert aws_access_mock.delete_stack.called

    with pytest.raises(StopIteration):
        next(res_gen)
