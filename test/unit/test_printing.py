import pytest

from io import StringIO
from typing import Union
from unittest.mock import MagicMock, call, create_autospec, Mock

from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.asset_printing.print_assets import print_with_printer, AssetTypes, print_assets
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from test.aws_mock_data import get_ami_image_mock_data, TEST_AMI_ID, get_snapshot_mock_data, \
    get_export_image_task_mock_data, get_s3_object_mock_data, TEST_BUCKET_ID, \
    get_ec2_cloudformation_mock_data, get_ec2_cloudformation_stack_resources_mock_data, get_ec2_key_pair_mock_data, \
    get_s3_cloudformation_mock_data, TEST_CLOUDFRONT_DOMAIN_NAME
from test.mock_cast import mock_cast


@pytest.fixture
def printing_mocks():
    table_printer_mock = MagicMock()
    text_printer_mock = MagicMock()
    printing_factory = MagicMock()
    printing_factory.create_table_printer.return_value = table_printer_mock
    printing_factory.create_text_printer.return_value = text_printer_mock
    return table_printer_mock, text_printer_mock, printing_factory


def test_printing_ami(default_asset_id, printing_mocks):
    table_printer_mock, text_printer_mock, printing_factory = printing_mocks

    aws_mock = MagicMock()
    aws_mock.list_amis.return_value = [get_ami_image_mock_data("available")]
    print_with_printer(aws_mock, None, (AssetTypes.AMI,), "*", printing_factory)

    assert table_printer_mock.add_column.call_count == 8
    table_printer_mock.add_row.assert_called_once_with(TEST_AMI_ID, default_asset_id.ami_name,
                                                       'Image Description', "no", '123/some_dummy_location',
                                                       '2022-08-16T15:02:10.000Z', "available",
                                                       default_asset_id.tag_value)
    table_printer_mock.finish.assert_called_once()
    assert text_printer_mock.print.call_count == 2


def test_printing_snapshot(default_asset_id, printing_mocks):
    table_printer_mock, text_printer_mock, printing_factory = printing_mocks

    aws_mock = MagicMock()
    aws_mock.list_snapshots.return_value = [get_snapshot_mock_data()]
    print_with_printer(aws_mock, None, (AssetTypes.SNAPSHOT,), "*", printing_factory)

    assert table_printer_mock.add_column.call_count == 7
    table_printer_mock.add_row.assert_called_once_with('snap-123', 'Created by foo',
                                                       '100%', 'vol-123', '2022-08-16, 15:03',
                                                       'completed', default_asset_id.tag_value)
    table_printer_mock.finish.assert_called_once()
    assert text_printer_mock.print.call_count == 2


export_image_task_mock_data = [
    ("50%", "active", "creating the image", get_export_image_task_mock_data(in_progress=True)),
    ("n/a", "completed", "n/a", get_export_image_task_mock_data(in_progress=False))
]


@pytest.mark.parametrize("progress,status, status_message, mock_data", export_image_task_mock_data)
def test_print_export_image_tasks(default_asset_id, printing_mocks, progress, status, status_message, mock_data):
    table_printer_mock, text_printer_mock, printing_factory = printing_mocks

    aws_mock = MagicMock()
    aws_mock.list_export_image_tasks.return_value = [mock_data]
    print_with_printer(aws_mock, None, (AssetTypes.EXPORT_IMAGE_TASK,), "*", printing_factory)

    assert table_printer_mock.add_column.call_count == 8

    table_printer_mock.add_row.assert_called_once_with('export-ami-123', 'VM Description',
                                                       progress,  TEST_BUCKET_ID,
                                                       default_asset_id.bucket_prefix,
                                                       status, status_message, default_asset_id.tag_value)
    table_printer_mock.finish.assert_called_once()
    assert text_printer_mock.print.call_count == 2


# "test" comes from DEFAULT_ASSET_ID
filter_for_s3 = [
    (None, True),
    ("test", True),
    ("not_there", False),
    ("test*", True),
    ("te?t", True),
    ("te*", True),
    ("n*", False),
    ("*", True),
]


