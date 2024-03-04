from typing import Union
from unittest.mock import Mock, create_autospec

import pytest

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.vm_bucket.vm_dss_bucket import (
    run_setup_vm_bucket,
    find_vm_bucket,
    create_vm_bucket_cf_template,
)
from test.aws.mock_data import (
    TEST_BUCKET_ID,
    get_waf_cloudformation_mock_data,
    get_s3_cloudformation_mock_data,
)
from test.mock_cast import mock_cast
from exasol.ds.sandbox.lib.vm_bucket.vm_dss_bucket import STACK_NAME as VM_STACK_NAME


def test_find_bucket_success(test_config):
    """
    This test uses a mock to validate the correct finding of the bucket in the stack.
    """
    aws: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws.describe_stacks).return_value = \
        get_s3_cloudformation_mock_data() + \
        get_waf_cloudformation_mock_data()
    mock_cast(aws.instantiate_for_region).return_value = aws
    run_setup_vm_bucket(aws, test_config)
    mock_cast(aws.upload_cloudformation_stack).assert_called_once()

    bucket = find_vm_bucket(aws)
    assert TEST_BUCKET_ID == bucket


def test_vm_bucket_undeployed(test_config):
    """
    This test uses a mock to validate the raising of a RuntimeError
    exception if the VM bucket was not deployed.
    """
    aws: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws.describe_stacks).return_value = get_waf_cloudformation_mock_data()
    mock_cast(aws.instantiate_for_region).return_value = aws

    with pytest.raises(RuntimeError, match=f"stack {VM_STACK_NAME} not found"):
        find_vm_bucket(aws)


def test_waf_undeployed(test_config):
    """
    This test uses a mock to validate the raising of a RuntimeError
    exception if the WAF and VM bucket were not deployed.
    """
    aws: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws.describe_stacks).return_value = list()

    with pytest.raises(RuntimeError, match=f"stack {VM_STACK_NAME} not found"):
        find_vm_bucket(aws)
