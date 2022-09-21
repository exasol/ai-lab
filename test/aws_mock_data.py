import datetime
from typing import List

from dateutil.tz import tzutc

from exasol_script_languages_developer_sandbox.lib.aws_access.ami import Ami
from exasol_script_languages_developer_sandbox.lib.aws_access.cloudformation_stack import CloudformationStack
from exasol_script_languages_developer_sandbox.lib.aws_access.export_image_task import ExportImageTask
from exasol_script_languages_developer_sandbox.lib.aws_access.key_pair import KeyPair
from exasol_script_languages_developer_sandbox.lib.aws_access.s3_object import S3Object
from exasol_script_languages_developer_sandbox.lib.aws_access.snapshot import Snapshot
from exasol_script_languages_developer_sandbox.lib.aws_access.stack_resource import StackResource
from exasol_script_languages_developer_sandbox.lib.vm_bucket.vm_slc_bucket import STACK_NAME
from test.conftest import DEFAULT_ASSET_ID

TEST_ROLE_ID = 'VM-SLC-Bucket-VMImportRole-TEST'
TEST_BUCKET_ID = 'vm-slc-bucket-vmslcbucket-TEST'
TEST_AMI_ID = "AMI-IMAGE-12345"
TEST_CLOUDFRONT_ID = "test-cloudfrontet-TEST"
TEST_CLOUDFRONT_DOMAIN_NAME = "test-s3.cloudfront.net"
INSTANCE_ID = "test-instance"


def get_vm_bucket_cloudformation_mock_data():
    # The following is a snapshot from calling AwsAccess(a).get_all_stack_resources("VM-SLC-Bucket") on a running
    # cloudformation stack
    return [StackResource({'LogicalResourceId': 'VMImportRole',
                           'PhysicalResourceId': TEST_ROLE_ID,
                           'ResourceType': 'AWS::IAM::Role',
                           'LastUpdatedTimestamp': datetime.datetime(2022, 8, 11, 17, 15, 20, 380000, tzinfo=tzutc()),
                           'ResourceStatus': 'CREATE_COMPLETE',
                           'DriftInformation': {'StackResourceDriftStatus': 'NOT_CHECKED'}}),
            StackResource({'LogicalResourceId': 'VMSLCBucket',
                           'PhysicalResourceId': TEST_BUCKET_ID,
                           'ResourceType': 'AWS::S3::Bucket',
                           'LastUpdatedTimestamp': datetime.datetime(2022, 8, 11, 17, 14, 55, 63000, tzinfo=tzutc()),
                           'ResourceStatus': 'CREATE_COMPLETE',
                           'DriftInformation': {'StackResourceDriftStatus': 'NOT_CHECKED'}})
            ]


def get_only_vm_stack_side_effect(stack_name: str):
    if stack_name == STACK_NAME:
        return get_vm_bucket_cloudformation_mock_data()
    else:
        raise ValueError(f"Unexpected parameter:{stack_name}")


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
                'Tags': [{'Key': 'exa_slc_id', 'Value': DEFAULT_ASSET_ID.tag_value}],
                'VirtualizationType': 'hvm'})


def get_snapshot_mock_data():
    return Snapshot({
        'Description': 'Created by foo', 'Encrypted': False,
        'OwnerId': '123', 'Progress': '100%', 'SnapshotId': 'snap-123',
        'StartTime': datetime.datetime(2022, 8, 16, 15, 3, 40, 662000, tzinfo=tzutc()), 'State': 'completed',
        'VolumeId': 'vol-123', 'VolumeSize': 100,
        'Tags': [{'Key': 'exa_slc_id', 'Value': DEFAULT_ASSET_ID.tag_value}],
        'StorageTier': 'standard'
    })


def get_export_image_task_mock_data(in_progress: bool):
    if in_progress:
        return ExportImageTask({
            'Description': 'VM Description',
            'ExportImageTaskId': 'export-ami-123',
            'S3ExportLocation':
                {
                    'S3Bucket': '123/some_dummy_location',
                    'S3Prefix': DEFAULT_ASSET_ID.bucket_prefix
                },
            'Progress': "50%",
            "StatusMessage": "creating the image",
            'Status': 'active',
            'Tags': [{'Key': 'exa_slc_id', 'Value': DEFAULT_ASSET_ID.tag_value}]
        })
    else:
        return ExportImageTask({
            'Description': 'VM Description',
            'ExportImageTaskId': 'export-ami-123',
            'S3ExportLocation':
                {
                    'S3Bucket': '123/some_dummy_location',
                    'S3Prefix': DEFAULT_ASSET_ID.bucket_prefix
                },
            'Status': 'completed',
            'Tags': [{'Key': 'exa_slc_id', 'Value': DEFAULT_ASSET_ID.tag_value}]
        })


def get_s3_object_mock_data():
    return S3Object({
        'Key': f'{DEFAULT_ASSET_ID.bucket_prefix}/export-ami-123.vmdk',
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
        'Tags': [{'Key': 'exa_slc_id', 'Value': DEFAULT_ASSET_ID.tag_value}],
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
        'Tags': [{'Key': 'exa_slc_id', 'Value': DEFAULT_ASSET_ID.tag_value}],
        'CreateTime': datetime.datetime(2022, 8, 16, 15, 30, 41,
                                        tzinfo=tzutc())
    })


def get_s3_cloudformation_mock_data() -> List[CloudformationStack]:
    return [CloudformationStack({
        'StackId': 'test-s3-stack-id',
        'StackName': "DEVELOPER-SANDBOX-VM-SLC-Bucket",
        'ChangeSetId': 'test-stack-changeset-id-2',
        'CreationTime': datetime.datetime(2022, 8, 16, 14, 30, 45, 559000, tzinfo=tzutc()),
        'LastUpdatedTime': datetime.datetime(2022, 8, 16, 14, 30, 51, 667000, tzinfo=tzutc()),
        'RollbackConfiguration': {},
        'StackStatus': 'CREATE_COMPLETE',
        'DisableRollback': False, 'NotificationARNs': [], 'Capabilities': ['CAPABILITY_IAM'],
        'Tags': [{'Key': 'exa_slc_id', 'Value': DEFAULT_ASSET_ID.tag_value}],
        'DriftInformation': {'StackDriftStatus': 'NOT_CHECKED'},
        'Outputs': [{'OutputKey': 'VMBucketId',
                     'OutputValue': TEST_BUCKET_ID, 'Description': ''},
                    {'OutputKey': 'VMExportRoleId',
                     'OutputValue': TEST_ROLE_ID, 'Description': ''},
                    {'OutputKey': 'CfDistributionId',
                     'OutputValue': TEST_CLOUDFRONT_ID, 'Description': ''},
                    {'OutputKey': 'CfDistributionDomainName',
                     'OutputValue': TEST_CLOUDFRONT_DOMAIN_NAME, 'Description': ''}
                    ]
        })
    ]
