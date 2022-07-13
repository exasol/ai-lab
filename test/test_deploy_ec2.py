from unittest.mock import MagicMock

from exasol_script_languages_developer_sandbox.lib.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.cf_stack import CloudformationStack, \
    CloudformationStackContextManager
from test.cloudformation_validation import validate_using_cfn_lint


def test_deploy_ec2_upload_invoked(ec2_cloudformation_yml):
    """"
    Test if function upload_cloudformation_stack() will be invoked
    with expected values when we run run_deploy_ci_build()
    """
    aws_access_mock = MagicMock()
    with CloudformationStackContextManager(CloudformationStack(aws_access_mock, "test_key", "test_user", None)) \
            as cf_access:
        pass
    aws_access_mock.upload_cloudformation_stack.assert_called_once_with(ec2_cloudformation_yml,
                                                                        cf_access.stack_name)


def test_deploy_ec2_custom_prefix(ec2_cloudformation_yml):
    """"
    Test that the custom prefix will be used for the cloudformation stack name.
    """
    aws_access_mock = MagicMock()
    aws_access_mock.stack_exists.return_value = False
    with CloudformationStackContextManager(CloudformationStack(aws_access_mock,
                                                               "test_key", "test_user", "test_prefix")) as cf_access:
        assert cf_access.stack_name.startswith("test_prefix")


def test_deploy_ec2_template(ec2_cloudformation_yml):
    aws_access = AwsAccess(None)
    aws_access.validate_cloudformation_template(ec2_cloudformation_yml)


def test_deploy_cec2_template_with_cnf_lint(tmp_path, ec2_cloudformation_yml):
    validate_using_cfn_lint(tmp_path, ec2_cloudformation_yml)
