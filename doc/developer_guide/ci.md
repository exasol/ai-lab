## Running tests in the CI

The GitHub workflow runs on each pull request and contains these test groups:
* Unit tests
* AWS-backed CI tests, which run after manual approval and provision AWS resources directly from GitHub Actions
* Integration tests, which include Docker-image build and validation checks in `test/integration`
* Notebook tests, which verify the notebook content and run in a separate workflow chain
* A system test suite that can be run locally against AWS resources

All required checks need to pass before a Github PR can be approved. The AWS-backed CI job stays blocked until the approval environment is granted.

### Executing Jupyter Notebook Tests

The regular CI build will ask for confirmation (aka. "review") before executing these tests, see [ETAJ developer guide](https://github.com/exasol/exasol-test-setup-abstraction-java/blob/main/doc/developer_guide/developer_guide.md#ci-build) for details.

### Executing AWS-backed CI

The AWS-backed CI tests are executed by the GitHub Actions workflow using AWS OIDC credentials and the
`test/aws_ci/test_ci*.py` suite.

To run these tests locally please use

```shell
export DSS_RUN_CI_TEST=true; poetry run -- pytest test/aws_ci/test_ci*.py
```

### Executing Integration Tests

The integration job in the GitHub workflow runs `test/integration`, which includes tests that build and validate the
AI Lab Docker image, for example `test/integration/test_create_dss_docker_image.py`.

To run these tests locally please use

```shell
poetry run -- pytest test/integration
```
