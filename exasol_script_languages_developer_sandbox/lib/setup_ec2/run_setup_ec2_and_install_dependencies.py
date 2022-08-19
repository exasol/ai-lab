import logging
import signal
import time
from typing import Tuple, Optional

from exasol_script_languages_developer_sandbox.lib import config
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_repository import AnsibleRepository, \
    default_repositories
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_run_context import AnsibleRunContext, \
    default_ansible_run_context
from exasol_script_languages_developer_sandbox.lib.asset_id import AssetId
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess

from exasol_script_languages_developer_sandbox.lib.setup_ec2.host_info import HostInfo

from exasol_script_languages_developer_sandbox.lib.setup_ec2.run_install_dependencies import run_install_dependencies
from exasol_script_languages_developer_sandbox.lib.setup_ec2.run_setup_ec2 import run_lifecycle_for_ec2, \
    EC2StackLifecycleContextManager


def run_setup_ec2_and_install_dependencies(aws_access: AwsAccess,
                                           ec2_key_file: Optional[str], ec2_key_name: Optional[str],
                                           asset_id: AssetId, ansible_access: AnsibleAccess,
                                           ansible_run_context: AnsibleRunContext = default_ansible_run_context,
                                           ansible_repositories: Tuple[AnsibleRepository, ...] = default_repositories
                                           ) -> None:
    """
    Runs setup of an EC2 instance and then installs all dependencies via Ansible.
    Note that if an error occurs during the ansible installation, the EC2-machine is not removed immediately. This
    gives you time to login into the machine and identify any setup issues.
    You can stop the EC-2 machine by pressing Ctrl-C.
    """
    execution_generator = run_lifecycle_for_ec2(aws_access, ec2_key_file, ec2_key_name, None, asset_id.tag_value)
    with EC2StackLifecycleContextManager(execution_generator) as res:
        ec2_instance_description, key_file_location = res

        if not ec2_instance_description.is_running:
            logging.error(f"Error during startup of EC2 instance '{ec2_instance_description.id}'. "
                          f"Status is {ec2_instance_description.state_name}")
            return

        #Wait for the EC-2 instance to become ready.
        time.sleep(config.global_config.time_to_wait_for_polling)
        host_name = ec2_instance_description.public_dns_name
        try:
            run_install_dependencies(ansible_access, (HostInfo(host_name, key_file_location),),
                                     ansible_run_context, ansible_repositories)
        except Exception as e:
            logging.exception("Install dependencies failed.")

        print("-----------------------------------------------------")
        print(f"You can now login to the ec2 machine with 'ssh -i {key_file_location}  ubuntu@{host_name}'")
        print(f"Also you can access Jupyterlab via http://{host_name}:8888/lab")
        print('Press Ctrl+C to stop and cleanup.')

        def signal_handler(sig, frame):
            print('Start cleanup.')

        signal.signal(signal.SIGINT, signal_handler)
        signal.pause()

    print('Cleanup done.')