@pytest.mark.parametrize("filter_value,expected_found_s3_object", filter_for_s3)
def test_printing_s3_object(default_asset_id, printing_mocks, filter_value, expected_found_s3_object):
    table_printer_mock, text_printer_mock, printing_factory = printing_mocks

    aws_access_mock: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws_access_mock.list_s3_objects).return_value = [get_s3_object_mock_data()]
    mock_cast(aws_access_mock.describe_stacks).return_value = get_s3_cloudformation_mock_data()
    asset_id = AssetId(filter_value) if filter_value else None
    print_with_printer(aws_access_mock, asset_id, (AssetTypes.VM_S3,), "*", printing_factory)

    assert table_printer_mock.add_column.call_count == 4

    if expected_found_s3_object:
        s3_uri = f"s3://{TEST_BUCKET_ID}/{default_asset_id.bucket_prefix}/export-ami-123.vmdk"
        url = f"https://{TEST_CLOUDFRONT_DOMAIN_NAME}/{default_asset_id.bucket_prefix}/export-ami-123.vmdk"
        table_printer_mock.add_row.assert_called_once_with(
            f'{default_asset_id.bucket_prefix}/export-ami-123.vmdk',
            "2.19 GB", s3_uri, url)
    else:
        table_printer_mock.add_row.assert_not_called()



# "test" comes from DEFAULT_ASSET_ID
filter_for_cloudformation = [
    ("test", True),
    ("not_there", False),
    ("test*", True),
    ("te?t", True),
    ("te*", True),
    ("n*", False),
    ("*", True),
]


@pytest.mark.parametrize("filter_value,expected_found_cloudformation", filter_for_cloudformation)
def test_print_cloudformation_stack(default_asset_id, printing_mocks, filter_value, expected_found_cloudformation):
    table_printer_mock, text_printer_mock, printing_factory = printing_mocks

    aws_mock = MagicMock()
    aws_mock.describe_stacks.return_value = [get_ec2_cloudformation_mock_data()]
    asset_id = AssetId(filter_value) if filter_value else None
    aws_mock.get_all_stack_resources.return_value = get_ec2_cloudformation_stack_resources_mock_data()
    print_with_printer(aws_mock, asset_id, (AssetTypes.CLOUDFORMATION,), filter_value, printing_factory)

    assert table_printer_mock.add_column.call_count == 7

    if expected_found_cloudformation:
        expected_calls = [
            call('test-stack-name', "n/a", "CREATE_COMPLETE", "2022-08-16, 14:30", "", "", default_asset_id.tag_value),
            call('', "", "", "", 'ec2-instance-123', 'AWS::EC2::Instance', "n/a"),
            call('', "", "", "", 'ec2-security-group-123', 'AWS::EC2::SecurityGroup', "n/a"),
        ]
        assert table_printer_mock.add_row.call_args_list == expected_calls
    else:
        table_printer_mock.add_row.assert_not_called()

    table_printer_mock.finish.assert_called_once()
    assert text_printer_mock.print.call_count == 2


def test_print_ec2_keypairs(default_asset_id, printing_mocks):
    table_printer_mock, text_printer_mock, printing_factory = printing_mocks

    aws_mock = MagicMock()
    aws_mock.list_ec2_key_pairs.return_value = [get_ec2_key_pair_mock_data()]
    print_with_printer(aws_mock, None, (AssetTypes.EC2_KEY_PAIR,), "*", printing_factory)

    assert table_printer_mock.add_column.call_count == 4

    table_printer_mock.add_row.assert_called_once_with(
        "key-123", "ec2-key-test-key", "2022-08-16, 15:30",
        default_asset_id.tag_value)

    table_printer_mock.finish.assert_called_once()
    assert text_printer_mock.print.call_count == 2


def test_print_docker(default_asset_id):
    aws_mock = MagicMock()
    aws_mock.list_s3_objects.return_value = [
        get_s3_object_mock_data("vhd"),
        get_s3_object_mock_data("vmdk"),
    ]
    aws_mock.describe_stacks.return_value = get_s3_cloudformation_mock_data()
    aws_mock.list_amis.return_value = [get_ami_image_mock_data("available")]
    with StringIO() as buf:
        print_assets(
            aws_mock,
            default_asset_id,
            buf,
            (AssetTypes.DOCKER, AssetTypes.AMI, AssetTypes.VM_S3,),
        )
        actual = buf.getvalue()
    assert "#### Docker Images" in actual
    assert "docker pull exasol/data-science-sandbox:test" in actual
