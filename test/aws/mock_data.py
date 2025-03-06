import datetime
from typing import Dict, List, Tuple
from unittest.mock import Mock

from dateutil.tz import tzutc

from exasol.ds.sandbox.lib.aws_access.ami import Ami
from exasol.ds.sandbox.lib.aws_access.cloudformation_stack import CloudformationStack
from exasol.ds.sandbox.lib.aws_access.export_image_task import ExportImageTask
from exasol.ds.sandbox.lib.aws_access.key_pair import KeyPair
from exasol.ds.sandbox.lib.aws_access.s3_object import S3Object
from exasol.ds.sandbox.lib.aws_access.snapshot import Snapshot
from exasol.ds.sandbox.lib.aws_access.stack_resource import StackResource
from exasol.ds.sandbox.lib.tags import create_default_asset_tag
from test.aws.templates import DEFAULT_ASSET_ID
from test.aws.templates import TEST_ACL_ARN

TEST_ROLE_ID = 'VM-DSS-Bucket-VMImportRole-TEST'
TEST_BUCKET_ID = 'vm-dss-bucket-vmdssbucket-TEST'
TEST_AMI_ID = "AMI-IMAGE-12345"
TEST_CLOUDFRONT_ID = "test-cloudfrontet-TEST"
TEST_CLOUDFRONT_DOMAIN_NAME = "test-s3.cloudfront.net"
INSTANCE_ID = "test-instance"
VM_BUCKET_OUTPUTS = {
    "VMBucketId": TEST_BUCKET_ID,
    "VMExportRoleId": TEST_ROLE_ID,
    "CfDistributionId": TEST_CLOUDFRONT_ID,
    "CfDistributionDomainName": TEST_CLOUDFRONT_DOMAIN_NAME,
}
EXAMPLE_DATA_BUCKET_HTTP_OUTPUTS = {
    "ExampleDataBucketId": TEST_BUCKET_ID,
    "ExportRoleId": TEST_ROLE_ID,
    "CfDistributionId": TEST_CLOUDFRONT_ID,
    "CfDistributionDomainName": TEST_CLOUDFRONT_DOMAIN_NAME,
}
EXAMPLE_DATA_BUCKET_S3_OUTPUTS = {
    "ExampleDataBucketId": TEST_BUCKET_ID,
}
VM_BUCKET_WAF_OUTPUTS = { 'VMDownloadACLArn': TEST_ACL_ARN }
EXAMPLE_DATA_WAF_OUTPUTS = { 'AiLabExampleDataDownloadACLArn': TEST_ACL_ARN }


def default_tags() -> List[Dict[str, str]]:
    return create_default_asset_tag(DEFAULT_ASSET_ID.tag_value)


def get_ami_image_mock_data(state: str) -> Ami:
    return Ami({'Architecture': 'x86_64',
                'CreationDate': '2022-08-16T15:02:10.000Z',
                'ImageId': TEST_AMI_ID,
                'ImageLocation': '123/some_dummy_location',
                'ImageType': 'machine', 'Public': False, 'OwnerId': '123',
                'PlatformDetails': 'Linux/UNIX',
                'UsageOperation': 'RunInstances',
                'State': state,
                'BlockDeviceMappings':
                    [{'DeviceName': '/dev/sda1',
                      'Ebs':
                          {'DeleteOnTermination': True, 'SnapshotId': 'snap-0e4b4dcef3f806d84',
                           'VolumeSize': 100, 'VolumeType': 'gp2', 'Encrypted': False}
                      },
                     {'DeviceName': '/dev/sdb', 'VirtualName': 'ephemeral0'},
                     {'DeviceName': '/dev/sdc', 'VirtualName': 'ephemeral1'}],
                'Description': 'Image Description', 'EnaSupport': True,
                'Hypervisor': 'xen',
                'Name': DEFAULT_ASSET_ID.ami_name,
                'RootDeviceName': '/dev/sda1',
                'RootDeviceType': 'ebs', 'SriovNetSupport': 'simple',
                'Tags': default_tags(),
                'VirtualizationType': 'hvm'})


def get_snapshot_mock_data():
    return Snapshot({
        'Description': 'Created by foo', 'Encrypted': False,
        'OwnerId': '123', 'Progress': '100%', 'SnapshotId': 'snap-123',
        'StartTime': datetime.datetime(2022, 8, 16, 15, 3, 40, 662000, tzinfo=tzutc()), 'State': 'completed',
        'VolumeId': 'vol-123', 'VolumeSize': 100,
        'Tags': default_tags(),
        'StorageTier': 'standard'
    })


def get_export_image_task_mock_data(in_progress: bool):
    if in_progress:
        return ExportImageTask({
            'Description': 'VM Description',
            'ExportImageTaskId': 'export-ami-123',
            'S3ExportLocation':
                {
                    'S3Bucket': TEST_BUCKET_ID,
                    'S3Prefix': DEFAULT_ASSET_ID.bucket_prefix
                },
            'Progress': "50%",
            "StatusMessage": "creating the image",
            'Status': 'active',
            'Tags': default_tags(),
        })
    else:
        return ExportImageTask({
            'Description': 'VM Description',
            'ExportImageTaskId': 'export-ami-123',
            'S3ExportLocation':
                {
                    'S3Bucket': TEST_BUCKET_ID,
                    'S3Prefix': DEFAULT_ASSET_ID.bucket_prefix
                },
            'Status': 'completed',
            'Tags': default_tags()
        })


