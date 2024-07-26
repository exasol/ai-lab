import pytest
from test.unit.cli import CliRunner
from exasol.ds.sandbox.cli.commands.setup_s3_bucket import setup_s3_bucket
from unittest.mock import patch
from exasol.ds.sandbox.lib.cloudformation_templates import (
    VmBucketCfTemplate,
    ExampleDataCfTemplate,
)


@pytest.fixture
def cli():
    return CliRunner(setup_s3_bucket)


def test_no_purpose(cli):
    assert cli.run().failed("Missing option '--purpose'")


def test_vm2_bucket(cli):
    with patch.object(VmBucketCfTemplate, 'setup') as setup:
        cli.run("--purpose", "vm")
    assert cli.succeeded()
    setup.assert_called_once()


def test_example_data_bucket(cli):
    with patch.object(ExampleDataCfTemplate, 'setup') as setup:
        cli.run("--purpose", "example-data")
    assert cli.succeeded()
    setup.assert_called_once()
