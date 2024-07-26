import pytest
from test.unit.cli import CliRunner
from exasol.ds.sandbox.cli.commands.setup_waf import setup_waf
from unittest.mock import patch
from exasol.ds.sandbox.lib.cloudformation_templates import (
    VmBucketCfTemplate,
    ExampleDataCfTemplate,
    WafCfTemplate,
)


@pytest.fixture
def cli():
    return CliRunner(setup_waf)


def test_no_purpose(cli):
    assert cli.run().failed("Missing option '--purpose'")


def test_vm_bucket(cli):
    with patch.object(VmBucketCfTemplate, 'waf') as waf:
        cli.run("--purpose", "vm")
    assert cli.succeeded()
    waf.assert_called_once()


def test_example_data_bucket(cli):
    with patch.object(ExampleDataCfTemplate, 'waf') as waf:
        cli.run("--purpose", "example-data")
    assert cli.succeeded()
    waf.assert_called_once()


@pytest.mark.parametrize("purpose", ("vm", "example-data"))
def test_waf_setup(cli, purpose):
    with patch.object(WafCfTemplate, 'setup') as setup:
        cli.run("--purpose", purpose)
    assert cli.succeeded()
    setup.assert_called_once()
