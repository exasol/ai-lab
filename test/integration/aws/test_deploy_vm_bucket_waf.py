from typing import Union
from unittest.mock import Mock, create_autospec

import pytest

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.vm_bucket.vm_dss_bucket_waf import run_setup_vm_bucket_waf, \
    find_acl_arn, get_cloudformation_template
from test.aws_mock_data import get_waf_cloudformation_mock_data, TEST_ACL_ARN
from test.integration.aws.cloudformation_validation import validate_using_cfn_lint
from test.mock_cast import mock_cast

TEST_IP = "1.1.1.1"


@pytest.fixture
def waf_cloudformation_yml():
    return get_cloudformation_template(TEST_IP)


def test_deploy_waf_template(waf_cloudformation_yml):
    aws_access = AwsAccess(None)
    aws_access.validate_cloudformation_template(waf_cloudformation_yml)


def test_deploy_waf_template_with_cnf_lint(tmp_path, waf_cloudformation_yml):
    validate_using_cfn_lint(tmp_path, waf_cloudformation_yml)


def test_find_acl_arn(test_config):
    """
    This test uses a mock to validate the correct finding of the ACL Arn in the mocked cloudformation stack.
    """
    aws_access_mock: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws_access_mock.describe_stacks).return_value = get_waf_cloudformation_mock_data()
    mock_cast(aws_access_mock.instantiate_for_region).return_value = aws_access_mock
    run_setup_vm_bucket_waf(aws_access_mock, allowed_ip=TEST_IP, config=test_config)
    mock_cast(aws_access_mock.upload_cloudformation_stack).assert_called_once()
    acl_arn = find_acl_arn(aws_access_mock, test_config)
    assert TEST_ACL_ARN == acl_arn
