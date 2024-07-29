import pytest
from test.unit.cli import CliRunner
from exasol.ds.sandbox.cli.commands.setup_waf import setup_waf
from unittest.mock import patch, call
from exasol.ds.sandbox.lib.cloudformation_templates import (
    VmBucketCfTemplate,
    ExampleDataCfTemplate,
    WafCfTemplate,
)


@pytest.fixture
def cli():
    """
    To prevent accidentally creating actual AWS resources, the fixture
    tells the CliRunner to use an invalid AWS profile.
    """
    return CliRunner(setup_waf, env={"AWS_PROFILE": "invalid-profile"})


def test_no_purpose(cli):
    assert cli.run().failed
    assert "Missing option '--purpose'" in cli.output


def test_vm_bucket(cli):
    with patch.object(VmBucketCfTemplate, "waf") as waf:
        cli.run("--purpose", "vm")
    assert cli.succeeded and waf.call_count == 1


def test_example_data_bucket(cli):
    with patch.object(ExampleDataCfTemplate, "waf") as waf:
        cli.run("--purpose", "example-data")
    assert cli.succeeded and waf.call_count == 1


@pytest.mark.parametrize("purpose", ("vm", "example-data"))
def test_waf_setup(cli, purpose):
    with patch.object(WafCfTemplate, "setup") as setup:
        cli.run("--purpose", purpose)
    assert cli.succeeded and setup.call_count == 1
