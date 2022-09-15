import time
from dataclasses import dataclass
from typing import Tuple

from exasol_script_languages_developer_sandbox.lib.asset_id import AssetId
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.aws_access.export_image_task import ExportImageTask
from exasol_script_languages_developer_sandbox.lib.logging import get_status_logger, LogType
from exasol_script_languages_developer_sandbox.lib.config import ConfigObject
from exasol_script_languages_developer_sandbox.lib.setup_ec2.cf_stack import find_ec2_instance_in_cf_stack
from exasol_script_languages_developer_sandbox.lib.asset_printing.print_assets import print_assets
from exasol_script_languages_developer_sandbox.lib.export_vm.vm_disk_image_format import VmDiskImageFormat
from exasol_script_languages_developer_sandbox.lib.vm_bucket.vm_slc_bucket import find_vm_bucket, find_vm_import_role

LOG = get_status_logger(LogType.EXPORT)


@dataclass(init=True, repr=True, eq=True)
class ExportImageTaskProgress:
    """
    Simple helper class which stores export image task progress and status.
    It supports comparison and hence can be used to check if there were any updates of `progress` or `status`.
    """
    progress: str
    status: str

    @staticmethod
    def from_export_image_task(export_image_task: ExportImageTask):
        return ExportImageTaskProgress(progress=export_image_task.progress, status=export_image_task.status)


def poll_export_image_task(aws_access: AwsAccess, export_image_task: ExportImageTask,
                           configuration: ConfigObject) -> ExportImageTask:
    """
    Checks a started exported-image-task in a loop until it completes or fails.

    :param aws_access: Aws Access proxy
    :param export_image_task:  the newly started export image task object.
    :param configuration: The global configuration object.
    :return: The export-image-task object after the task has completed or failed.
    """
    last_progress = ExportImageTaskProgress.from_export_image_task(export_image_task)
    while export_image_task.is_active:
        time.sleep(configuration.time_to_wait_for_polling)
        export_image_task = aws_access.get_export_image_task(export_image_task.id)
        progress = ExportImageTaskProgress.from_export_image_task(export_image_task)
        if last_progress != progress:
            LOG.info(f"still running export of vm image to "
                                                   f"{export_image_task.s3_bucket}/{export_image_task.s3_prefix}: "
                                                   f"{progress} ")
            last_progress = progress
    return export_image_task


def export_vm_image(aws_access: AwsAccess, vm_image_format: VmDiskImageFormat, tag_value: str,
                    ami_id: str, vmimport_role: str, vm_bucket: str, bucket_prefix: str,
                    configuration: ConfigObject):
    """
    Exports an AMI (parameter ami_id) to a VM image in the given S3-Bucket (parameter vm_bucket)
    at prefix (parameter bucket_prefix). The format of the VM is given by parameter vm_image_format.
    The export-image-task will be tagged with parameter tag_value. This action requires a AWS-role with sufficient
    permissions; this role needs to be defined by parameter vmimport_role.
    """
    LOG.info(f"export ami to vm with format '{vm_image_format}'")
    export_image_task_id = \
        aws_access.export_ami_image_to_vm(image_id=ami_id, tag_value=tag_value,
                                          description="VM Description", role_name=vmimport_role,
                                          disk_format=vm_image_format,
                                          s3_bucket=vm_bucket, s3_prefix=bucket_prefix)

    export_image_task = aws_access.get_export_image_task(export_image_task_id)
    LOG.info(f"Started export of vm image to {vm_bucket}/{bucket_prefix}. "
             f"Status message is {export_image_task.status_message}.")
    export_image_task = poll_export_image_task(aws_access, export_image_task, configuration)
    if not export_image_task.is_completed:
        raise RuntimeError(f"Export of VM failed: status message was {export_image_task.status_message}")


def export_vm_images(aws_access: AwsAccess, vm_image_formats: Tuple[str, ...], tag_value: str,
                     ami_id: str, vmimport_role: str, vm_bucket: str,
                     bucket_prefix: str, configuration: ConfigObject):
    for vm_image_format in vm_image_formats:
        try:
            export_vm_image(aws_access, VmDiskImageFormat[vm_image_format], tag_value,
                            ami_id, vmimport_role, vm_bucket, bucket_prefix, configuration)
        except Exception as e:
            raise RuntimeError(f"Failed to export VM to bucket {vm_bucket} at {bucket_prefix}\n") from e


def create_ami(aws_access: AwsAccess, ami_name: str, tag_value: str,
               instance_id: str, configuration: ConfigObject) -> str:
    """
    Creates a new AMI with the given name (parameter ami_name) for the EC2-Instance identified by parameter instance_id.
    The AMI will be tagged with given tag_value.
    :raises RuntimeError if an error occured during creation of the AMI
    Returns the ami_id if the export-image-task succeeded.
    """
    LOG.info(f"create ami with name '{ami_name}' and tag(s) '{tag_value}'")
    ami_id = aws_access.create_image_from_ec2_instance(instance_id, name=ami_name, tag_value=tag_value,
                                                       description="Image Description")

    ami = aws_access.get_ami(ami_id)
    while ami.is_pending:
        LOG.info(f"ami  with name '{ami.name}' and tag(s) '{tag_value}'  still pending...")
        time.sleep(configuration.time_to_wait_for_polling)
        ami = aws_access.get_ami(ami_id)
    if not ami.is_available:
        raise RuntimeError(f"Failed to create ami! ami state is '{ami.state}'")
    return ami_id


def export_vm(aws_access: AwsAccess,
              instance_id: str,
              vm_image_formats: Tuple[str, ...],
              asset_id: AssetId,
              configuration: ConfigObject) -> None:
    vm_bucket = find_vm_bucket(aws_access)
    vmimport_role = find_vm_import_role(aws_access)
    tag_value = asset_id.tag_value
    bucket_prefix = f"{asset_id.bucket_prefix}/"
    try:
        ami_id = create_ami(aws_access, asset_id.ami_name, tag_value, instance_id, configuration)
        export_vm_images(aws_access, vm_image_formats, tag_value, ami_id, vmimport_role, vm_bucket,
                         bucket_prefix, configuration)
    except Exception as e:
        print_assets(aws_access=aws_access, asset_id=asset_id, outfile=None)
        LOG.warning(f"VM Export finished for: {asset_id.ami_name}. There were errors. "
                    f"You might want to delete some of the assets created.")
        raise RuntimeError("Export failed") from e
    print_assets(aws_access=aws_access, asset_id=asset_id, outfile=None)
    LOG.info(f"VM Export finished for: {asset_id.ami_name} without any errors")


def run_export_vm(aws_access: AwsAccess,
                  stack_name: str,
                  vm_image_formats: Tuple[str, ...],
                  asset_id: AssetId,
                  configuration: ConfigObject):
    """
    Runs export only of the VM image.
    """
    ec_instance_id = find_ec2_instance_in_cf_stack(aws_access, stack_name)
    export_vm(aws_access, ec_instance_id, vm_image_formats, asset_id, configuration)
