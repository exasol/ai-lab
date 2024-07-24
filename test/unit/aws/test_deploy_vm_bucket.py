from typing import Union
from unittest.mock import Mock, create_autospec

import pytest

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.cloudformation_templates import VmBucketCfTemplate
from test.aws.mock_data import (
    TEST_BUCKET_ID,
    get_waf_cloudformation_mock_data,
    get_s3_cloudformation_mock_data,
)
from test.mock_cast import mock_cast


def test_find_bucket_success(test_config):
    """
    This test uses a mock to validate the correct finding of the bucket in the stack.
    """
    aws: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws.describe_stacks).return_value = \
        get_s3_cloudformation_mock_data() + \
        get_waf_cloudformation_mock_data()
    mock_cast(aws.instantiate_for_region).return_value = aws
    testee = VmBucketCfTemplate(aws)
    testee.setup(test_config)
    mock_cast(aws.upload_cloudformation_stack).assert_called_once()
    assert TEST_BUCKET_ID == testee.id


def test_vm_bucket_not_deployed(test_config):
    """
    This test uses a mock to validate the raising of a RuntimeError
    exception if the VM bucket was not deployed.
    """
    aws: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws.describe_stacks).return_value = get_waf_cloudformation_mock_data()
    mock_cast(aws.instantiate_for_region).return_value = aws

    testee = VmBucketCfTemplate(aws)
    with pytest.raises(RuntimeError, match=f"Stack {testee.stack_name} not found"):
        testee.id


def test_waf_not_deployed(test_config):
    """
    This test uses a mock to validate the raising of a RuntimeError
    exception if the WAF and VM bucket were not deployed.
    """
    aws: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws.describe_stacks).return_value = list()

    testee = VmBucketCfTemplate(aws)
    with pytest.raises(RuntimeError, match=f"Stack {testee.stack_name} not found"):
        testee.id
