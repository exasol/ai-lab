from typing import NamedTuple
from unittest.mock import Mock

import pytest
from exasol.ds.sandbox.lib.aws_access.ami import Ami
from exasol.ds.sandbox.lib.setup_ec2.source_ami import AmiFinder, FindAmiError


class AmiSpec(NamedTuple):
    date: str
    id: str


def aws_mock(specs: list[AmiSpec]) -> Mock:
    def ami(spec: AmiSpec):
        suffix = spec.date.replace("-", "")
        return Ami({
            "Architecture": "x86_64",
            "CreationDate": f"{spec.date}T16:39:06.000Z",
            "ImageId": spec.id,
            "OwnerId": "099720109477",
            "State": "available",
            "Name": f"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-{suffix}",
        })

    aws = Mock()
    aws.list_amis.return_value = [ami(spec) for spec in specs]
    return aws


@pytest.fixture
def finder_without_amis(test_config) -> AmiFinder:
    return AmiFinder(aws_mock([]), test_config.source_ami_filters)


def test_unique_success(test_config):
    spec = AmiSpec("2022-06-10", "ami-0c9354388bb36c088")
    testee = AmiFinder(aws_mock([spec]), test_config.source_ami_filters)
    ami = testee.find(spec.id)
    assert ami.id == spec.id


def test_unique_no_ami_found(finder_without_amis):
    with pytest.raises(FindAmiError, match="Couldn't find any AMI"):
        finder_without_amis.find("non-existing-id")


def test_unique_multiple_amis_found(test_config):
    duplicate_id = "ami-0d672276deff62a7b"
    specs = [
        AmiSpec("2020-10-14", duplicate_id),
        AmiSpec("2022-03-31", duplicate_id),
    ]
    aws = aws_mock(specs)
    testee = AmiFinder(aws, test_config.source_ami_filters)
    with pytest.raises(FindAmiError, match="Found more than one"):
        testee.find(duplicate_id)


def test_latest_success(test_config):
    """
    Test that AmiFinder.latest() returns the latest AMI image based on the
    filters given in the global config.

    The list is based on a dump of data returned from aws cli:
    aws ec2 --profile exa_individual_mfa describe-images \
      --owners 099720109477 \
      --filters Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*
    """
    latest_ami = AmiSpec("2022-06-28", "ami-0d203747b007677da")
    specs = [
        AmiSpec("2020-10-14", "ami-056114420b6ed624e"),
        AmiSpec("2022-03-31", "ami-0d672276deff62a7b"),
        latest_ami,
        AmiSpec("2022-06-10", "ami-0c9354388bb36c088"),
    ]
    aws = aws_mock(specs)
    testee = AmiFinder(aws, test_config.source_ami_filters)
    ami = testee.find(None)
    assert ami.id == latest_ami.id


def test_latest_failure(finder_without_amis):
    with pytest.raises(FindAmiError):
        finder_without_amis.find(None)
