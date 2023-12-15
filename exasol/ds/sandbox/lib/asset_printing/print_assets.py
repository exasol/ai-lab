import fnmatch
import humanfriendly
import urllib.parse

from datetime import datetime
from dataclasses import dataclass
from inspect import cleandoc
from typing import Dict, List, Optional, TextIO, Tuple

from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.asset_printing.mark_down_printer import MarkdownPrintingFactory
from exasol.ds.sandbox.lib.asset_printing.printing_factory import (
    PrintingFactory,
    CodeBlockTextObject,
    HighlightedTextObject,
    TextObject,
    TitleTextObject,
)
from exasol.ds.sandbox.lib.asset_printing.rich_console_printer import RichConsolePrintingFactory
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from enum import Enum

from exasol.ds.sandbox.lib.aws_access.cloudformation_stack import CloudformationStack
from exasol.ds.sandbox.lib.tags import DEFAULT_TAG_KEY
from exasol.ds.sandbox.lib.vm_bucket.vm_dss_bucket import find_vm_bucket, find_url_for_bucket
from exasol.ds.sandbox.lib.dss_docker import DEFAULT_ORG_AND_REPOSITORY


class AssetTypes(Enum):
    DOCKER = "docker"
    AMI = "ami"
    SNAPSHOT = "snapshot"
    EXPORT_IMAGE_TASK = "export-image-task"
    VM_S3 = "s3-object"
    CLOUDFORMATION = "cloudformation"
    EC2_KEY_PAIR = "ec2-key-pair"

    @staticmethod
    def from_name(name: str):
        return next(a for a in AssetTypes if a.value == name)


def aws_asset_type_names() -> Tuple[str, ...]:
    return tuple(a.value for a in AssetTypes if a != AssetTypes.DOCKER)


def find_default_tag_value_in_tags(tags: Optional[List[Dict[str,str]]]):
    return_value = "n/a"

    filtered_tags = [tag["Value"] for tag in tags if tag["Key"] == DEFAULT_TAG_KEY]
    if len(filtered_tags) == 1:
        return_value = filtered_tags[0]
    return return_value


def print_amis(aws_access: AwsAccess, filter_value: str, printing_factory: PrintingFactory):
    table_printer = printing_factory.create_table_printer(title=f"AMI Images (Filter={filter_value})")

    table_printer.add_column("Image ID", style="blue", no_wrap=True)
    table_printer.add_column("Name", no_wrap=True)
    table_printer.add_column("Description", no_wrap=False)
    table_printer.add_column("Public", no_wrap=True)
    table_printer.add_column("Image Location", no_wrap=True)
    table_printer.add_column("Creation Date", style="magenta", no_wrap=True)
    table_printer.add_column("State", no_wrap=True)
    table_printer.add_column("Asset-Tag-Value", no_wrap=True)

    amis = aws_access.list_amis(filters=[{'Name': f'tag:{DEFAULT_TAG_KEY}', 'Values': [filter_value]}])
    for ami in amis:
        is_public = "yes" if ami.is_public else "no"
        table_printer.add_row(ami.id, ami.name, ami.description, is_public,
                              ami.image_location, ami.creation_date, ami.state,
                              find_default_tag_value_in_tags(ami.tags))

    table_printer.finish()
    text_print = printing_factory.create_text_printer(console_only=True)
    text_print.print((TextObject("You can de-register AMI images using AWS CLI:\n"),
                      TextObject("'aws ec2 deregister-image --image-id "),
                      HighlightedTextObject("Image-Id"),
                      TextObject("'")))
    text_print.print(tuple())


def print_snapshots(aws_access: AwsAccess, filter_value: str, printing_factory: PrintingFactory):
    table_printer = printing_factory.create_table_printer(title=f"EC-2 Snapshots (Filter={filter_value})")

    table_printer.add_column("SnapshotId", style="blue", no_wrap=True)
    table_printer.add_column("Description", no_wrap=False)
    table_printer.add_column("Progress", no_wrap=True)
    table_printer.add_column("VolumeId", no_wrap=True)
    table_printer.add_column("StartTime", style="magenta", no_wrap=True)
    table_printer.add_column("State", no_wrap=True)
    table_printer.add_column("Asset-Tag-Value", no_wrap=True)

    snapshots = aws_access.list_snapshots(filters=[{'Name': f'tag:{DEFAULT_TAG_KEY}', 'Values': [filter_value]}])
    for snapshot in snapshots:
        table_printer.add_row(snapshot.id, snapshot.description, snapshot.progress,
                              snapshot.volume_id, snapshot.start_time.strftime("%Y-%m-%d, %H:%M"),
                              snapshot.state, find_default_tag_value_in_tags(snapshot.tags))

    table_printer.finish()

    text_print = printing_factory.create_text_printer(console_only=True)
    text_print.print((TextObject("You can remove snapshots using AWS CLI:\n"),
                      TextObject("'aws ec2 delete-snapshot --snapshot-id "),
                      HighlightedTextObject("SnapshotId"),
                      TextObject("'")))
    text_print.print(tuple())


