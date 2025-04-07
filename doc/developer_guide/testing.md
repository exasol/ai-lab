# Tests

XAIL comes with a number of tests in the directory `test`. Besides, unit and integration tests in the respective directories, there are tests in the directory `codebuild`, see [Executing AWS CodeBuild](ci.md#executing-aws-codebuild).

## Speeding up Docker-based Tests

Creating a docker image is quite time-consuming, currently around 7 minutes.

To get test results faster, you can use an existing Docker image. You can create such an image using the [CLI command](commands.md#release-commands) `create-docker-image` or run your tests once with an additional CLI option `--keep-dss-docker-image` to keep the image rather than removing it after the test session.

Sample usage of the command `create-docker-image`:
```shell
poetry run -- exasol/ds/sandbox/main.py \
       create-docker-image \
       --version 9.9.9 \
       --log-level info
```

To use an existing docker image in the tests in `integration/test_create_dss_docker_image.py`, simply add the CLI option `--dss-docker-image` when calling `pytest`:

```shell
poetry run -- pytest --dss-docker-image exasol/ai-lab:3.1.0
```

## Tests for Jupyter Notebooks

The AI-Lab also contains end-to-end tests for Jupyter notebooks. Executing these tests can take several hours, currently ~3h.

The notebook tests are based on a common parameterized [test-runner](../../test/notebook_test_runner/test_notebooks_in_dss_docker_image.py). The test-runner contains a single parameterized test case on the outer level. Each time the test is executed, the test is parameterized with a Python file from the directory [test/notebooks](../../test/notebooks/) containing the particular test cases for one of the Jupyter notebooks.

The outer test case then uses a session-scoped fixture for creating an ordinary AI-Lab Docker image. Another session-scoped fixture adds some packages for executing the notebook tests, resulting in a second Docker image. Finally, the test-runner launches a Docker container from the second image and runs the inner test cases for the current notebook inside the Docker container.

In total, the following Docker entities are involved:
* Docker image 1 of the AI-Lab
* Docker image 2 for running the inner notebook tests
* Docker container running Docker image 2

### Speeding up Notebook Tests

You can speed up the notebook tests using the [same strategy](#speeding-up-docker-based-tests) as for tests involving the basic Docker image for the AI-Lab.

The CLI option to keep the image is `--keep-docker-image-notebook-test`, the option for using an existing Docker image for executing the notebook tests is `--docker-image-notebook-test`.

```shell
poetry run -- pytest --docker-image-notebook-test <name:version>
```

## Executing Tests Involving AWS Resources

In the AWS web interface, IAM create an access key for CLI usage and save or download the *access key id* and the *secret access key*.

In the file `~/.aws/config`, add lines:

```
[profile dss_aws_tests]
region = eu-central-1
```

In the file `~/.aws/credentials`, add:

```
[dss_aws_tests]
aws_access_key_id=...
aws_secret_access_key=...
```

In case you are using MFA authentication, please allocate a temporary token.

After that, you can set an environment variable and execute the tests involving AWS resources:

```shell
export AWS_PROFILE=dss_aws_tests_mfa
poetry run -- pytest test/test_deploy_codebuild.py
```

## Executing Tests Involving Ansible

To make pytest display Ansible log messages, please use:

```shell
poetry run -- pytest -s -o log_cli=true -o log_cli_level=INFO
```
