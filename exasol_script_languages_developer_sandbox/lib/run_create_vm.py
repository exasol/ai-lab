import time
from typing import Tuple, Optional, List

from exasol_script_languages_developer_sandbox.lib import config
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_repository import AnsibleRepository, \
    default_repositories
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_run_context import \
    reset_password_ansible_run_context, default_ansible_run_context
from exasol_script_languages_developer_sandbox.lib.asset_id import AssetId
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess

from exasol_script_languages_developer_sandbox.lib.setup_ec2.host_info import HostInfo
from exasol_script_languages_developer_sandbox.lib.export_vm.run_export_vm import export_vm
from exasol_script_languages_developer_sandbox.lib.setup_ec2.run_install_dependencies import run_install_dependencies
from exasol_script_languages_developer_sandbox.lib.setup_ec2.run_reset_password import run_reset_password
from exasol_script_languages_developer_sandbox.lib.setup_ec2.run_setup_ec2 import run_lifecycle_for_ec2, \
    EC2StackLifecycleContextManager


def run_create_vm(aws_access: AwsAccess, ec2_key_file: Optional[str], ec2_key_name: Optional[str],
                  ansible_access: AnsibleAccess, default_password: str,
                  vm_image_formats: Tuple[str, ...],
                  asset_id: AssetId,
                  ansible_run_context=default_ansible_run_context,
                  ansible_reset_password_context=reset_password_ansible_run_context,
                  ansible_repositories: Tuple[AnsibleRepository, ...] = default_repositories) \
        -> Optional[Tuple[str, List[str]]]:
    """
    Runs setup of an EC2 instance and then installs all dependencies via Ansible,
    and finally exports the VM to the S3 Bucket (which must be already created by the stack ("VM-SLC-Bucket").
    If anything goes wrong the cloudformation stack of the EC-2 instance will be removed.
    For debuging you can use the available debug commands.
    """
    execution_generator = run_lifecycle_for_ec2(aws_access, ec2_key_file, ec2_key_name, None, asset_id.tag_value)

    with EC2StackLifecycleContextManager(execution_generator) as ec2_data:
        ec2_instance_description, key_file_location = ec2_data
        if not ec2_instance_description.is_running:
            raise RuntimeError(f"Error during startup of EC2 instance '{ec2_instance_description.id}'. "
                               f"Status is {ec2_instance_description.state_name}")

        # Wait for the EC-2 instance to become ready.
        time.sleep(config.global_config.time_to_wait_for_polling)

        host_name = ec2_instance_description.public_dns_name
        run_install_dependencies(ansible_access, (HostInfo(host_name, key_file_location),),
                                 ansible_run_context, ansible_repositories)
        run_reset_password(ansible_access, default_password,
                           (HostInfo(host_name, key_file_location),), ansible_reset_password_context,
                           ansible_repositories)
        return export_vm(aws_access, ec2_instance_description.id, vm_image_formats, asset_id)
