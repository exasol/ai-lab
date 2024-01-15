from typing import Union
from unittest.mock import Mock, create_autospec

import pytest

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.vm_bucket.vm_dss_bucket import run_setup_vm_bucket, find_vm_bucket, \
    create_vm_bucket_cf_template
from test.aws_mock_data import TEST_BUCKET_ID, get_waf_cloudformation_mock_data, TEST_ACL_ARN, \
    get_s3_cloudformation_mock_data
from test.integration.aws.cloudformation_validation import validate_using_cfn_lint
from test.mock_cast import mock_cast
from exasol.ds.sandbox.lib.vm_bucket.vm_dss_bucket import STACK_NAME as VM_STACK_NAME


@pytest.fixture
def vm_bucket_cloudformation_yml():
    return create_vm_bucket_cf_template(TEST_ACL_ARN)


def test_deploy_vm_bucket_template(vm_bucket_cloudformation_yml):
    aws_access = AwsAccess(None)
    aws_access.validate_cloudformation_template(vm_bucket_cloudformation_yml)


def test_deploy_vm_bucket_template_with_cnf_lint(tmp_path, vm_bucket_cloudformation_yml):
    validate_using_cfn_lint(tmp_path, vm_bucket_cloudformation_yml)


def test_find_bucket_with_mock(test_config):
    """
    This test uses a mock to validate the correct finding of the bucket in the stack.
    """
    aws_access_mock: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws_access_mock.describe_stacks).return_value = get_s3_cloudformation_mock_data() + \
                                                              get_waf_cloudformation_mock_data()
    mock_cast(aws_access_mock.instantiate_for_region).return_value = aws_access_mock
    run_setup_vm_bucket(aws_access_mock, test_config)
    mock_cast(aws_access_mock.upload_cloudformation_stack).assert_called_once()

    bucket = find_vm_bucket(aws_access_mock)
    assert TEST_BUCKET_ID == bucket


def test_find_fails_if_vm_stack_not_deployed_with_mock(test_config):
    """
    This test uses a mock to validate the raising of a RuntimeError exception if the VM bucket was not deployed.
    """
    aws_access_mock: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws_access_mock.describe_stacks).return_value = get_waf_cloudformation_mock_data()
    mock_cast(aws_access_mock.instantiate_for_region).return_value = aws_access_mock

    with pytest.raises(RuntimeError, match=f"stack {VM_STACK_NAME} not found"):
        find_vm_bucket(aws_access_mock)


def test_find_fails_if_waf_stack_not_deployed_with_mock(test_config):
    """
    This test uses a mock to validate the raising of a RuntimeError exception if the WAF and VM bucket were not deployed.
    """
    aws_access_mock: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)

    mock_cast(aws_access_mock.describe_stacks).return_value = list()

    with pytest.raises(RuntimeError, match=f"stack {VM_STACK_NAME} not found"):
        find_vm_bucket(aws_access_mock)
