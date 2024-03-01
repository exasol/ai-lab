from typing import Union
from unittest.mock import Mock, create_autospec

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.vm_bucket.vm_dss_bucket_waf import (
    run_setup_vm_bucket_waf,
    find_acl_arn,
    get_cloudformation_template,
)
from test.aws.templates import TEST_IP, TEST_ACL_ARN
from test.aws.mock_data import get_waf_cloudformation_mock_data
from test.mock_cast import mock_cast


def test_find_acl_arn(test_config):
    """
    This test uses a mock to validate the correct finding of the ACL Arn
    in the mocked cloudformation stack.
    """
    aws: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws.describe_stacks).return_value = get_waf_cloudformation_mock_data()
    mock_cast(aws.instantiate_for_region).return_value = aws
    run_setup_vm_bucket_waf(aws, allowed_ip=TEST_IP, config=test_config)
    mock_cast(aws.upload_cloudformation_stack).assert_called_once()
    acl_arn = find_acl_arn(aws, test_config)
    assert TEST_ACL_ARN == acl_arn
