import logging
import signal
import traceback
from typing import Tuple, Optional

from exasol_script_languages_developer_sandbox.lib.ansible.ansible_access import AnsibleAccess, AnsibleException
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_repository import AnsibleRepository, \
    default_repositories
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_run_context import AnsibleRunContext, \
    default_ansible_run_context
from exasol_script_languages_developer_sandbox.lib.aws_access import AwsAccess

from exasol_script_languages_developer_sandbox.lib.host_info import HostInfo

from exasol_script_languages_developer_sandbox.lib.run_install_dependencies import run_install_dependencies
from exasol_script_languages_developer_sandbox.lib.run_setup_ec2 import run_lifecycle_for_ec2


def run_setup_ec2_and_install_dependencies(aws_access: AwsAccess,
                                           ec2_key_file: Optional[str], ec2_key_name: Optional[str],
                                           ansible_access: AnsibleAccess,
                                           ansible_run_context: AnsibleRunContext = default_ansible_run_context,
                                           ansible_repositories: Tuple[AnsibleRepository, ...] = default_repositories
                                           ) -> None:
    """
    Runs setup of an EC2 instance and then installs all dependencies via Ansible.
    Note that if an error occurs during the ansible installation, the EC2-machine is not removed immediately. This
    gives you time to login into the machine and identify any setup issues.
    You can stop the EC-2 machine by pressing Ctrl-C.
    """
    execution_generator = run_lifecycle_for_ec2(aws_access, ec2_key_file, ec2_key_name, None)
    res = next(execution_generator)
    while res[0] == "pending":
        logging.info(f"EC2 instance not ready yet.")
        res = next(execution_generator)

    ec2_instance_status, host_name, ec2_instance_id, key_file_location = res
    if ec2_instance_status != "running":
        logging.error(f"Error during startup of EC2 instance '{ec2_instance_id}'. Status is {ec2_instance_status}")
        return

    try:
        run_install_dependencies(ansible_access, (HostInfo(host_name, key_file_location),),
                                 ansible_run_context, ansible_repositories)
    except Exception as e:
        traceback.print_exc()

    print("-----------------------------------------------------")
    print(f"You can now login to the ec2 machine with 'ssh -i {key_file_location}  ubuntu@{host_name}'")
    print(f"Also you can access Jupyterlab via http://{host_name}:8888/lab")
    print('Press Ctrl+C to stop and cleanup.')

    def signal_handler(sig, frame):
        print('Start cleanup.')
        next(execution_generator)
        print('Cleanup done.')

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
