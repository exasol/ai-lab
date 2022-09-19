from copy import copy
from typing import Union
from unittest.mock import create_autospec, Mock

import pytest

from exasol_script_languages_developer_sandbox.lib.aws_access.ami import Ami
from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.export_vm.run_make_ami_public import run_make_ami_public
from test.aws_mock_data import get_ami_image_mock_data

from test.mock_cast import mock_cast


def test_make_ami_public(default_asset_id):
    aws_access_mock: Union[AwsAccess, Mock] = create_autospec(AwsAccess)

    mock_ami = get_ami_image_mock_data("AVAILABLE")

    mock_public_ami_data = copy(mock_ami._aws_object)
    mock_public_ami_data["Public"] = True
    mock_cast(aws_access_mock.list_amis).return_value = [mock_ami]
    mock_cast(aws_access_mock.get_ami).return_value = Ami(mock_public_ami_data)
    run_make_ami_public(aws_access_mock, default_asset_id)
    mock_cast(aws_access_mock.modify_image_launch_permission).assert_called_once_with(mock_ami.id, {
        'Add': [
            {
                'Group': 'all',
            },
        ],
    })


def test_make_ami_public_not_changing_public_ami(default_asset_id):
    aws_access_mock: Union[AwsAccess, Mock] = create_autospec(AwsAccess)

    mock_ami = get_ami_image_mock_data("AVAILABLE")
    mock_ami._aws_object["Public"] = True
    mock_cast(aws_access_mock.list_amis).return_value = [mock_ami]
    run_make_ami_public(aws_access_mock, default_asset_id)
    mock_cast(aws_access_mock.get_ami).assert_not_called()
    mock_cast(aws_access_mock.modify_image_launch_permission).assert_not_called()


def test_make_ami_public_not_changed_raises_exception(default_asset_id):
    aws_access_mock: Union[AwsAccess, Mock] = create_autospec(AwsAccess)

    mock_ami = get_ami_image_mock_data("AVAILABLE")
    mock_cast(aws_access_mock.list_amis).return_value = [mock_ami]
    mock_cast(aws_access_mock.get_ami).return_value = mock_ami
    with pytest.raises(RuntimeError, match=f"Making AMI {mock_ami.id} public did not work"):
        run_make_ami_public(aws_access_mock, default_asset_id)
