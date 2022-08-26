from typing import Optional

from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.logging import get_status_logger, LogType
from exasol_script_languages_developer_sandbox.lib.setup_ec2.random_string_generator import get_random_str_of_length_n
from exasol_script_languages_developer_sandbox.lib.render_template import render_template
from exasol_script_languages_developer_sandbox.lib.tags import DEFAULT_TAG_KEY, create_default_asset_tag

_MAX_ATTEMPTS_TO_FIND_STACK_NAME = 3

LOG = get_status_logger(LogType.SETUP)


def find_ec2_instance_in_cf_stack(aws_access: AwsAccess, stack_name: str) -> str:
    stack_resources = aws_access.get_all_stack_resources(stack_name)
    ec2_instance = [i for i in stack_resources if i.is_ec2_instance]
    if len(ec2_instance) == 0:
        raise RuntimeError("Error starting or retrieving ec2 instance of stack %s" % stack_name)
    elif len(ec2_instance) > 1:
        raise RuntimeError("Multiple ec2 instances of stack %s" % stack_name)
    ec2_instance_id = ec2_instance[0].physical_id
    LOG.info(f"Started EC2 with physical id {ec2_instance_id}")
    return ec2_instance_id


class CloudformationStack:
    """
    This class provides instantiation and destruction  of an AWS Cloudformation stack.
    It is implemented as ContextManager, so that if it enters the context, the instance will be created,
    and when exiting the stack will be destroyed.
    """

    def __init__(self, aws_access: AwsAccess, ec2_key_name: str, user_name: str, stack_prefix: Optional[str],
                 tag_value: str, ami_id: str):
        self._aws_access = aws_access
        self._stack_name = None
        self._ec2_key_name = ec2_key_name
        self._user_name = user_name
        self._stack_prefix = stack_prefix or "EC2-SLC-DEV-SANDBOX-"
        self._tag_value = tag_value
        self._ami_id = ami_id

    def _generate_stack_name(self) -> str:
        """
        Create a new stack name. We append a random number as suffix,
        so that in theory multiple instances can be created.
        """

        return f"{self._stack_prefix}{get_random_str_of_length_n(5)}"

    @property
    def stack_name(self) -> Optional[str]:
        return self._stack_name

    def _find_new_stack_name(self):
        for i in range(_MAX_ATTEMPTS_TO_FIND_STACK_NAME):
            stack_name = self._generate_stack_name()
            if not self._aws_access.stack_exists(stack_name=stack_name):
                return stack_name

    def upload_cloudformation_stack(self):
        yml = render_template("ec2_cloudformation.jinja.yaml",
                              key_name=self._ec2_key_name, user_name=self._user_name,
                              trace_tag=DEFAULT_TAG_KEY, trace_tag_value=self._tag_value,
                              ami_id=self._ami_id)
        self._stack_name = self._find_new_stack_name()
        self._aws_access.upload_cloudformation_stack(yml, self._stack_name,
                                                     tags=tuple(create_default_asset_tag(self._tag_value)))
        LOG.info(f"Deployed cloudformation stack "
                 f"{self._stack_name} with tag value '{self._tag_value}'")
        return self

    def get_ec2_instance_id(self) -> str:
        return find_ec2_instance_in_cf_stack(self._aws_access, self._stack_name)

    def close(self) -> None:
        if self._stack_name is not None:
            self._aws_access.delete_stack(self._stack_name)


class CloudformationStackContextManager:
    """
    The ContextManager-wrapper for CloudformationStack
    """
    def __init__(self, cf_stack: CloudformationStack):
        self._cf_stack = cf_stack

    def __enter__(self) -> CloudformationStack:
        self._cf_stack.upload_cloudformation_stack()
        return self._cf_stack

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._cf_stack.close()
