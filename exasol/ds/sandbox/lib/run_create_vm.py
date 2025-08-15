import time
from typing import Optional, Tuple

from exasol.ds.sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol.ds.sandbox.lib.ansible.ansible_repository import (
    AnsibleRepository, default_repositories)
from exasol.ds.sandbox.lib.ansible.ansible_run_context import (
    AnsibleRunContext, default_ansible_run_context,
    reset_password_ansible_run_context)
from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import ConfigObject
from exasol.ds.sandbox.lib.export_vm.run_export_vm import export_vm
from exasol.ds.sandbox.lib.export_vm.run_make_ami_public import \
    run_make_ami_public
from exasol.ds.sandbox.lib.logging import LogType, get_status_logger
from exasol.ds.sandbox.lib.setup_ec2.host_info import HostInfo
from exasol.ds.sandbox.lib.setup_ec2.run_install_dependencies import \
    run_install_dependencies
from exasol.ds.sandbox.lib.setup_ec2.run_reset_password import \
    run_reset_password
from exasol.ds.sandbox.lib.setup_ec2.run_setup_ec2 import (
    EC2StackLifecycleContextManager, run_lifecycle_for_ec2)
from exasol.ds.sandbox.lib.setup_ec2.source_ami import find_source_ami

LOG = get_status_logger(LogType.CREATE_VM)


def run_create_vm(
    aws_access: AwsAccess,
    ec2_instance_type: str,
    ec2_key_file: Optional[str],
    ec2_key_name: Optional[str],
    ansible_access: AnsibleAccess,
    default_password: str,
    vm_image_formats: Tuple[str, ...],
    asset_id: AssetId,
    configuration: ConfigObject,
    user_name: Optional[str],
    make_ami_public: bool,
    ansible_run_context: AnsibleRunContext = default_ansible_run_context,
    ansible_reset_password_context: AnsibleRunContext = reset_password_ansible_run_context,
    ansible_repositories: Tuple[AnsibleRepository, ...] = default_repositories,
) -> None:
    """
    Runs setup of an EC2 instance and then installs all dependencies via Ansible,
    and finally exports the VM to the S3 Bucket (which must be already created
    by the stack "DATA-SCIENCE-SANDBOX-VM-Bucket").
    If anything goes wrong the cloudformation stack of the EC-2 instance will be removed.
    For debuging you can use the available debug commands.
    """
    source_ami = find_source_ami(aws_access, configuration.source_ami_filters)
    LOG.info(f"Using source ami: '{source_ami.name}' from {source_ami.creation_date}")
    execution_generator = run_lifecycle_for_ec2(
        aws_access=aws_access,
        ec2_instance_type=ec2_instance_type,
        ec2_key_file=ec2_key_file,
        ec2_key_name=ec2_key_name,
        asset_id=asset_id,
        ami_id=source_ami.id,
        user_name=user_name,
    )
    with EC2StackLifecycleContextManager(execution_generator, configuration) as ec2_data:
        ec2_instance, key_file_location = ec2_data
        if not ec2_instance.is_running:
            raise RuntimeError(
                f"Error during startup of EC2 instance '{ec2_instance.id}'. "
                f"Status is {ec2_instance.state_name}"
            )

        # Wait for the EC-2 instance to become ready.
        time.sleep(configuration.time_to_wait_for_polling)

        host_name = ec2_instance.public_dns_name
        run_install_dependencies(
            ansible_access,
            configuration,
            (HostInfo(host_name, key_file_location),),
            ansible_run_context,
            ansible_repositories,
        )
        run_reset_password(
            ansible_access,
            default_password,
            (HostInfo(host_name, key_file_location),),
            ansible_reset_password_context,
            ansible_repositories,
        )
        export_vm(
            aws_access,
            ec2_instance.id,
            vm_image_formats,
            asset_id,
            configuration,
        )

    if make_ami_public:
        run_make_ami_public(aws_access, asset_id)
