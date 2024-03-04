# The tests in this file validate the various cloudformation templates by
# using the cloudformation linter "cfn-lint".

import pytest
import subprocess

from test.aws.templates import (
    ec2_template,
    waf_template,
    vm_bucket_template,
    ci_codebuild_template,
    release_codebuild_template,
)


def validate_using_cfn_lint(tmp_path, cloudformation_yml):
    """
    This test uses cfn-lint to validate the Cloudformation template.
    (See https://github.com/aws-cloudformation/cfn-lint)
    """
    out_file = tmp_path / "cloudformation.yaml"
    with open(out_file, "w") as f:
        f.write(cloudformation_yml)

    completed_process = subprocess.run(["cfn-lint", str(out_file.absolute())], capture_output=True)
    try:
        completed_process.check_returncode()
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        raise e


TEMPLATES = {
    "ci-codebuild": ci_codebuild_template(),
    "release-codebuild": release_codebuild_template(),
    "ec2": ec2_template(),
    "vm-bucket": vm_bucket_template(),
    "waf": waf_template(),
}


@pytest.mark.parametrize("template_key", TEMPLATES)
def test_lint_cloudformation_templates(tmp_path, template_key):
    validate_using_cfn_lint(tmp_path, TEMPLATES[template_key])
