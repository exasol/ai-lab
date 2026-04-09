import os
import textwrap
from inspect import cleandoc
from pathlib import Path
from typing import Tuple

import boto3
from botocore.exceptions import ClientError as BotoClientError
from exasol.nb_connector.ai_lab_config import AILabConfig as CKey
from exasol.nb_connector.secret_store import Secrets
# We need to manually import all fixtures that we use, directly or indirectly,
# since the pytest won't do this for us.
from notebook_test_utils import (
    backend_setup,
    run_notebook,
    uploading_hack,
    set_log_level_for_libraries,
)

set_log_level_for_libraries()


def _create_aws_s3_bucket() -> str:
    """
    Copied from the sagemaker-extension/tests/ci_test/fixtures/prepare_environment_fixture.py
    """
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
    """
    Copied from the sagemaker-extension/tests/ci_test/fixtures/prepare_environment_fixture.py
    """
    s3_client = boto3.resource('s3')
    bucket = s3_client.Bucket(bucket_name)
    bucket.objects.all().delete()


def _create_sagemaker_role(iam_client) -> str:
    """
    Copied from the sagemaker-extension/tests/ci_test/fixtures/prepare_environment_fixture.py
    """
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
    """
    Copied from the sagemaker-extension/tests/ci_test/fixtures/prepare_environment_fixture.py
    """
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
    """
    Copied from the sagemaker-extension/tests/ci_test/fixtures/prepare_environment_fixture.py
    """
    iam_client.attach_role_policy(
        PolicyArn=policy_arn,
        RoleName=role_name,
    )


