import os
from pathlib import Path
import boto3
from inspect import cleandoc
import pytest

from exasol.secret_store import Secrets
from exasol.ai_lab_config import AILabConfig as CKey

from notebook_test_utils import (access_to_temp_secret_store, run_notebook, uploading_hack)


def _create_aws_s3_bucket() -> str:
    s3_client = boto3.client('s3')
    bucket_name = "ci-exasol-sagemaker-extension-bucket"
    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': os.environ["NBTEST_AWS_DEFAULT_REGION"]}
        )
    except s3_client.exceptions.BucketAlreadyOwnedByYou as ex:
        print("Bucket already exists")
    return bucket_name


def _remove_aws_s3_bucket_content(bucket_name: str) -> None:
    s3_client = boto3.resource('s3')
    bucket = s3_client.Bucket(bucket_name)
    bucket.objects.all().delete()


def _create_sagemaker_role(iam_client) -> str:
    role_name = "ci-exasol-sagemaker-extension-role"
    try:
        assume_policy_document = cleandoc("""
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "sagemaker.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        """)
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=assume_policy_document,
            Description='This role is used for the CI Tests of the exasol.sagemaker-extension',
        )
    except iam_client.exceptions.EntityAlreadyExistsException as ex:
        print(f"Role '{role_name}' already exists")
    return role_name


def _create_sagemaker_policy(iam_client) -> str:
    policy_name = "ci-exasol-sagemaker-extension-policy"
    try:
        policy_document = cleandoc("""
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:*"
                    ],
                    "Resource": "*"
                }
            ]
        }
        """)
        response = iam_client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=policy_document,
            Description='This policy is used for the CI Tests of the exasol.sagemaker-extension',

        )
        return response["Policy"]["Arn"]
    except iam_client.exceptions.EntityAlreadyExistsException as ex:
        print("'EntityAlreadyExistsException' exception is handled")
        sts_client = boto3.client('sts')
        account_id = sts_client.get_caller_identity()['Account']
        policy_arn = f'arn:aws:iam::{account_id}:policy/{policy_name}'
        return policy_arn


def _attach_policy_to_role(iam_client, policy_arn, role_name):
    iam_client.attach_role_policy(
        PolicyArn=policy_arn,
        RoleName=role_name,
    )


def _store_aws_credentials(store_path: Path, store_password: str, bucket_name: str, role_name: str):

    conf = Secrets(store_path, store_password)
    conf.connection()
    conf.save(CKey.aws_access_key_id, os.environ["NBTEST_AWS_ACCESS_KEY_ID"])
    conf.save(CKey.aws_secret_access_key, os.environ["NBTEST_AWS_SECRET_ACCESS_KEY"])
    conf.save(CKey.aws_region, os.environ["NBTEST_AWS_DEFAULT_REGION"])
    conf.save(CKey.aws_bucket, bucket_name)
    conf.save(CKey.aws_role, role_name)


@pytest.fixture(scope="session")
def aws_s3_bucket() -> str:
    bucket_name = _create_aws_s3_bucket()
    try:
        yield bucket_name
    finally:
        _remove_aws_s3_bucket_content(bucket_name)


@pytest.fixture(scope="session")
def aws_sagemaker_role() -> str:
    iam_client = boto3.client('iam')
    role_name = _create_sagemaker_role(iam_client)
    policy_arn = _create_sagemaker_policy(iam_client)
    _attach_policy_to_role(iam_client,
                           policy_arn=policy_arn,
                           role_name=role_name)
    _attach_policy_to_role(iam_client,
                           policy_arn="arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
                           role_name=role_name)
    return role_name


def test_sagemaker(access_to_temp_secret_store, aws_s3_bucket, aws_sagemaker_role, uploading_hack):

    store_path, store_password = access_to_temp_secret_store
    store_file = str(store_path)
    _store_aws_credentials(store_path, store_password, aws_s3_bucket, aws_sagemaker_role)

    current_dir = os.getcwd()
    try:
        run_notebook('main_config.ipynb', store_file, store_password)
        os.chdir('./data')
        run_notebook('data_telescope.ipynb', store_file, store_password)
        os.chdir('../sagemaker')
        run_notebook('sme_init.ipynb', store_file, store_password, hacks=[uploading_hack])
        run_notebook('sme_train_model.ipynb', store_file, store_password)
        run_notebook('sme_deploy_model.ipynb', store_file, store_password)
    finally:
        os.chdir(current_dir)
