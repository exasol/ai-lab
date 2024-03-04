from unittest.mock import MagicMock

from exasol.ds.sandbox.lib.setup_ec2.cf_stack import (
    CloudformationStack,
    CloudformationStackContextManager,
)
from exasol.ds.sandbox.lib.tags import create_default_asset_tag


def test_deploy_ec2_upload_invoked(ec2_cloudformation_yml, default_asset_id, test_dummy_ami_id):
    """"
    Test if function upload_cloudformation_stack() will be invoked with
    expected values when we run run_deploy_ci_build()
    """
    aws = MagicMock()
    with CloudformationStackContextManager(
            CloudformationStack(
                aws,
                "test_key",
                "test_user",
                default_asset_id,
                test_dummy_ami_id,
            )) as cloudformation:
        pass
    default_tag = tuple(create_default_asset_tag(default_asset_id.tag_value))
    aws.upload_cloudformation_stack.assert_called_once_with(
        ec2_cloudformation_yml,
        cloudformation.stack_name,
        tags=default_tag,
    )


def test_deploy_ec2_custom_prefix(ec2_cloudformation_yml, default_asset_id, test_dummy_ami_id):
    """"
    Test that the custom prefix will be used for the cloudformation stack name.
    """
    aws = MagicMock()
    aws.stack_exists.return_value = False
    with CloudformationStackContextManager(
            CloudformationStack(
                aws,
                "test_key",
                "test_user",
                default_asset_id,
                test_dummy_ami_id,
            )) as cloudformation:
        assert cloudformation.stack_name.startswith("test-stack")
