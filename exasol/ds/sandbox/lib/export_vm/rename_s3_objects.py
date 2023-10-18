from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.aws_access.export_image_task import ExportImageTask
from exasol.ds.sandbox.lib.export_vm.vm_disk_image_format import VmDiskImageFormat


def build_image_source(prefix: str, export_image_task_id: str, vm_image_format: VmDiskImageFormat) -> str:
    img_format = vm_image_format.value.lower()
    return "{bucket_prefix}{export_task_id}.{img_format}".format(
        bucket_prefix=prefix,
        export_task_id=export_image_task_id,
        img_format=img_format)


def build_image_destination(prefix: str, asset_id: AssetId, vm_image_format: VmDiskImageFormat) -> str:
    img_format = vm_image_format.value.lower()
    return "{bucket_prefix}exasol-data-science-developer-sandbox-{asset_id}.{img_format}".format(
        bucket_prefix=prefix,
        asset_id=str(asset_id),
        img_format=img_format)


def rename_image_in_s3(aws_access: AwsAccess, export_image_task: ExportImageTask,
                       vm_image_format: VmDiskImageFormat,
                       asset_id: AssetId) -> None:
    """
    Renames the resulting S3 object of an export-image-task.
    The source objects always have the format "$export-image-task-id.$format".
    The destination objects always have the format "exasol-data-science-sandbox-{asset_id}.{img_format}"
    The bucket and prefix in bucket do not change.
    :param aws_access: Access proxy to Aws
    :param export_image_task: The export image task which is expected to be completed successfully.
    :param vm_image_format: The image format of the virtual image object.
                            The file name suffix is derived from this information.
    :param asset_id: The asset-id. This information will be appended to the destination name.
    """
    source = build_image_source(prefix=export_image_task.s3_prefix,
                                export_image_task_id=export_image_task.id,
                                vm_image_format=vm_image_format)
    dest = build_image_destination(prefix=export_image_task.s3_prefix, asset_id=asset_id,
                                   vm_image_format=vm_image_format)
    aws_access.copy_s3_object(bucket=export_image_task.s3_bucket, source=source, dest=dest)
    aws_access.delete_s3_object(bucket=export_image_task.s3_bucket, source=source)
