import logging
import signal
from typing import Optional, Tuple, Any

from exasol_script_languages_developer_sandbox.lib.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.cf_stack import CloudformationStack, \
    CloudformationStackContextManager
from exasol_script_languages_developer_sandbox.lib.key_file_manager import KeyFileManager, KeyFileManagerContextManager


def unpack_ec2_instance_description(ec2_instance_description: Any) -> Tuple[str, str]:
    return ec2_instance_description["State"]["Name"], ec2_instance_description["PublicDnsName"]


def run_lifecycle_for_ec2(aws_access: AwsAccess,
                          ec2_key_file: Optional[str], ec2_key_name: Optional[str],
                          stack_prefix: Optional[str]) -> Tuple[str, str, str, str]:
    with KeyFileManagerContextManager(KeyFileManager(aws_access, ec2_key_name, ec2_key_file)) as km:
        with CloudformationStackContextManager(CloudformationStack(aws_access, km.key_name,
                                                                   aws_access.get_user(), stack_prefix)) \
                as cf_stack:
            ec2_instance_id = cf_stack.get_ec2_instance_id()

            logging.info(f"Waiting for EC2 instance ({ec2_instance_id}) to start...")
            while True:
                ec2_instance_description = aws_access.describe_instance(ec2_instance_id)
                ec2_instance_status, host_name = unpack_ec2_instance_description(ec2_instance_description)
                yield ec2_instance_status, host_name, ec2_instance_id, km.key_file_location
                if ec2_instance_status != "pending":
                    break
    yield "terminated", "", "", ""


def run_setup_ec2(aws_access: AwsAccess, ec2_key_file: Optional[str], ec2_key_name: Optional[str]) -> None:
    execution_generator = run_lifecycle_for_ec2(aws_access, ec2_key_file, ec2_key_name, None)
    res = next(execution_generator)
    while res[0] == "pending":
        logging.info(f"EC2 instance not ready yet.")
        res = next(execution_generator)

    ec2_instance_status, host_name, ec2_instance_id, key_file_location = res
    if ec2_instance_status != "running":
        print(f"Error during startup of EC2 instance '{ec2_instance_id}'. Status is {ec2_instance_status}")
    else:
        print(f"You can now login to the ec2 machine with 'ssh -i {key_file_location}  ubuntu@{host_name}'")
    print('Press Ctrl+C to stop and cleanup.')

    def signal_handler(sig, frame):
        print('Start cleanup.')
        next(execution_generator)
        print('Cleanup done.')

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