def print_export_image_tasks(aws_access: AwsAccess, filter_value: str, printing_factory: PrintingFactory):
    table_printer = printing_factory.create_table_printer(title=f"Export Image Tasks (Filter={filter_value})")

    table_printer.add_column("ExportImageTaskId", style="blue", no_wrap=True)
    table_printer.add_column("Description", no_wrap=False)
    table_printer.add_column("Progress", no_wrap=True)
    table_printer.add_column("S3ExportLocation - S3Bucket", no_wrap=True)
    table_printer.add_column("S3ExportLocation - S3Prefix", no_wrap=True)
    table_printer.add_column("Status", no_wrap=True)
    table_printer.add_column("StatusMessage", no_wrap=True)
    table_printer.add_column("Asset-Tag-Value", no_wrap=True)

    export_image_tasks = \
        aws_access.list_export_image_tasks(filters=[{'Name': f'tag:{DEFAULT_TAG_KEY}', 'Values': [filter_value]}])

    for export_image_task in export_image_tasks:
        s3bucket = export_image_task.s3_bucket
        s3prefix = export_image_task.s3_prefix
        table_printer.add_row(export_image_task.id, export_image_task.description,
                              export_image_task.progress, s3bucket, s3prefix,
                              export_image_task.status, export_image_task.status_message,
                              find_default_tag_value_in_tags(export_image_task.tags))

    table_printer.finish()
    text_print = printing_factory.create_text_printer(console_only=True)
    text_print.print((TextObject("You can cancel active tasks using AWS CLI:\n"),
                      TextObject("'aws ec2 cancel-export-task --export-task-id "),
                      HighlightedTextObject("ExportImageTaskId"),
                      TextObject("'")))
    text_print.print(tuple())


def print_s3_objects(aws_access: AwsAccess, asset_id: Optional[AssetId], printing_factory: PrintingFactory):
    vm_bucket = find_vm_bucket(aws_access)
    url_for_bucket = find_url_for_bucket(aws_access)

    if asset_id is not None:
        prefix = asset_id.bucket_prefix
    else:
        prefix = ""

    table_printer = printing_factory.create_table_printer(title=f"S3 Objects (Bucket={vm_bucket} Prefix={prefix})")

    table_printer.add_column("Key", no_wrap=True)
    table_printer.add_column("Size", no_wrap=True)
    table_printer.add_column("S3 URI", no_wrap=False)
    table_printer.add_column("URL", no_wrap=False)

    # How the filtering works:
    # 1. The VM are stored under following location in the S3 Bucket: $BUCKET_PREFIX/$AssetId/name.$VM_FORMAT
    #    For example "data_science_sandbox/5.0.0/export-ami-01be860e6a6a98bf8.vhd"
    # 2. Because S3 list_s3_object does not support wildcards,
    #    we need to implement our own wildcard implementation here.
    #    We call list_s3_object with the standard prefix (e.g. "data_science_sandbox"),
    #    which returns ALL stored vm objects.
    # 3. If no filter is given (asset_id == None), "prefix" will be empty, and we return all s3 objects
    # 4. If the variable "prefix" is not empty, we need to ensure that it ends with a wildcard, so that the matching
    #    works correctly.
    # => Assume that a filter is given  "5.0.0". Variable prefix would be "data_science_sandbox/5.0.0".

    s3_objects = aws_access.list_s3_objects(bucket=vm_bucket, prefix=AssetId.BUCKET_PREFIX)

    if s3_objects is not None and len(prefix) > 0:
        if prefix[-1] != "*":
            prefix = f"{prefix}*"
        s3_objects = [s3_object for s3_object in s3_objects if fnmatch.fnmatch(s3_object.key, prefix)]
    s3_bucket_uri = "s3://{bucket}/{{object}}".format(bucket=vm_bucket)
    https_bucket_url = "https://{url_for_bucket}/{{object}}".format(url_for_bucket=url_for_bucket)

    if s3_objects is not None:
        for s3_object in s3_objects:
            obj_size = humanfriendly.format_size(s3_object.size)
            key = s3_object.key
            s3_uri = s3_bucket_uri.format(object=key)
            https_url = https_bucket_url.format(object=urllib.parse.quote(key))
            table_printer.add_row(key, obj_size, s3_uri, https_url)

    table_printer.finish()


def cloudformation_stack_has_matching_tag(cloudformation_stack: CloudformationStack, filter_value: str):
    if filter_value == "*":
        return True
    else:
        if cloudformation_stack.tags is not None:
            for tag in cloudformation_stack.tags:
                tag_key = tag["Key"]
                tag_value = tag["Value"]
                if tag_key == DEFAULT_TAG_KEY and fnmatch.fnmatch(tag_value, filter_value):
                    return True
    return False


