from typing import Any

import boto3

from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess


class AwsLocalStackAccess(AwsAccess):
    def _get_aws_client(self, service_name: str) -> Any:
        return boto3.client(service_name, endpoint_url="http://localhost:4566", aws_access_key_id="test",
                            aws_secret_access_key="test", region_name="eu-central-1")
