import pytest

from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.render_template import render_template
from test.cloudformation_validation import validate_using_cfn_lint


codebuild_cloudformation_templates = [
    render_template("ci_code_build.jinja.yaml", vm_bucket="test-bucket-123"),
    render_template("release_code_build.jinja.yaml", vm_bucket="test-bucket-123")]


@pytest.mark.parametrize("cloudformation_template", codebuild_cloudformation_templates)
def test_deploy_ci_codebuild_template(cloudformation_template):
    aws_access = AwsAccess(None)
    aws_access.validate_cloudformation_template(cloudformation_template)


@pytest.mark.parametrize("cloudformation_template", codebuild_cloudformation_templates)
def test_deploy_ci_codebuild_template_with_cnf_lint(tmp_path, cloudformation_template):
    validate_using_cfn_lint(tmp_path, cloudformation_template)
