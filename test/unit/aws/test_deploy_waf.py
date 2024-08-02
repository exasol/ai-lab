import pytest
from typing import Union
from unittest.mock import Mock, create_autospec

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.cloudformation_templates import (
    VmBucketCfTemplate,
    ExampleDataCfTemplate,
)
from test.aws.templates import TEST_IP, TEST_ACL_ARN
from test.aws.mock_data import (
    cf_stack_mock,
    VM_BUCKET_WAF_OUTPUTS,
    EXAMPLE_DATA_WAF_OUTPUTS,
)
from test.mock_cast import mock_cast


@pytest.fixture(params=(VmBucketCfTemplate, ExampleDataCfTemplate))
def cf_template_testee(request):
    return request.param


@pytest.mark.parametrize(
    "cf_template_testee, outputs",
     [
         (VmBucketCfTemplate, VM_BUCKET_WAF_OUTPUTS),
         (ExampleDataCfTemplate, EXAMPLE_DATA_WAF_OUTPUTS),
     ]
)
def test_find_acl_arn(test_config, cf_template_testee, outputs):
    """
    This test uses a mock to validate the correct finding of the ACL Arn
    in the mocked cloudformation stack.
    """
    aws: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws.instantiate_for_region).return_value = aws
    testee = cf_template_testee(aws).waf(config=test_config)
    mock_cast(aws.describe_stacks).return_value = cf_stack_mock(testee.stack_name, outputs)
    testee.setup(TEST_IP)
    mock_cast(aws.upload_cloudformation_stack).assert_called_once()
    assert TEST_ACL_ARN == testee.acl_arn