def get_s3_object_mock_data(suffix: str = "vmdk"):
    return S3Object({
        'Key': f'{DEFAULT_ASSET_ID.bucket_prefix}/export-ami-123.{suffix}',
        'LastModified': datetime.datetime(2022, 8, 15, 11, 14, 4, tzinfo=tzutc()),
        'ETag': '"32555a13671cd66c04959366c579b09b-209"',
        'Size': 2185813504,
        'StorageClass': 'STANDARD'
    })


def get_ec2_cloudformation_mock_data():
    return CloudformationStack({
        'StackId': 'test-stack-id',
        'StackName': 'test-stack-name',
        'ChangeSetId': 'test-stack-changeset-id-1',
        'CreationTime': datetime.datetime(2022, 8, 16, 14, 30, 45, 559000, tzinfo=tzutc()),
        'LastUpdatedTime': datetime.datetime(2022, 8, 16, 14, 30, 51, 667000, tzinfo=tzutc()),
        'RollbackConfiguration': {},
        'StackStatus': 'CREATE_COMPLETE',
        'DisableRollback': False, 'NotificationARNs': [], 'Capabilities': ['CAPABILITY_IAM'],
        'Tags': default_tags(),
        'DriftInformation': {'StackDriftStatus': 'NOT_CHECKED'}
    })


def get_ec2_cloudformation_stack_resources_mock_data():
    return [
        StackResource({'LogicalResourceId': 'EC2Instance',
                       'PhysicalResourceId': 'ec2-instance-123',
                       'ResourceType': 'AWS::EC2::Instance',
                       'LastUpdatedTimestamp': datetime.datetime(2022, 8, 16, 14, 31, 35, 929000, tzinfo=tzutc()),
                       'ResourceStatus': 'CREATE_COMPLETE',
                       'DriftInformation': {'StackResourceDriftStatus': 'NOT_CHECKED'}
                       }),
        StackResource({'LogicalResourceId': 'Ec2SecurityGroup',
                       'PhysicalResourceId': 'ec2-security-group-123',
                       'ResourceType': 'AWS::EC2::SecurityGroup',
                       'LastUpdatedTimestamp': datetime.datetime(2022, 8, 16, 14, 31, 0, 224000, tzinfo=tzutc()),
                       'ResourceStatus': 'CREATE_COMPLETE',
                       'DriftInformation': {'StackResourceDriftStatus': 'NOT_CHECKED'}
                       })
    ]


def get_ec2_key_pair_mock_data():
    return KeyPair({
        'KeyPairId': 'key-123',
        'KeyFingerprint': '12:34:56:78:90:12:34:56:78:90:12:34:56:78:90:12:34:56:78:90',
        'KeyName': 'ec2-key-test-key',
        'KeyType': 'rsa',
        'Tags': default_tags(),
        'CreateTime': datetime.datetime(2022, 8, 16, 15, 30, 41, tzinfo=tzutc())
    })


def mock_outputs(output_values: Dict[str, str]):
    def transform(k, v):
        return {
            "OutputKey": k,
            "OutputValue": v,
            "Description": "n/a",
        }
    return [ transform(k, v) for k, v in output_values.items() ]


def cf_stack_mock_data(stack_name: str, outputs: Dict[str, str]) -> Dict[str, any]:
    created = datetime.datetime(2022, 8, 16, 14, 30, 45, 559000, tzinfo=tzutc())
    last_update = datetime.datetime(2022, 8, 16, 14, 30, 51, 667000, tzinfo=tzutc())
    return {
        'StackId': 'test-stack-id',
        'StackName': stack_name,
        'ChangeSetId': 'test-stack-changeset-id',
        'CreationTime': created,
        'LastUpdatedTime': last_update,
        'RollbackConfiguration': {},
        'StackStatus': 'CREATE_COMPLETE',
        'DisableRollback': False, 'NotificationARNs': [], 'Capabilities': ['CAPABILITY_IAM'],
        'Tags': default_tags(),
        'DriftInformation': {'StackDriftStatus': 'NOT_CHECKED'},
        'Outputs': mock_outputs(outputs)
    }


def cf_stack_mock(stack_name: str, outputs: Dict[str, str]) -> List[CloudformationStack]:
    return [
        CloudformationStack(cf_stack_mock_data(stack_name, outputs))
    ]


def get_s3_cloudformation_mock_data() -> List[CloudformationStack]:
    return cf_stack_mock("DATA-SCIENCE-SANDBOX-VM-Bucket", VM_BUCKET_OUTPUTS)


def get_waf_cloudformation_mock_data() -> List[CloudformationStack]:
    return cf_stack_mock(
        "DATA-SCIENCE-SANDBOX-VM-Bucket-WAF",
        VM_BUCKET_WAF_OUTPUTS,
    )


def mock_stack(name: str, outputs: List[Tuple[str, str]]):
    stack = Mock(outputs=[
        Mock(output_key=k, output_value=v)
        for k,v in outputs
    ])
    stack.configure_mock(name=name)
    return stack