def print_cloudformation_stacks(aws_access: AwsAccess, filter_value: str, printing_factory: PrintingFactory):
    table_printer = printing_factory.create_table_printer(title=f"Cloudformation stacks (Filter={filter_value})")

    table_printer.add_column("Stack-Name", style="blue", no_wrap=True)
    table_printer.add_column("Description", no_wrap=False)
    table_printer.add_column("StackStatus", no_wrap=True)
    table_printer.add_column("CreationTime", style="magenta", no_wrap=True)
    table_printer.add_column("PhysicalResourceId", no_wrap=False)
    table_printer.add_column("ResourceType", no_wrap=True)
    table_printer.add_column("Asset-Tag-Value", no_wrap=True)

    cloudformation_stack = aws_access.describe_stacks()

    relevant_stacks = [stack for stack in
                       cloudformation_stack if cloudformation_stack_has_matching_tag(stack, filter_value)]
    for stack in relevant_stacks:
        table_printer.add_row(stack.name,
                              stack.description, stack.status,
                              stack.creation_time.strftime("%Y-%m-%d, %H:%M"), "", "",
                              find_default_tag_value_in_tags(stack.tags))
        stack_resources = aws_access.get_all_stack_resources(stack_name=stack.name)
        for stack_resource in stack_resources:
            table_printer.add_row("", "", "", "", stack_resource.physical_id,
                                  stack_resource.resource_type, "n/a")

    table_printer.finish()
    text_print = printing_factory.create_text_printer(console_only=True)
    text_print.print((TextObject("You can remove a cf stack using AWS CLI:\n"),
                      TextObject("'aws cloudformation delete-stack --stack-name "),
                      HighlightedTextObject("Stack-Name/Stack-Id"),
                      TextObject("'")))
    text_print.print(tuple())


def print_ec2_keys(aws_access: AwsAccess, filter_value: str, printing_factory: PrintingFactory):
    table_printer = printing_factory.create_table_printer(title=f"EC-2 Keys (Filter={filter_value})")

    table_printer.add_column("KeyPairId", style="blue", no_wrap=True)
    table_printer.add_column("KeyName", no_wrap=True)
    table_printer.add_column("CreateTime", style="magenta", no_wrap=True)
    table_printer.add_column("Asset-Tag-Value", no_wrap=True)

    key_pairs = aws_access.list_ec2_key_pairs(filters=[{'Name': f'tag:{DEFAULT_TAG_KEY}', 'Values': [filter_value]}])
    for key_pair in key_pairs:
        table_printer.add_row(key_pair.id, key_pair.key_name,
                              key_pair.created_time.strftime("%Y-%m-%d, %H:%M"),
                              find_default_tag_value_in_tags(key_pair.tags))

    table_printer.finish()

    text_print = printing_factory.create_text_printer(console_only=True)
    text_print.print((TextObject("You can remove key-pairs using AWS CLI:\n"),
                      TextObject("'aws ec2 delete-key-pair --key-pair-id "),
                      HighlightedTextObject("KeyPairId"),
                      TextObject("'")))
    text_print.print(tuple())


def print_with_printer(
        aws_access: AwsAccess,
        asset_id: Optional[AssetId],
        asset_types: Tuple[AssetTypes],
        filter_value: str,
        printing_factory: PrintingFactory,
):
    print_function = {
        AssetTypes.DOCKER: print_docker_images,
        AssetTypes.AMI: print_amis,
        AssetTypes.SNAPSHOT: print_snapshots,
        AssetTypes.EXPORT_IMAGE_TASK: print_export_image_tasks,
        AssetTypes.VM_S3: print_s3_objects,
        AssetTypes.CLOUDFORMATION: print_cloudformation_stacks,
        AssetTypes.EC2_KEY_PAIR: print_ec2_keys,
    }

    def second_arg(asset_type: AssetTypes):
        if asset_type in (AssetTypes.DOCKER, AssetTypes.VM_S3):
            return asset_id
        return filter_value

    selected = (a for a in AssetTypes if a in asset_types)
    for asset_type in selected:
        print_function[asset_type](
            aws_access,
            second_arg(asset_type),
            printing_factory,
        )


def print_docker_images(aws_access: AwsAccess, asset_id: str, printing_factory: PrintingFactory):
    printer = printing_factory.create_text_printer()
    printer.print((
        TitleTextObject("Docker Images"),
        CodeBlockTextObject(f"docker pull {DEFAULT_ORG_AND_REPOSITORY}:{asset_id}"),
    ))
    printer.print(tuple())


def printing_factory(outfile):
    if outfile is None:
        return RichConsolePrintingFactory()
    return MarkdownPrintingFactory(outfile)


def print_assets(
        aws_access: AwsAccess,
        asset_id: Optional[AssetId],
        outfile: Optional[TextIO],
        asset_types: Tuple[AssetTypes] = AssetTypes,
):
    filter_value = "*" if asset_id is None else asset_id.tag_value
    print_with_printer(
        aws_access,
        asset_id,
        asset_types,
        filter_value,
        printing_factory(outfile),
    )
