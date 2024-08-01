import pytest
from typing import Union
from unittest.mock import Mock, create_autospec
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.cloudformation_templates.cf_template import CfTemplateSpec


@pytest.fixture
def aws_mock() -> Union[AwsAccess, Mock]:
    return create_autospec(AwsAccess, spec_set=True)


@pytest.fixture
def cf_template_spec():
    return CfTemplateSpec(
        "my_stack_name",
        template="cloudformation/vm-images/s3-bucket.jinja.yaml",
        outputs={
            "a": "aa",
            "b": "bb",
        },
    )
