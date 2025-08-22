import re
from typing import NamedTuple, Tuple
from unittest.mock import Mock

import pytest
from exasol.ds.sandbox.lib.aws_access.ami import Ami
from exasol.ds.sandbox.lib.setup_ec2.source_ami import AmiFinder, FindAmiError


class AmiSpec(NamedTuple):
    date: str
    id: str


# The following is based on a dump of data returned from aws cli:
# aws ec2 --profile exa_individual_mfa describe-images
# --owners 099720109477
# --filters Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*

AMI_SPECS = [
    AmiSpec("2020-10-14", "ami-056114420b6ed624e"),
    AmiSpec("2022-03-31", "ami-0d672276deff62a7b"),
    AmiSpec("2022-06-28", "ami-0d203747b007677da"),
    AmiSpec("2022-06-10", "ami-0c9354388bb36c088"),
]


@pytest.fixture(scope="session")
def sample_amis():
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

    return [ami(spec) for spec in AMI_SPECS]


@pytest.fixture(scope="session")
def aws_mock(sample_amis):
    def mock_list_amis(filters: list[dict[str, str | list[str]]]) -> list[Ami]:
        def matches(ami: Ami) -> bool:
            for f in filters:
                key = f["Name"]
                att = key.title().replace("-", "")
                for crit in f["Values"]:
                    regex = crit.replace("*", ".*")
                    value = ami._aws_object[att]
                    if not re.match(regex, value):
                        return False
            return True

        return [ami for ami in sample_amis if matches(ami)]

    return Mock(list_amis=mock_list_amis)


@pytest.fixture
def sample_finder(aws_mock, test_config) -> AmiFinder:
    return AmiFinder(aws_mock, test_config.source_ami_filters)


def test_unique(sample_finder):
    id = "ami-0c9354388bb36c088"
    ami = sample_finder.find(id)
    assert ami.id == id


def test_unique_failure(sample_finder):
    with pytest.raises(FindAmiError):
        sample_finder.find("non-existing-id")


def test_latest(sample_finder):
    """
    Test that AmiFinder.latest() returns the latest AMI image based on the
    filters given in the global config.
    """
    ami = sample_finder.find(None)
    # ami-0d203747b007677da is the latest one in the mock data
    assert ami.id == "ami-0d203747b007677da"


def test_latest_failure(aws_mock):
    filters = {
        "name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*",
    }
    finder = AmiFinder(aws_mock, filters)
    with pytest.raises(FindAmiError):
        finder.find(None)
