from typing import Union
from unittest.mock import Mock, create_autospec

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.cloudformation_templates import VmBucketCfTemplate
from test.aws.templates import TEST_IP, TEST_ACL_ARN
from test.aws.mock_data import get_waf_cloudformation_mock_data
from test.mock_cast import mock_cast


# TODO: Do we need to generalize these tests apply them to Example Data S3 Bucket, too?
def test_find_acl_arn(test_config):
    """
    This test uses a mock to validate the correct finding of the ACL Arn
    in the mocked cloudformation stack.
    """
    aws: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws.describe_stacks).return_value = get_waf_cloudformation_mock_data()
    mock_cast(aws.instantiate_for_region).return_value = aws
    testee = VmBucketCfTemplate(aws).waf(config=test_config)
    testee.setup(TEST_IP)
    mock_cast(aws.upload_cloudformation_stack).assert_called_once()
    assert TEST_ACL_ARN == testee.acl_arn
