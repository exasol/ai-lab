from functools import wraps
from typing import Optional, Any, List, Dict, Tuple

import boto3
import botocore

from exasol.ds.sandbox.lib.aws_access.ami import Ami
from exasol.ds.sandbox.lib.aws_access.cloudformation_stack import CloudformationStack
from exasol.ds.sandbox.lib.aws_access.deployer import Deployer
from exasol.ds.sandbox.lib.aws_access.ec2_instance import EC2Instance
from exasol.ds.sandbox.lib.aws_access.ec2_instance_status import EC2InstanceStatus
from exasol.ds.sandbox.lib.aws_access.export_image_task import ExportImageTask
from exasol.ds.sandbox.lib.aws_access.key_pair import KeyPair
from exasol.ds.sandbox.lib.aws_access.s3_object import S3Object
from exasol.ds.sandbox.lib.aws_access.snapshot import Snapshot
from exasol.ds.sandbox.lib.aws_access.stack_resource import StackResource
from exasol.ds.sandbox.lib.aws_access.waiter.codebuild_waiter import CodeBuildWaiter
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.tags import create_default_asset_tag
from exasol.ds.sandbox.lib.export_vm.vm_disk_image_format import VmDiskImageFormat

LOG = get_status_logger(LogType.AWS_ACCESS)


