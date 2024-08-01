import pytest
from unittest.mock import patch, call
from exasol.ds.sandbox.lib.cloudformation_templates import (
    CfTemplate,
    WafCfTemplate,
)

@pytest.fixture
def waf_cf_template(aws_mock, cf_template_spec):
    return WafCfTemplate(aws_mock, cf_template_spec, "some region")


def test_region(aws_mock, cf_template_spec):
    testee = WafCfTemplate(aws_mock, cf_template_spec, "northpole region")
    assert aws_mock.instantiate_for_region.called


def test_setup(waf_cf_template):
    with patch.object(CfTemplate, "setup") as mock:
        waf_cf_template.setup(allowed_ip=None)
    assert mock.call_args == call(allowed_ip='127.0.0.1')


def test_acl_arn(waf_cf_template):
    with patch.object(CfTemplate, "stack_output") as mock:
        waf_cf_template.acl_arn
    assert mock.call_args == call("DownloadACLArn")
