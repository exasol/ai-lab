import os
import pytest
import importlib.util
from unittest.mock import Mock

LAMBDA_PATH = "exasol/ds/sandbox/templates/cloudformation/example-data-s3/lambda.py"
TEST_BUCKET_NAME = "test-bucket"

@pytest.fixture
def lambda_module():
    spec = importlib.util.spec_from_file_location("lambda", LAMBDA_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def lambda_bucket_name_env(lambda_module):
    os.environ[lambda_module.ENV_BUCKET_NAME] = TEST_BUCKET_NAME
    yield TEST_BUCKET_NAME
    del os.environ[lambda_module.ENV_BUCKET_NAME]


def test_lambda_no_env(lambda_module):
    with pytest.raises(KeyError, match=lambda_module.ENV_BUCKET_NAME):
        lambda_module.lambda_handler({}, {})


def test_lambda(lambda_module, lambda_bucket_name_env):
    lambda_module.s3 = Mock(name='s3')
    method_mock = Mock(name="put_public_access_block")
    lambda_module.s3.put_public_access_block = method_mock

    res = lambda_module.lambda_handler(event={}, context={})
    method_mock.assert_called_once_with(
        Bucket=TEST_BUCKET_NAME,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True
        }
    )
    assert res['statusCode'] == 200
    assert TEST_BUCKET_NAME + " is now restricted" in res['body']
