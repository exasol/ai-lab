import signal
import time
from typing import Optional, Tuple, Generator

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


def run_lifecycle_for_ec2(aws_access: AwsAccess,
                          ec2_key_file: Optional[str], ec2_key_name: Optional[str],
                          stack_prefix: Optional[str], tag_value: str, ami_id: str) -> Generator:
    with KeyFileManagerContextManager(KeyFileManager(aws_access, ec2_key_name, ec2_key_file, tag_value)) as km:
        with CloudformationStackContextManager(CloudformationStack(aws_access, km.key_name,
                                                                   aws_access.get_user(), stack_prefix,
                                                                   tag_value, ami_id)) \
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
    def __init__(self, lifecycle_generator: Generator, configuration: ConfigObject):
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
    source_ami = find_source_ami(aws_access, configuration.source_ami_filters)
    LOG.info(f"Using source ami: '{source_ami.name}' from {source_ami.creation_date}")
    execution_generator = run_lifecycle_for_ec2(aws_access, ec2_key_file, ec2_key_name, None,
                                                asset_id.tag_value, source_ami.id)
    with EC2StackLifecycleContextManager(execution_generator, configuration) as res:
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
