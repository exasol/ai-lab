from typing import Any

import boto3

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess


class AwsLocalStackAccess(AwsAccess):
    def __init__(self, key_id="test", secret_key="test"):
        super().__init__(aws_profile=None)
        self.key_id = key_id
        self.secret_key = secret_key

    def with_user(self, user_name: str = "default_user") -> "AwsLocalStackAccess":
        self._create_user(user_name)
        key = self._create_access_key(user_name)
        # print(f'key_id = {key["AccessKeyId"]}, secret_key = {key["SecretAccessKey"]}')
        return AwsLocalStackAccess(
            key_id=key["AccessKeyId"],
            secret_key=key["SecretAccessKey"],
        )

    def _create_user(self, name) -> Any:
        return self._get_aws_client("iam").create_user(UserName = name)

    def _create_access_key(self, user_name: str) -> Any:
        result = self._get_aws_client("iam").create_access_key(UserName=user_name)
        return result["AccessKey"]

    def _get_aws_client(self, service_name: str) -> Any:
        return boto3.client(
            service_name,
            endpoint_url="http://localhost:4566",
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.secret_key,
            region_name="eu-central-1",
        )
