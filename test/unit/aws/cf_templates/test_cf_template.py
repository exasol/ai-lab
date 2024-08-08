import pytest
from typing import List, Tuple
from unittest.mock import Mock, patch

from jinja2.exceptions import UndefinedError
from jinja2 import StrictUndefined
import jinja2

from exasol.ds.sandbox.lib.cloudformation_templates import CfTemplate
from test.aws.mock_data import mock_stack


@pytest.fixture
def cf_template(aws_mock, cf_template_spec):
    yield CfTemplate(aws_mock, cf_template_spec)


class MyRenderer:
    def __init__(self, template_content: str):
        self._template_content = template_content

    def render(self, template: str, **kwargs):
        env = jinja2.Environment(
            autoescape=jinja2.select_autoescape(),
            keep_trailing_newline=True,
            undefined=StrictUndefined,
        )
        t = env.from_string(self._template_content)
        return f"{template}: " + t.render(**kwargs)


def test_stack_name(cf_template):
    assert cf_template.stack_name == "my_stack_name"


def test_render_missing_param(cf_template):
    cf_template._template_renderer = MyRenderer("x={{x}} {{a}}=1 {{b}}=2")
    with pytest.raises(UndefinedError, match="'x' is undefined") as ex:
        cf_template.cloudformation_template()


def test_render_success(cf_template):
    cf_template._template_renderer = MyRenderer("x={{x}} {{a}}=1 {{b}}=2")
    actual = cf_template.cloudformation_template(x="0")
    assert "cloudformation/vm-images/s3-bucket.jinja.yaml: x=0 aa=1 bb=2" == actual


def test_setup(aws_mock, cf_template_spec):
    testee = CfTemplate(aws_mock, cf_template_spec)
    with patch.object(CfTemplate, "cloudformation_template") as mock:
        testee.setup(x="0")
    assert mock.called
    assert aws_mock.upload_cloudformation_stack.called


def test_stack_output_stack_not_found(aws_mock, cf_template_spec):
    testee = CfTemplate(aws_mock, cf_template_spec)
    aws_mock.describe_stacks.return_value = [
        mock_stack("other_stack_name", [("aa", "11"),])
    ]
    with pytest.raises(RuntimeError, match="Stack my_stack_name not found"):
        testee.stack_output("a")


@pytest.mark.parametrize("mnemonic", ("a", "b"))
def test_stack_output_key_not_found(aws_mock, cf_template_spec, mnemonic):
    testee = CfTemplate(aws_mock, cf_template_spec)
    aws_mock.describe_stacks.return_value = [
        mock_stack("my_stack_name", [("bb", "21"), ("bb", "22")]),
    ]
    with pytest.raises(RuntimeError, match="Output key .* not found or non-uniq"):
        testee.stack_output(mnemonic)


def test_stack_output_success(aws_mock, cf_template_spec):
    testee = CfTemplate(aws_mock, cf_template_spec)
    aws_mock.describe_stacks.return_value = [
        mock_stack("my_stack_name", [("aa", "11")]),
    ]
    assert "11" == testee.stack_output("a")
