from unittest.mock import MagicMock

from exasol_script_languages_developer_sandbox.lib.aws_access.ami import Ami
from exasol_script_languages_developer_sandbox.lib.setup_ec2.source_ami import find_source_ami

# The following is just a dump of data returned from aws cli:
# 'aws ec2 --profile exa_individual_mfa describe-images --filters Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-* --owners 099720109477'
mock_data = [
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2020-10-14T16:39:06.000Z",
        "ImageId": "ami-056114420b6ed624e",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20201014",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0dfed1ba04750714c",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2020-10-14",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20201014",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2022-10-14T16:39:06.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2022-03-31T21:03:35.000Z",
        "ImageId": "ami-0d672276deff62a7b",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220331",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-076e6ea4ec3f46bb3",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2022-03-31",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220331",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2024-03-31T21:03:35.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2020-10-27T01:02:32.000Z",
        "ImageId": "ami-0502e817a62226e03",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20201026",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-06c551c41e4bc2f56",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2020-10-26",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20201026",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2022-10-27T01:02:32.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2021-01-09T01:45:55.000Z",
        "ImageId": "ami-0bb75d95f668ff5a7",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210108",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0ed4e5f13a8efbc41",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2021-01-08",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210108",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2023-01-09T01:45:55.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2020-12-03T18:45:56.000Z",
        "ImageId": "ami-064bd5aa0a25234f1",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20201201",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-08ef88ec7a11e3f73",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2020-12-01",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20201201",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2022-12-03T18:45:56.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2021-08-21T00:03:49.000Z",
        "ImageId": "ami-089550b3658b806d5",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210820",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0eba500f0bfd7e08a",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2021-08-20",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210820",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2023-08-21T00:03:49.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2021-04-14T00:57:47.000Z",
        "ImageId": "ami-050c57054a945f865",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210413",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0a286dc481a86d732",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2021-04-13",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210413",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2023-04-14T00:57:47.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2022-03-03T20:20:46.000Z",
        "ImageId": "ami-0ccc52d1499699b6b",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220302",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0fe9c09274bc13f82",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2022-03-02",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220302",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2024-03-03T20:20:46.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2020-09-25T01:16:48.000Z",
        "ImageId": "ami-00caf1798495a2300",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20200924",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0a030876d79c6aff6",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2020-09-24",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20200924",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2022-09-25T01:16:48.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2020-09-04T22:46:25.000Z",
        "ImageId": "ami-05d68e6d48a41210f",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20200903",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0218d3ded1b315754",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2020-09-03",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20200903",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2022-09-04T22:46:25.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2021-05-04T00:36:32.000Z",
        "ImageId": "ami-0e4c7d981c4817239",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210503",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0856978de4f22730c",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2021-05-03",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210503",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2023-05-04T00:36:32.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2021-04-16T05:34:55.000Z",
        "ImageId": "ami-0848da720bb07de35",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210415",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0d5245055e71e7e47",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2021-04-15",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210415",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2023-04-16T05:34:55.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2021-08-25T23:55:00.000Z",
        "ImageId": "ami-0b063c60b220a0574",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210825",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-09f33d01324963fec",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2021-08-25",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210825",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2023-08-25T23:55:00.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2022-06-28T00:51:13.000Z",
        "ImageId": "ami-0d203747b007677da",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220627.1",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0f36ed9157a99fd48",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2022-06-27",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220627.1",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2024-06-28T00:51:13.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2021-09-28T00:25:39.000Z",
        "ImageId": "ami-0afc0414aefc9eaa7",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210927",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0422f57150a61fa5d",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2021-09-27",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210927",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2023-09-28T00:25:39.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2021-02-24T18:24:51.000Z",
        "ImageId": "ami-0767046d1677be5a0",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210223",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-07c3e864b523cd314",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2021-02-23",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210223",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2023-02-24T18:24:51.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2022-05-24T02:07:16.000Z",
        "ImageId": "ami-092f628832a8d22a5",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220523",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0c99b870e2bd583f4",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2022-05-23",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220523",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2024-05-24T02:07:16.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2021-10-16T00:09:47.000Z",
        "ImageId": "ami-0358b49d1ab873c60",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20211015",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0068aa0941bee3086",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2021-10-15",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20211015",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2023-10-16T00:09:47.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2021-03-16T00:50:51.000Z",
        "ImageId": "ami-0dca0d6d4f591c2f4",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210315",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-060b798dc92784a0f",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2021-03-15",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210315",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2023-03-16T00:50:51.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2022-06-10T11:47:47.000Z",
        "ImageId": "ami-0c9354388bb36c088",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220610",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-093bd6f21a1452dac",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2022-06-10",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220610",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2024-06-10T11:47:47.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2022-03-08T23:53:39.000Z",
        "ImageId": "ami-0498a49a15494604f",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220308",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-05b0f8d9dbc9a7d24",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2022-03-08",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220308",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2024-03-08T23:53:39.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2020-09-08T00:56:08.000Z",
        "ImageId": "ami-0c960b947cbb2dd16",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20200907",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0e55257c35999fffb",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2020-09-07",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20200907",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2022-09-08T00:56:08.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2022-04-05T00:51:16.000Z",
        "ImageId": "ami-0ca64d1b4e674f837",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220404",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0e2aa065b7002c40e",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2022-04-04",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220404",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2024-04-05T00:51:16.000Z"
    }),
    Ami({
        "Architecture": "x86_64",
        "CreationDate": "2020-09-17T16:24:38.000Z",
        "ImageId": "ami-052eaddc8881bf2ec",
        "ImageLocation": "099720109477/ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20200916",
        "ImageType": "machine",
        "Public": True,
        "OwnerId": "099720109477",
        "PlatformDetails": "Linux/UNIX",
        "UsageOperation": "RunInstances",
        "State": "available",
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "DeleteOnTermination": True,
                    "SnapshotId": "snap-0a31b4b0ef89e280e",
                    "VolumeSize": 8,
                    "VolumeType": "gp2",
                    "Encrypted": False
                }
            },
            {
                "DeviceName": "/dev/sdb",
                "VirtualName": "ephemeral0"
            },
            {
                "DeviceName": "/dev/sdc",
                "VirtualName": "ephemeral1"
            }
        ],
        "Description": "Canonical, Ubuntu, 20.04 LTS, amd64 focal image build on 2020-09-16",
        "EnaSupport": True,
        "Hypervisor": "xen",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20200916",
        "RootDeviceName": "/dev/sda1",
        "RootDeviceType": "ebs",
        "SriovNetSupport": "simple",
        "VirtualizationType": "hvm",
        "DeprecationTime": "2022-09-17T16:24:38.000Z"
    }),
]


def test_find_source_ami_returns_latest_ami(test_config):
    """
    Test that find_source_ami returns the latest AMI image based on the filters given in the global config.
    """
    aws_mock = MagicMock()
    aws_mock.list_amis.return_value = mock_data
    latest_ami = find_source_ami(aws_mock, test_config.source_ami_filters)
    # ami-0d203747b007677da is the latest one in the mock data
    assert latest_ami.id == "ami-0d203747b007677da"

