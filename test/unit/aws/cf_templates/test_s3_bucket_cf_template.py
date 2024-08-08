import pytest
from unittest.mock import patch, call
from exasol.ds.sandbox.lib.cloudformation_templates import (
    CfTemplateSpec,
    CfTemplate,
    S3BucketCfTemplate,
)

from test.aws.mock_data import mock_stack

@pytest.fixture
def waf_cf_template_spec():
    return CfTemplateSpec(
        "waf_stack_name",
        template="cloudformation/vm-images/waf.jinja.yaml",
        outputs={
            "DownloadACLArn": "aaa",
        },
    )


@pytest.fixture
def s3_bucket_cf_template(aws_mock, cf_template_spec, waf_cf_template_spec):
    return S3BucketCfTemplate(aws_mock, cf_template_spec, waf_cf_template_spec)


def test_setup(test_config, aws_mock, cf_template_spec, waf_cf_template_spec):
    aws_mock.describe_stacks.return_value = [
        mock_stack("waf_stack_name", [("aaa", "vv"),])
    ]
    testee = S3BucketCfTemplate(aws_mock, cf_template_spec, waf_cf_template_spec)
    aws_mock.instantiate_for_region.return_value = aws_mock
    with patch.object(CfTemplate, "setup") as mock:
        testee.setup(test_config)
    assert mock.call_args == call(acl_arn='vv', path_in_bucket='ai_lab')
    assert aws_mock.instantiate_for_region.call_args == call("us-east-1")
