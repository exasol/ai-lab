## Running tests in the CI

The project has two types of CI tests:
* Unit tests and integration tests which run in a Github workflow
* Special integration tests verifying the content of the Jupyter notebook files
* A system test which runs in a AWS Codebuild

All these tests need to pass before the approval of a Github PR.
The Github workflow will run on each push to a branch in the Github repository.

However, the notebook tests and the AWS Codebuild will only run under specific conditions, e.g. manual approval or push a commit containing a special string in the commit message, see the following sections.

### Executing Jupyter Notebook Tests

The regular CI build will ask for confirmation (aka. "review") before executing these tests, see [ETAJ developer guide](https://github.com/exasol/exasol-test-setup-abstraction-java/blob/main/doc/developer_guide/developer_guide.md#ci-build) for details.

### Executing AWS CodeBuild

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
export DSS_RUN_CI_TEST=true; poetry run -- test/codebuild/test_ci.py
```

