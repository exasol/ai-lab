import signal
import time
from typing import Optional, Tuple, Iterator

from exasol_script_languages_developer_sandbox.lib.asset_id import AssetId
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.aws_access.ec2_instance import EC2Instance
from exasol_script_languages_developer_sandbox.lib.config import ConfigObject
from exasol_script_languages_developer_sandbox.lib.logging import get_status_logger, LogType
from exasol_script_languages_developer_sandbox.lib.setup_ec2.cf_stack import CloudformationStack, \
    CloudformationStackContextManager
from exasol_script_languages_developer_sandbox.lib.setup_ec2.key_file_manager import KeyFileManager, \
    KeyFileManagerContextManager
from exasol_script_languages_developer_sandbox.lib.setup_ec2.source_ami import find_source_ami


LOG = get_status_logger(LogType.SETUP)

# Python version of a typedef: Defines a type for the tuple and the iterator (of the tuple) we use for the state machine
EC2LifecycleData = Tuple[Optional[EC2Instance], Optional[str]]
EC2LifecycleDataIterator = Iterator[EC2LifecycleData]


def retrieve_user_name(user_name: Optional[str], aws_access: AwsAccess) -> str:
    """
    This function returns parameter "user_name" if valid. Otherwise, it tries to identify the user name from the AWS
    profile.
    Background: Within AWS codebuilds, which run under an IAM role,
                the user name cannot be retrieved from the AWS profile, and we need to set it in the environment.
    """
    if user_name:
        LOG.info(f"Using user name {user_name}")
        return user_name
    else:
        user_name_from_aws = aws_access.get_user()
        LOG.info(f"Using registered AWS user name: {user_name_from_aws}")
        return user_name_from_aws


def run_lifecycle_for_ec2(aws_access: AwsAccess,
                          ec2_key_file: Optional[str], ec2_key_name: Optional[str],
                          asset_id: AssetId, ami_id: str, user_name: Optional[str]) -> EC2LifecycleDataIterator:
    """
    This method launches a new EC-2 instance, using the given AMI (parameter ami_id), and yields every status:
    (pending, running). After it has yielded any other status than 'pending',
    when calling next() on the iterator object again, it will shutdown the instance.
    The client must check if the instance was launched successfully (by checking EC2Instance's state).
    :param aws_access: AwsAccess proxy.
    :param ec2_key_file:  The private key file to use for the EC2-Instance.
    :param ec2_key_name:  The key name of the key to use for the EC2-Instance.
    :param asset_id: The asset id to use: Will use the tags (for the cloudformation stack and the key) and the prefix of the cloudformation stack
    :param ami_id: The id of the AMI to use.
    :param user_name: Optional username to be used. If not given, the function will try to retrieve the user name from the AWS profile (however, this does not work for IAM roles).
    :return: An iterator which can be used to control the lifecycle of the EC2-instance.
    """
    with KeyFileManagerContextManager(KeyFileManager(aws_access, ec2_key_name, ec2_key_file, asset_id.tag_value)) as km:
        with CloudformationStackContextManager(CloudformationStack(aws_access, km.key_name,
                                                                   retrieve_user_name(user_name, aws_access),
                                                                   asset_id, ami_id)) \
                as cf_stack:
            ec2_instance_id = cf_stack.get_ec2_instance_id()

            LOG.info(f"Waiting for EC2 instance ({ec2_instance_id}) to start...")
            while True:
                ec2_instance_description = aws_access.describe_instance(ec2_instance_id)
                yield ec2_instance_description, km.key_file_location
                if not ec2_instance_description.is_pending:
                    break
    yield None, None


class EC2StackLifecycleContextManager:
    """
    Helper class which can be used to shutdown the EC2-instance automatically after it has been launched.
    It will call next() on the EC2LifecycleDataIterator when leaving the context.
    """
    def __init__(self, lifecycle_generator: EC2LifecycleDataIterator,
                 configuration: ConfigObject):
        self._lifecycle_generator = lifecycle_generator
        self._config = configuration

    def __enter__(self) -> Tuple[EC2Instance, str]:
        res = next(self._lifecycle_generator)
        while res[0].is_pending:
            LOG.info(f"EC2 instance not ready yet.")
            time.sleep(self._config.time_to_wait_for_polling)
            res = next(self._lifecycle_generator)
        ec2_instance_description, key_file_location = res
        return ec2_instance_description, key_file_location

    def __exit__(self, exc_type, exc_val, exc_tb):
        next(self._lifecycle_generator)


def run_setup_ec2(aws_access: AwsAccess, ec2_key_file: Optional[str], ec2_key_name: Optional[str],
                  asset_id: AssetId, configuration: ConfigObject) -> None:
    """
    Launches an EC2-instance and then waits until the user presses Ctrl-C, then shuts down the instance again.
    :param aws_access: AWSAccess proxy.
    :param ec2_key_file:  The private key file to use for the EC2-Instance.
    :param ec2_key_name:  The key name of the key to use for the EC2-Instance.
    :param asset_id: The asset id to use: Will use the tags (for the cloudformation stack and the key) and the prefix of the cloudformation stack
    :param configuration: The global configuration to use.
    """
    source_ami = find_source_ami(aws_access, configuration.source_ami_filters)
    LOG.info(f"Using source ami: '{source_ami.name}' from {source_ami.creation_date}")
    execution_generator = run_lifecycle_for_ec2(aws_access, ec2_key_file, ec2_key_name,
                                                asset_id, source_ami.id, user_name=None)
    with EC2StackLifecycleContextManager(execution_generator, configuration) as res:
        ec2_instance_description: Optional[EC2Instance]
        key_file_location: Optional[str]
        ec2_instance_description, key_file_location = res

        if not ec2_instance_description.is_running:
            LOG.error(f"Error during startup of EC2 instance "
                      f"'{ec2_instance_description.id}'. "
                      f"Status is {ec2_instance_description.state_name}")
        else:
            LOG.info(f"You can now login to the ec2 machine with "
                     f"'ssh -i {key_file_location} "
                     f"ubuntu@{ec2_instance_description.public_dns_name}'")
        LOG.info('Press Ctrl+C to stop and cleanup.')

        def signal_handler(sig, frame):
            LOG.info('Start cleanup.')

        signal.signal(signal.SIGINT, signal_handler)
        signal.pause()

    LOG.info('Cleanup done.')
