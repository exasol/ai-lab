import logging
from typing import Optional, Any, List, Dict

import boto3
import botocore

from exasol_script_languages_developer_sandbox.lib.deployer import Deployer


class AwsAccess(object):
    def __init__(self, aws_profile: Optional[str]):
        self._aws_profile = aws_profile

    @property
    def aws_profile_for_logging(self) -> str:
        if self._aws_profile is not None:
            return self._aws_profile
        else:
            return "{default}"

    @property
    def aws_profile(self) -> Optional[str]:
        return self._aws_profile

    def create_new_ec2_key_pair(self, key_name: str) -> str:
        """
        Create an EC-2 Key-Pair, identified by parameter 'key_name'
        """
        logging.debug(f"Running create_new_ec2_key_pair for aws profile {self.aws_profile_for_logging}")
        cloud_client = self._get_aws_client("ec2")
        key_pair = cloud_client.create_key_pair(KeyName=key_name)
        return str(key_pair['KeyMaterial'])

    def delete_ec2_key_pair(self, key_name: str) -> None:
        """
        Delete the EC-2 Key-Pair, given by parameter 'key_name'
        """
        logging.debug(f"Running delete_ec2_key_pair for aws profile {self.aws_profile_for_logging}")
        cloud_client = self._get_aws_client("ec2")
        cloud_client.delete_key_pair(KeyName=key_name)

    def upload_cloudformation_stack(self, yml: str, stack_name: str):
        """
        Deploy the cloudformation stack.
        """
        logging.debug(f"Running upload_cloudformation_stack for aws profile {self.aws_profile_for_logging}")
        cloud_client = self._get_aws_client("cloudformation")
        try:
            cfn_deployer = Deployer(cloudformation_client=cloud_client)
            result = cfn_deployer.create_and_wait_for_changeset(stack_name=stack_name, cfn_template=yml,
                                                                parameter_values=[],
                                                                capabilities=(), role_arn=None,
                                                                notification_arns=None, tags=tuple())
        except Exception as e:
            logging.error(f"Error creating changeset for cloud formation template: {e}")
            raise e
        try:
            cfn_deployer.execute_changeset(changeset_id=result.changeset_id, stack_name=stack_name)
            cfn_deployer.wait_for_execute(stack_name=stack_name, changeset_type=result.changeset_type)
        except Exception as e:
            logging.error(f"Error executing changeset for cloud formation template: {e}")
            logging.error(f"Run 'aws cloudformation describe-stack-events --stack-name {stack_name}' to get details.")
            raise e

    def validate_cloudformation_template(self, cloudformation_yml) -> None:
        """
        This function pushes the YAML to AWS Cloudformation for validation
        (see https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-validate-template.html)
        Pitfall: Boto3 expects the YAML string as parameter, whereas the AWS CLI expects the file URL as parameter.
        It requires to have the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables set correctly.
        """
        logging.debug(f"Running validate_cloudformation_template for aws profile {self.aws_profile_for_logging}")
        cloud_client = self._get_aws_client("cloudformation")
        cloud_client.validate_template(TemplateBody=cloudformation_yml)

    def _get_stack_resources(self, stack_name: str) -> List[Dict[str, str]]:
        cf_client = self._get_aws_client('cloudformation')
        current_result = cf_client.list_stack_resources(StackName=stack_name)
        result = current_result["StackResourceSummaries"]

        while "nextToken" in current_result:
            current_result = cf_client.list_stack_resources(StackName=stack_name, nextToken=current_result["nextToken"])
            result.extend(current_result["StackResourceSummaries"])
        return result

    def get_all_stack_resources(self, stack_name: str) -> List[Dict[str, str]]:
        """
        This functions uses Boto3 to get all AWS Cloudformation resources for a specific Cloudformation stack,
        identified by parameter `stack_name`.
        The AWS API truncates at a size of 1MB, and in order to get all chunks the method must be called
        passing the previous retrieved token until no token is returned.
        """
        logging.debug(f"Running get_all_codebuild_projects for aws profile {self.aws_profile_for_logging}")
        return self._get_stack_resources(stack_name=stack_name)

    def stack_exists(self, stack_name: str) -> bool:
        """
        This functions uses Boto3 to check if stack with name `stack_name` exists.
        """
        logging.debug(f"Running stack_exists for aws profile {self.aws_profile_for_logging}")
        try:
            result = self._get_stack_resources(stack_name=stack_name)
            return any([res["ResourceStatus"] != "DELETE_COMPLETE" for res in result])
        except botocore.exceptions.ClientError:
            return False

    def delete_stack(self, stack_name: str) -> None:
        """
        This functions uses Boto3 to delete a stack identified by parameter "stack_name".
        """
        logging.debug(f"Running delete_stack for aws profile {self.aws_profile_for_logging}")
        cf_client = self._get_aws_client('cloudformation')
        cf_client.delete_stack(StackName=stack_name)

    def describe_instance(self, instance_id: str):
        """
        Describes an AWS instance identified by parameter instance_id
        """
        logging.debug(f"Running delete_ec2_key_pair for aws profile {self.aws_profile_for_logging}")
        cloud_client = self._get_aws_client("ec2")
        return cloud_client.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]

    def get_user(self) -> str:
        """
        Return the current IAM user name.
        """
        iam_client = self._get_aws_client("iam")
        cu = iam_client.get_user()
        return cu["User"]["UserName"]

    def _get_aws_client(self, service_name: str) -> Any:
        if self._aws_profile is None:
            return boto3.client(service_name)
        aws_session = boto3.session.Session(profile_name=self._aws_profile)
        return aws_session.client(service_name)
