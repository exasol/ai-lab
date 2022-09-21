from typing import Union
from unittest.mock import MagicMock, Mock

import pytest

from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.vm_bucket.vm_slc_bucket import run_setup_vm_bucket, find_vm_bucket
from test.aws_mock_data import get_s3_cloudformation_mock_data
from test.cloudformation_validation import validate_using_cfn_lint
from test.mock_cast import mock_cast


def test_deploy_vm_bucket_template(vm_bucket_cloudformation_yml):
    aws_access = AwsAccess(None)
    aws_access.validate_cloudformation_template(vm_bucket_cloudformation_yml)


def test_deploy_vm_bucket_template_with_cnf_lint(tmp_path, vm_bucket_cloudformation_yml):
    validate_using_cfn_lint(tmp_path, vm_bucket_cloudformation_yml)


def test_find_bucket_with_mock():
    """
    This test uses a mock to validate the correct finding of the bucket in the stack.
    """
    aws_access_mock: Union[AwsAccess, Mock] = MagicMock()
    run_setup_vm_bucket(aws_access_mock)
    assert aws_access_mock.upload_cloudformation_stack.called

    mock_cast(aws_access_mock.describe_stacks).return_value = get_s3_cloudformation_mock_data()

    bucket = find_vm_bucket(aws_access_mock)
    assert len(bucket) > 0


def test_find_fails_with_mock():
    """
    This test uses a mock to validate the raising of a RuntimeError exception if the bucket was not deployed.
    """
    aws_access_mock: Union[AwsAccess, Mock] = MagicMock()
    run_setup_vm_bucket(aws_access_mock)
    assert aws_access_mock.upload_cloudformation_stack.called

    s3_stacks = get_s3_cloudformation_mock_data()
    s3_stacks[0]._aws_object["Outputs"] = []

    aws_access_mock.get_all_stack_resources.return_value = s3_stacks

    with pytest.raises(RuntimeError):
        find_vm_bucket(aws_access_mock)