def _log_function_start(func):
    """
    Logging function which can be used to debug-log start of member function of AwsAccess.
    This decorator works only for class AwsAccess.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        LOG.debug('Start {func_name} for aws profile "{aws_profile}"'.
                  format(func_name=func.__name__, aws_profile=self.aws_profile_for_logging))
        result = func(self, *args, **kwargs)
        return result
    return wrapper


class AwsAccess(object):
    def __init__(self, aws_profile: Optional[str], region: Optional[str] = None):
        self._aws_profile = aws_profile
        self._region = region
        LOG.info("Instantiated AwsAccess with {aws_profile}".format(aws_profile=aws_profile))

    @property
    def aws_profile_for_logging(self) -> str:
        if self._aws_profile is not None:
            return self._aws_profile
        else:
            return "{default}"

    @property
    def aws_profile(self) -> Optional[str]:
        return self._aws_profile

    @_log_function_start
    def create_new_ec2_key_pair(self, key_name: str, tag_value: str) -> str:
        """
        Create an EC-2 Key-Pair, identified by parameter 'key_name'
        :required actions: ec2:CreateKeyPair
        """
        cloud_client = self._get_aws_client("ec2")
        tags = [{"ResourceType": "key-pair", "Tags": create_default_asset_tag(tag_value)}]
        key_pair = cloud_client.create_key_pair(KeyName=key_name, TagSpecifications=tags)
        return str(key_pair['KeyMaterial'])

    @_log_function_start
    def delete_ec2_key_pair(self, key_name: str) -> None:
        """
        Delete the EC-2 Key-Pair, given by parameter 'key_name'
        :required actions: ec2:DeleteKeyPair
        """
        cloud_client = self._get_aws_client("ec2")
        cloud_client.delete_key_pair(KeyName=key_name)

    @_log_function_start
    def upload_cloudformation_stack(self, yml: str, stack_name: str, tags=tuple()) -> None:
        """
        Deploy the cloudformation stack.
        :required actions: cloudformation:CreateChangeSet, cloudformation:DescribeChangeSet,
                           cloudformation:ExecuteChangeSet,
                           and all actions required for creating elements of the specific stack
                           (e.g. ec2:CreateSecurityGroup, ec2:RunInstances,...)
        """
        cloud_client = self._get_aws_client("cloudformation")
        try:
            cfn_deployer = Deployer(cloudformation_client=cloud_client)
            result = cfn_deployer.create_and_wait_for_changeset(stack_name=stack_name, cfn_template=yml,
                                                                parameter_values=[],
                                                                capabilities=("CAPABILITY_IAM",), role_arn=None,
                                                                notification_arns=None, tags=tags)
        except Exception as e:
            LOG.error(f"Error creating changeset for cloud formation template: {e}")
            raise e
        try:
            cfn_deployer.execute_changeset(changeset_id=result.changeset_id, stack_name=stack_name)
            cfn_deployer.wait_for_execute(stack_name=stack_name, changeset_type=result.changeset_type)
        except Exception as e:
            LOG.error(f"Error executing changeset for cloud formation template: {e}")
            LOG.error(f"Run 'aws cloudformation describe-stack-events --stack-name {stack_name}' to get details.")
            raise e

    def read_secret_arn(self, physical_resource_id: str):
        """"
        Uses Boto3 to retrieve the ARN of a secret from secrets manager.
        """
        LOG.debug("Reading secret for getting ARN,"
                 f" physical resource ID = {physical_resource_id},"
                 f" for aws profile {self.aws_profile_for_logging}")
        client = self._get_aws_client("secretsmanager")
        try:
            secret = client.get_secret_value(SecretId=physical_resource_id)
            return secret["ARN"]
        except botocore.exceptions.ClientError as e:
            LOG.error("Unable to read secret")
            raise e

    def read_dockerhub_secret_arn(self):
        return self.read_secret_arn("Dockerhub")

    @_log_function_start
    def validate_cloudformation_template(self, cloudformation_yml) -> None:
        """
        This function pushes the YAML to AWS Cloudformation for validation
        (see https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-validate-template.html)
        Pitfall: Boto3 expects the YAML string as parameter, whereas the AWS CLI expects the file URL as parameter.
        It requires to have the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables set correctly.
        :required actions: cloudformation:ValidateTemplate
        """
        cloud_client = self._get_aws_client("cloudformation")
        cloud_client.validate_template(TemplateBody=cloudformation_yml)

    def _get_stack_resources(self, stack_name: str) -> List[StackResource]:
        cf_client = self._get_aws_client('cloudformation')
        current_result = cf_client.list_stack_resources(StackName=stack_name)
        result = current_result["StackResourceSummaries"]

        while "nextToken" in current_result:
            current_result = cf_client.list_stack_resources(StackName=stack_name, nextToken=current_result["nextToken"])
            result.extend(current_result["StackResourceSummaries"])
        return [StackResource(stack_resource) for stack_resource in result]

    @_log_function_start
    def get_all_stack_resources(self, stack_name: str) -> List[StackResource]:
        """
        This functions uses Boto3 to get all AWS Cloudformation resources for a specific Cloudformation stack,
        identified by parameter `stack_name`.
        The AWS API truncates at a size of 1MB, and in order to get all chunks the method must be called
        passing the previous retrieved token until no token is returned.
        :required actions: cloudformation:ListStackResources
        """
        return self._get_stack_resources(stack_name=stack_name)

    @_log_function_start
    def stack_exists(self, stack_name: str) -> bool:
        """
        This functions uses Boto3 to check if stack with name `stack_name` exists.
        :required actions: cloudformation:ListStackResources
        """
        try:
            result = self._get_stack_resources(stack_name=stack_name)
            return any([res.status != "DELETE_COMPLETE" for res in result])
        except botocore.exceptions.ClientError:
            return False

    @_log_function_start
    def delete_stack(self, stack_name: str) -> None:
        """
        This functions uses Boto3 to delete a stack identified by parameter "stack_name".
        :required actions: cloudformation:DeleteStack,
                           and all actions required to stop/delete elements of the stack
                           (e.g. ec2:DeleteSecurityGroup, ec2:TerminateInstances,...)
        """
        cf_client = self._get_aws_client('cloudformation')
        cf_client.delete_stack(StackName=stack_name)

    @_log_function_start
    def describe_stacks(self) -> List[CloudformationStack]:
        """
        This functions uses Boto3 to describe all cloudformation stacks.
        :required actions: cloudformation:DescribeStacks
        """
        cf_client = self._get_aws_client('cloudformation')
        current_result = cf_client.describe_stacks()
        result = current_result["Stacks"]

        while "NextToken" in current_result:
            current_result = cf_client.describe_stacks(NextToken=current_result["NextToken"])
            result.extend(current_result["Stacks"])
        return [CloudformationStack(stack) for stack in result]

    @_log_function_start
    def describe_instance(self, instance_id: str) -> EC2Instance:
        """
        Describes an AWS instance identified by parameter instance_id
        :required actions: ec2:DescribeInstances
        """
        cloud_client = self._get_aws_client("ec2")
        instances_result = cloud_client.describe_instances(InstanceIds=[instance_id])
        reservations = instances_result["Reservations"]
        if len(reservations) != 1:
            raise RuntimeError(f"Unexpected number of reservations in describe_instance(): {len(reservations)}")
        instances = reservations[0]["Instances"]
        if len(instances) != 1:
            raise RuntimeError(f"Unexpected number of instances in describe_instance(): {len(instances)}")
        return EC2Instance(instances[0])

    @_log_function_start
    def create_image_from_ec2_instance(self, instance_id: str, name: str, tag_value: str, description: str) -> str:
        """
        Creates an AMI image from an EC-2 instance.
        Returns the image-id of the new AMI.
        :required actions: ec2:CreateImage, ec2:CreateTags
        """
        cloud_client = self._get_aws_client("ec2")
        tags = [{"ResourceType": "image", "Tags": create_default_asset_tag(tag_value)},
                {"ResourceType": "snapshot", "Tags": create_default_asset_tag(tag_value)}]

        result = cloud_client.create_image(Name=name, InstanceId=instance_id, Description=description,
                                           NoReboot=False, TagSpecifications=tags)
        return result["ImageId"]

    @_log_function_start
    def export_ami_image_to_vm(self, image_id: str, tag_value: str,
                               description: str, role_name: str, disk_format: VmDiskImageFormat,
                               s3_bucket: str, s3_prefix: str) -> str:
        """
        Creates an AMI image from an EC-2 instance.
        Returns the export_image_task_id.
        :required actions: ec2:ExportImage, ec2:CreateTags
        """
        cloud_client = self._get_aws_client("ec2")
        tags = [{"ResourceType": "export-image-task", "Tags": create_default_asset_tag(tag_value)}]
        result = cloud_client.export_image(ImageId=image_id, Description=description,
                                           RoleName=role_name, DiskImageFormat=disk_format.value,
                                           S3ExportLocation={"S3Bucket": s3_bucket, "S3Prefix": s3_prefix},
                                           TagSpecifications=tags)

        return result["ExportImageTaskId"]

    @_log_function_start
    def get_export_image_task(self, export_image_task_id: str) -> ExportImageTask:
        """
        Get Export-Image-Task for given export_image_task_id.
        :required actions: ec2:DescribeExportImageTasks
        """
        cloud_client = self._get_aws_client("ec2")
        result = cloud_client.describe_export_image_tasks(ExportImageTaskIds=[export_image_task_id])
        assert "NextToken" not in result  # We expect only one result
        export_image_tasks = result["ExportImageTasks"]
        if len(export_image_tasks) != 1:
            raise RuntimeError(f"Unexpected number of export image tasks: {export_image_tasks}")
        export_image_task = export_image_tasks[0]
        return ExportImageTask(export_image_task)

    @_log_function_start
    def get_ami(self, image_id: str) -> Ami:
        """
        Get AMI image for given image_id
        :required actions: ec2:DescribeImages
        """
        cloud_client = self._get_aws_client("ec2")

        response = cloud_client.describe_images(ImageIds=[image_id])
        images = response["Images"]
        if len(images) != 1:
            raise RuntimeError(f"AwsAccess.get_ami() for image_id='{image_id}' returned {len(images)} elements: {images}")
        return Ami(images[0])

    @_log_function_start
    def get_instance_status(self, instance_id: str) -> EC2InstanceStatus:
        """
        Get EC-2 instance status for given instance_id
        :required actions: ec2:DescribeInstanceStatus
        """
        cloud_client = self._get_aws_client("ec2")

        response = cloud_client.describe_instance_status(InstanceIds=[instance_id])
        instance_statuses = response["InstanceStatuses"]
        if len(instance_statuses) != 1:
            raise RuntimeError(f"AwsAccess.get_instance_status() for instance_id='{instance_id}'"
                               f" returned {len(instance_statuses)} elements: {instance_statuses}")
        return EC2InstanceStatus(instance_statuses[0])

    @_log_function_start
    def list_amis(self, filters: list) -> List[Ami]:
        """
        List AMI images with given tag filter
        :required actions: ec2:DescribeImages
        """
        cloud_client = self._get_aws_client("ec2")
        response = cloud_client.describe_images(Filters=filters)
        return [Ami(ami) for ami in response["Images"]]

    @_log_function_start
    def list_snapshots(self, filters: list) -> List[Snapshot]:
        """
        List EC2 volume snapthos with given tag filter
        :required actions: ec2:DescribeSnapshots
        """
        cloud_client = self._get_aws_client("ec2")

        response = cloud_client.describe_snapshots(Filters=filters)
        assert "NextToken" not in response
        return [Snapshot(snapshot) for snapshot in response["Snapshots"]]

    @_log_function_start
    def list_export_image_tasks(self, filters: list) -> List[ExportImageTask]:
        """
        List export image tasks with given tag filter
        :required actions: ec2:DescribeExportImageTasks
        """
        cloud_client = self._get_aws_client("ec2")

        response = cloud_client.describe_export_image_tasks(Filters=filters)
        assert "NextToken" not in response
        return [ExportImageTask(export_image_task) for export_image_task in response["ExportImageTasks"]]

    @_log_function_start
    def list_ec2_key_pairs(self, filters: list) -> List[KeyPair]:
        """
        List ec-2 key-pairs with given tag filter
        :required actions: ec2:DescribeKeyPairs
        """
        cloud_client = self._get_aws_client("ec2")

        response = cloud_client.describe_key_pairs(Filters=filters)
        assert "NextToken" not in response
        return [KeyPair(keypair) for keypair in response["KeyPairs"]]

    @_log_function_start
    def list_s3_objects(self, bucket: str, prefix: str) -> Optional[List[S3Object]]:
        """
        List s3 objects images with given tag filter
        :required actions: s3:ListBucket
        """
        cloud_client = self._get_aws_client("s3")

        response = cloud_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        if "Contents" in response:
            return [S3Object(s3object) for s3object in response["Contents"]]

    @_log_function_start
    def deregister_ami(self, ami_d: str) -> None:
        """
        De-registers an AMI
        :required actions: ec2:DeregisterImage
        """
        cloud_client = self._get_aws_client("ec2")
        cloud_client.deregister_image(ImageId=ami_d)

    @_log_function_start
    def remove_snapshot(self, snapshot_id: str) -> None:
        """
        Removes a snapshot
        :required actions: ec2:DeleteSnapshot
        """
        cloud_client = self._get_aws_client("ec2")
        cloud_client.delete_snapshot(SnapshotId=snapshot_id)

    @_log_function_start
    def get_user(self) -> str:
        """
        Return the current IAM user name.
        :required actions: iam:GetUser
        """
        iam_client = self._get_aws_client("iam")
        cu = iam_client.get_user()
        return cu["User"]["UserName"]

    @_log_function_start
    def start_codebuild(self, project: str, environment_variables_overrides: List[Dict[str, str]], branch: str) \
            -> Tuple[int, CodeBuildWaiter]:
        """
        This functions uses Boto3 to start a build.
        It forwards all variables from parameter env_variables as environment variables to the CodeBuild project.
        It starts the codebuild for the given branch and then immediately returns the build-id and of the new build
        and a CodeBuildWaiter-object which can be used to wait for the build finish.
        :param project: Codebuild project name to start
        :param environment_variables_overrides: List of environment variables which will be overwritten in build
        :param branch: Branch on which the build will run
        :raises `RuntimeError`: if build fails or AWS Batch build returns unknown status
        :required actions: codebuild:StartBuild
        """
        codebuild_client = self._get_aws_client("codebuild")
        ret_val = codebuild_client.start_build(projectName=project,
                                               sourceVersion=branch,
                                               environmentVariablesOverride=list(
                                                 environment_variables_overrides))
        build_id = ret_val['build']['id']
        LOG.debug(f"Codebuild for project {project} with branch {branch} triggered. Id is {build_id}.")
        return build_id, CodeBuildWaiter(codebuild_client, build_id)

    @_log_function_start
    def modify_image_launch_permission(self, ami_id: str, launch_permissions: Dict[str, Any]):
        """
        This functions uses Boto3 to modify the launch_permissions of an AMI.
        See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.modify_image_attribute
        for details.
        :param ami_id: The AMI id for which the launch permission should be changed.
        :param launch_permissions: Dict of launch permissions
        :required actions: ec2:ModifyImageAttribute
        """
        cloud_client = self._get_aws_client("ec2")
        cloud_client.modify_image_attribute(ImageId=ami_id, LaunchPermission=launch_permissions)

    @_log_function_start
    def copy_s3_object(self, bucket: str, source: str, dest: str):
        """
        This functions uses Boto3 to copy a s3 object within a bucket.
        See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.copy_object
        for details.
        :param bucket: The bucket name where source is located and destination will be located.
        :param source: The source object, including the prefix (e.g. 'path1/path2/src_object')
        :param dest: The destination object, including the prefix (e.g. 'path1/path2/dest_object')
        :required actions: s3:GetObject, s3:PutObject
        """
        cloud_client = self._get_aws_client("s3")
        copy_source = {'Bucket': bucket, 'Key': source}
        cloud_client.copy_object(Bucket=bucket, CopySource=copy_source, Key=dest)

    @_log_function_start
    def delete_s3_object(self, bucket: str, source: str):
        """
        This functions uses Boto3 to delete a s3 object within a bucket.
        See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_object
        for details.
        :param bucket: The bucket name where source is located and destination will be located.
        :param source: The object which will be deleted, including the prefix (e.g. 'path1/path2/src_object')
        :required actions: s3:DeleteObject
        """
        cloud_client = self._get_aws_client("s3")
        cloud_client.delete_object(Bucket=bucket, Key=source)

    def _get_aws_client(self, service_name: str) -> Any:
        if self._aws_profile is None:
            return boto3.client(service_name)
        aws_session = boto3.session.Session(profile_name=self._aws_profile, region_name=self._region)
        return aws_session.client(service_name)

    def instantiate_for_region(self, region: str) -> "AwsAccess":
        """
        Creates a new instance, based on self, but for region indicated by parameter "region"
        :param region: The AWS region on which the new AwsAccess instance will operate.
        """
        return self.__class__(aws_profile=self._aws_profile, region=region)
