### Tests

XAL comes with a number of tests in directory `test`. 
Besides, unit and integrations tests in the respective directories 
there are tests in directory `codebuild`, see [Executing AWS CodeBuild](ci.md#executing-aws-codebuild).  

# Speeding up Docker-based Tests

Creating a docker image is quite time-consuming, currently around 7 minutes. In order to use an existing 
docker image in the tests in `integration/test_create_dss_docker_image.py` 
simply add CLI option `--dss-docker-image` when calling `pytest`:

```shell  
poetry run pytest --dss-docker-image exasol/ai-lab:1.0.0 
```

#### Executing tests involving AWS resources

In AWS web interface, IAM create an access key for CLI usage and save or download the *access key id* and the *secret access key*.

In file `~/.aws/config` add lines

```
[profile dss_aws_tests]
region = eu-central-1
```

In file `~/.aws/credentials` add

```
[dss_aws_tests]
aws_access_key_id=...
aws_secret_access_key=...
```

In case your are using MFA authentication please allocate a temporary token.

After that you can set an environment variable and execute the tests involving AWS resources:

```shell
export AWS_PROFILE=dss_aws_tests_mfa
poetry run pytest test/test_deploy_codebuild.py
```

#### Executing tests involving Ansible

For making pytest display Ansible log messages, please use

```shell
poetry run pytest -s -o log_cli=true -o log_cli_level=INFO
```