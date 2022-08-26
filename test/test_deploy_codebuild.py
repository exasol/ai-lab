from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from test.cloudformation_validation import validate_using_cfn_lint


def test_deploy_ec2_template(codebuild_cloudformation_yml):
    aws_access = AwsAccess(None)
    aws_access.validate_cloudformation_template(codebuild_cloudformation_yml)


def test_deploy_cec2_template_with_cnf_lint(tmp_path, codebuild_cloudformation_yml):
    validate_using_cfn_lint(tmp_path, codebuild_cloudformation_yml)
