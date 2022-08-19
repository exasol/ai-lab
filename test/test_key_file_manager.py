import os
from unittest.mock import MagicMock

from exasol_script_languages_developer_sandbox.lib.setup_ec2.key_file_manager import KeyFileManager, KeyFileManagerContextManager


def test_external_keys(tmp_path, default_asset_id):
    """"
       Test that external key files will be used if given and the file won't be deleted when calling close()
       """
    aws_access_mock = MagicMock()
    tmp_file = tmp_path / "tst.pem"
    with open(tmp_file, "w") as f:
        f.write("secret")
    with KeyFileManagerContextManager(KeyFileManager(aws_access_mock, "test_key", str(tmp_file),
                                                     default_asset_id.tag_value)) as km:
        assert km.key_name == "test_key"
        assert km.key_file_location == str(tmp_file)
        assert not km._remove_key_on_close
    assert not aws_access_mock.delete_ec2_key_pair.called
    assert os.path.exists(str(tmp_file))


def test_generated_key(default_asset_id):
    """
    Test that generated key files will be created on AWS and removed when calling close().
    """
    aws_access_mock = MagicMock()
    aws_access_mock.create_new_ec2_key_pair.return_value = "secret_abc"
    key_name = ""
    with KeyFileManagerContextManager(KeyFileManager(aws_access_mock, None, None, default_asset_id.tag_value)) as km:
        assert len(km.key_name) > 0
        aws_access_mock.create_new_ec2_key_pair.assert_called_once_with(key_name=km.key_name,
                                                                        tag_value=default_asset_id.tag_value)
        assert km._remove_key_on_close
        key_name = km.key_name
        with open(km.key_file_location, "r") as f:
            content = f.read()
            assert content == "secret_abc"

    # Now call close. After that we expect that the key has been removed from AWS and the temporary file was removed.
    aws_access_mock.delete_ec2_key_pair.assert_called_once_with(key_name=key_name)
    assert not os.path.exists(km.key_file_location)

