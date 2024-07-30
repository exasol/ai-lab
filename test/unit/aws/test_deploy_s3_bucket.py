from typing import Union
from unittest.mock import Mock, create_autospec

import pytest

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.cloudformation_templates import (
    VmBucketCfTemplate,
    ExampleDataCfTemplate,
)
from test.aws.mock_data import (
    get_waf_cloudformation_mock_data,
    cf_stack_mock,
    cf_stack_outputs,
    TEST_BUCKET_ID,
)
from test.mock_cast import mock_cast


@pytest.fixture(params=(VmBucketCfTemplate, ExampleDataCfTemplate))
def cf_template_testee(request):
    return request.param



def test_find_bucket_success(test_config, cf_template_testee):
    """
    This test uses a mock to validate the correct finding of the bucket in the stack.
    """
    aws: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    testee = cf_template_testee(aws)

    bucket = cf_stack_mock(
        testee.stack_name,
        cf_stack_outputs(cf_template_testee.__name__, "s3")
    )
    waf = cf_stack_mock(
        testee.waf(test_config).stack_name,
        cf_stack_outputs(cf_template_testee.__name__, "waf"),
    )

    mock_cast(aws.describe_stacks).return_value = bucket + waf
    mock_cast(aws.instantiate_for_region).return_value = aws
    testee.setup(test_config)
    mock_cast(aws.upload_cloudformation_stack).assert_called_once()
    assert TEST_BUCKET_ID == testee.id


def test_vm_bucket_not_deployed(cf_template_testee):
    """
    This test uses a mock to validate the raising of a RuntimeError
    exception if the VM bucket was not deployed.
    """
    aws: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws.describe_stacks).return_value = get_waf_cloudformation_mock_data()
    mock_cast(aws.instantiate_for_region).return_value = aws

    testee = cf_template_testee(aws)
    with pytest.raises(RuntimeError, match=f"Stack {testee.stack_name} not found"):
        testee.id


def test_waf_not_deployed(cf_template_testee):
    """
    This test uses a mock to validate the raising of a RuntimeError
    exception if the WAF and VM bucket were not deployed.
    """
    aws: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws.describe_stacks).return_value = list()

    testee = cf_template_testee(aws)
    with pytest.raises(RuntimeError, match=f"Stack {testee.stack_name} not found"):
        testee.id
