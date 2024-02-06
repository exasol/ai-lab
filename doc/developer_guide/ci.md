## Running tests in the CI

The project has two types of CI tests:
* unit tests and integration tests which run in a Github workflow
* A system test which runs on a AWS Codebuild

Both ci tests need to pass before the approval of a Github PR.
The Github workflow will run on each push to a branch in the Github repository. However, the AWS Codebuild will only run after you push a commit containing the string "[CodeBuild]" in the commit message, see [Executing AWS CodeBuild](#executing-aws-codebuild).

## Executing AWS CodeBuild

Use the following git commands to execute the AWS CodeBuild script:

```shell
git commit -m "[CodeBuild]" --allow-empty && git push
```

This will trigger a webhook that was installed by an AWS template into the git-Repository.
* The webhook is defined in file `exasol/ds/sandbox/templates/ci_code_build.jinja.yaml`
* and calls `aws-code-build/ci/buildspec.yaml`
* which then executes `test/codebuild/test_ci*.py`

The CodeBuild will take about 20 minutes to complete.

## Running AWS CodeBuild locally

To run these tests locally please use

```shell 
export DSS_RUN_CI_TEST=true; poetry run test/codebuild/test_ci.py 
```

