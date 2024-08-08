import pytest
import yaml
from unittest.mock import patch, call
from exasol.ds.sandbox.lib.cloudformation_templates import (
    VmBucketCfTemplate,
    ExampleDataCfTemplate,
)


def captcha_rules(rendered_cf_template: str):
    def locate(yml, path):
        rest = yml
        for p in path.split("/"):
            if not p in rest:
                return None
            rest = rest[p]
        return rest or True

    def rules(yml):
        for resource, content in yml["Resources"].items():
            rules = locate(content, "Properties/Rules") or []
            yield from (
                f'{resource}: {r["Name"]}'
                for r in rules
                if locate(r, "Action/Captcha")
            )

    # Replace "!" by "_" to simplily testing. Otherwise the yaml loader would
    # instantiate an arbitrary python object for each "yaml tag" marked with
    # "!", see https://pyyaml.org/wiki/PyYAMLDocumentation#constructors-representers-resolvers
    yml = yaml.safe_load(rendered_cf_template.replace("!", "_"))
    return list(rules(yml))


@pytest.mark.parametrize(
    "cf_template_testee, expected",
    [
        (VmBucketCfTemplate, True),
        (ExampleDataCfTemplate, False),
    ]
)
def test_captcha(test_config, aws_mock, cf_template_testee, expected):
    waf = cf_template_testee(aws_mock).waf(test_config)
    rendered = waf.cloudformation_template(allowed_ip="1.2.3.4")
    actual = True if captcha_rules(rendered) else False
    assert actual == expected