def _copy_aws_credentials():

    os.environ["AWS_DEFAULT_REGION"] = os.environ["NBTEST_AWS_DEFAULT_REGION"]
    os.environ["AWS_ACCESS_KEY_ID"] = os.environ["NBTEST_AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = os.environ["NBTEST_AWS_SECRET_ACCESS_KEY"]


def _store_aws_credentials(store_path: Path, store_password: str, bucket_name: str, role_name: str):

    conf = Secrets(store_path, store_password)
    conf.connection()
    conf.save(CKey.aws_access_key_id, os.environ["NBTEST_AWS_ACCESS_KEY_ID"])
    conf.save(CKey.aws_secret_access_key, os.environ["NBTEST_AWS_SECRET_ACCESS_KEY"])
    conf.save(CKey.aws_region, os.environ["NBTEST_AWS_DEFAULT_REGION"])
    conf.save(CKey.sme_aws_bucket, bucket_name)
    conf.save(CKey.sme_aws_role, role_name)


def _create_sagemaker_role_with_policy() -> str:
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


def get_job_polling_hack() -> Tuple[str, str]:
    return (
        'job_polling',
        textwrap.dedent("""
        def continuous_job_polling():
            import time
            from exasol.nb_connector.connections import open_pyexasol_connection
            from exasol.nb_connector.language_container_activation import get_activation_sql

            sql = f'EXECUTE SCRIPT {ai_lab_config.db_schema}."SME_POLL_SAGEMAKER_AUTOPILOT_JOB_STATUS"(' \
                f"'{ai_lab_config.JOB_NAME}'," \
                f"'{ai_lab_config.sme_aws_connection}'," \
                f"'{ai_lab_config.aws_region}');"

            with open_pyexasol_connection(ai_lab_config, compression=True) as conn:
                conn.execute(get_activation_sql(ai_lab_config))
                t_start = time.time()
                job_status = 'Unknown'
                while job_status != 'Completed':
                    assert time.time() - t_start < 14400, "Job execution is taking longer than 4 hours"
                    time.sleep(30)
                    query_result = conn.execute(sql)
                    job_status = query_result.fetchall()[0][0]

        continuous_job_polling()
        """)
    )


def get_deploy_model_hack() -> Tuple[str, str]:
    """
    Returns a notebook hack that cleans up any pre-existing SageMaker endpoint and endpoint
    configuration before the deployment step runs in sme_deploy_model.ipynb.

    Background / Why this is needed:
        The notebook hard-codes the endpoint name as 'APSPredictor'. AWS SageMaker does not
        allow creating an endpoint configuration that already exists - it raises a
        ValidationException: "Cannot create already existing endpoint configuration".
        When a previous test run is interrupted or the endpoint was not deleted at the end of
        the notebook (e.g. due to a test failure), the leftover endpoint config causes every
        subsequent test run to fail at the deploy step.

        This hack is injected into the notebook immediately after the cell tagged
        'endpoint_setup' (where ENDPOINT_NAME is defined), so ENDPOINT_NAME is already in
        scope when the cleanup runs.  It:
          1. Checks whether an endpoint with the same name is active and, if so, deletes it
             and waits until the deletion is confirmed by AWS.
          2. Checks whether an endpoint configuration with the same name exists and, if so,
             deletes it.
        Both steps handle the case where the resource does not exist yet (idempotent), so the
        hack is safe to run on a clean environment as well.
    """
    return (
        'endpoint_setup',
        textwrap.dedent("""
        def cleanup_existing_endpoint(endpoint_name):
            import boto3
            from botocore.exceptions import ClientError

            sm_client = boto3.client('sagemaker')

            # Delete existing endpoint if it exists
            try:
                response = sm_client.describe_endpoint(EndpointName=endpoint_name)
                status = response['EndpointStatus']
                print(f"Found endpoint '{endpoint_name}' in status '{status}'.")

                if status == 'Deleting':
                    # Already being deleted by a previous run — just wait for completion
                    print(f"Endpoint '{endpoint_name}' is already deleting, waiting...")
                else:
                    if status in ('Creating', 'Updating'):
                        # Must reach a stable state before deletion is accepted
                        print(f"Endpoint '{endpoint_name}' is '{status}', waiting for InService...")
                        sm_client.get_waiter('endpoint_in_service').wait(EndpointName=endpoint_name)
                    print(f"Deleting existing endpoint '{endpoint_name}'...")
                    sm_client.delete_endpoint(EndpointName=endpoint_name)

                waiter = sm_client.get_waiter('endpoint_deleted')
                waiter.wait(EndpointName=endpoint_name)
                print(f"Endpoint '{endpoint_name}' deleted.")
            except ClientError as e:
                if e.response['Error']['Code'] == 'ValidationException':
                    print(f"Endpoint '{endpoint_name}' does not exist, skipping deletion.")
                else:
                    raise

            # Delete existing endpoint configuration if it exists
            try:
                sm_client.describe_endpoint_config(EndpointConfigName=endpoint_name)
                print(f"Deleting existing endpoint config '{endpoint_name}'...")
                sm_client.delete_endpoint_config(EndpointConfigName=endpoint_name)
                print(f"Endpoint config '{endpoint_name}' deleted.")
            except ClientError as e:
                if e.response['Error']['Code'] == 'ValidationException':
                    print(f"Endpoint config '{endpoint_name}' does not exist, skipping deletion.")
                else:
                    raise

        cleanup_existing_endpoint(ENDPOINT_NAME)
        """)
    )


def _remove_sagemaker_endpoint_and_config(endpoint_name: str) -> None:
    """
    Deletes the SageMaker endpoint and its endpoint configuration by name.

    Why this is needed:
        The notebook's built-in delete step (SME_DELETE_SAGEMAKER_AUTOPILOT_ENDPOINT) only
        deletes the active endpoint itself, but leaves the endpoint *configuration* behind in
        AWS.  On the next test run, when the notebook tries to call CreateEndpointConfig with
        the same hard-coded name ('APSPredictor'), AWS raises:
            ValidationException: Cannot create already existing endpoint configuration.

        This function is called in the test's finally block so that both the endpoint and its
        configuration are always removed after the test, regardless of whether the notebook
        succeeded or failed mid-way.  Combined with get_deploy_model_hack() (which cleans up
        any pre-existing leftovers before the deploy step), this makes the test fully
        idempotent across consecutive runs.
    """
    sm_client = boto3.client('sagemaker')

    # Delete endpoint if it still exists (the notebook may or may not have deleted it already)
    try:
        response = sm_client.describe_endpoint(EndpointName=endpoint_name)
        status = response['EndpointStatus']
        print(f"Teardown: found endpoint '{endpoint_name}' in status '{status}'.")

        if status == 'Deleting':
            # Already being deleted (e.g. by the notebook's own cleanup step) — just wait
            print(f"Teardown: endpoint '{endpoint_name}' already deleting, waiting...")
        else:
            if status in ('Creating', 'Updating'):
                print(f"Teardown: endpoint '{endpoint_name}' is '{status}', waiting for stable state...")
                try:
                    sm_client.get_waiter('endpoint_in_service').wait(EndpointName=endpoint_name)
                except Exception:
                    pass  # endpoint may have failed; proceed with deletion attempt
            print(f"Teardown: deleting endpoint '{endpoint_name}'...")
            sm_client.delete_endpoint(EndpointName=endpoint_name)

        waiter = sm_client.get_waiter('endpoint_deleted')
        waiter.wait(EndpointName=endpoint_name)
        print(f"Teardown: endpoint '{endpoint_name}' deleted.")
    except BotoClientError as e:
        if e.response['Error']['Code'] == 'ValidationException':
            print(f"Teardown: endpoint '{endpoint_name}' not found, skipping.")
        else:
            raise

    # Always delete the endpoint config — the notebook never removes it
    try:
        sm_client.describe_endpoint_config(EndpointConfigName=endpoint_name)
        print(f"Teardown: deleting endpoint config '{endpoint_name}'...")
        sm_client.delete_endpoint_config(EndpointConfigName=endpoint_name)
        print(f"Teardown: endpoint config '{endpoint_name}' deleted.")
    except BotoClientError as e:
        if e.response['Error']['Code'] == 'ValidationException':
            print(f"Teardown: endpoint config '{endpoint_name}' not found, skipping.")
        else:
            raise


def test_sagemaker(backend_setup, uploading_hack):

    store_path, store_password = backend_setup
    store_file = str(store_path)

    _copy_aws_credentials()
    bucket_name = _create_aws_s3_bucket()
    role_name = _create_sagemaker_role_with_policy()
    _store_aws_credentials(store_path, store_password, bucket_name, role_name)

    current_dir = os.getcwd()
    try:
        run_notebook('main_config.ipynb', store_file, store_password)
        os.chdir('./data')
        run_notebook('data_telescope.ipynb', store_file, store_password)
        os.chdir('../sagemaker')
        run_notebook('sme_init.ipynb', store_file, store_password,
                     hacks=[uploading_hack])
        run_notebook('sme_train_model.ipynb', store_file, store_password,
                     hacks=[get_job_polling_hack()])
        run_notebook('sme_deploy_model.ipynb', store_file, store_password,
                     hacks=[get_deploy_model_hack()])
    finally:
        os.chdir(current_dir)
        _remove_aws_s3_bucket_content(bucket_name)
        _remove_sagemaker_endpoint_and_config("APSPredictor")
