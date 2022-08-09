from unittest.mock import MagicMock

import pytest

from exasol_script_languages_developer_sandbox.lib.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.vm_slc_bucket import run_setup_vm_bucket, find_vm_bucket
from test.cloudformation_validation import validate_using_cfn_lint
from test.aws_local_stack_access import AwsLocalStackAccess


def test_deploy_vm_bucket_template(vm_bucket_cloudformation_yml):
    aws_access = AwsAccess(None)
    aws_access.validate_cloudformation_template(vm_bucket_cloudformation_yml)


def test_deploy_vm_bucket_template_with_cnf_lint(tmp_path, vm_bucket_cloudformation_yml):
    validate_using_cfn_lint(tmp_path, vm_bucket_cloudformation_yml)


def test_find_bucket_with_mock():
    """
    This test uses a mock to validate the correct finding of the bucket in the stack.
    """
    aws_access_mock = MagicMock()
    run_setup_vm_bucket(aws_access_mock)
    assert aws_access_mock.upload_cloudformation_stack.called

    stack_resources_mock = \
        [
            {"ResourceType": "AWS::S3::Bucket",
             "ResourceStatus": "CREATE_COMPLETE",
             "LogicalResourceId": "VMSLCBucket",
             "PhysicalResourceId": "abc"}
        ]

    aws_access_mock.get_all_stack_resources.return_value = stack_resources_mock

    bucket = find_vm_bucket(aws_access_mock)
    assert len(bucket) > 0


def test_find_fails_with_mock():
    """
    This test uses a mock to validate the raising of a RuntimeError exception if the bucket was not deployed.
    """
    aws_access_mock = MagicMock()
    run_setup_vm_bucket(aws_access_mock)
    assert aws_access_mock.upload_cloudformation_stack.called

    stack_resources_mock = \
        [
            {"ResourceType": "AWS::S3::Bucket",
             "ResourceStatus": "CREATE_COMPLETE",
             "LogicalResourceId": "OtherBucket",
             "PhysicalResourceId": "abc"}
        ]

    aws_access_mock.get_all_stack_resources.return_value = stack_resources_mock

    with pytest.raises(RuntimeError):
        find_vm_bucket(aws_access_mock)


def test_find_bucket(local_stack):
    """
    This test uses localstack to deploy the VM Bucket and then find it again.
    """
    aws_access = AwsLocalStackAccess(None)
    run_setup_vm_bucket(aws_access)
    bucket = find_vm_bucket(aws_access)
    assert len(bucket) > 0


