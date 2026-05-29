from pathlib import Path


def test_ci_workflow_uses_python_toolbox_and_oidc_for_aws_ci():
    workflow = (Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yaml").read_text()

    assert "exasol/python-toolbox/.github/actions/python-environment@v8" in workflow
    assert "aws-actions/configure-aws-credentials@v5" in workflow
    assert "role-to-assume: ${{ vars.AWS_CI_ROLE }}" in workflow
    assert "aws-region: ${{ vars.AWS_CI_REGION }}" in workflow
    assert "approval-for-aws-ci-tests" in workflow
    assert "approve-aws-ci-execution" in workflow
    assert "needs: approval-for-aws-ci-tests" in workflow
    assert "RELEASE_MODE: workflow_dispatch" in workflow
    assert "RELEASE_TITLE: CI validation" in workflow
    assert "DSS_RUN_CI_TEST: \"true\"" in workflow
    assert "AWS_USER_NAME: release_user" in workflow
    assert "test/aws_ci/test_ci*.py" in workflow
