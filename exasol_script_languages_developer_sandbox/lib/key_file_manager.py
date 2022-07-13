import logging
import os
from tempfile import mkstemp
from typing import Optional

from exasol_script_languages_developer_sandbox.lib.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.random_string_generator import get_random_str


class KeyFileManager:
    """
    Manages access to an AWS KeyFile (EC2). If a keyname and keyfile is given in constructor,
    this one will be used, and not be deleted.
    If no keyname is given in constructor, a new EC2 key will be generated and written to a temporary file:
    This key and temporary file will then be deleted during close.
    """
    def __init__(self, aws_access: AwsAccess,
                 external_ec2_key_name: Optional[str], external_ec2_key_file: Optional[str]):
        self._ec2_key_file = external_ec2_key_file
        self._aws_access = aws_access
        self._remove_key_on_close = False
        self._key_name = external_ec2_key_name

    def create_key_if_needed(self) -> None:
        if self._ec2_key_file is None:
            logging.debug("Creating new key-pair")
            self._key_name = f"ec2-key-{get_random_str()}"
            ec2_key_file_handle, self._ec2_key_file = mkstemp(text=True)
            with os.fdopen(ec2_key_file_handle, 'w') as f:
                f.write(self._aws_access.create_new_ec2_key_pair(key_name=self._key_name))
            self._remove_key_on_close = True
            logging.debug(f"Created new key-pair: key-name={self._key_name}, key-file={self._ec2_key_file}")
            os.chmod(self._ec2_key_file, 0o400)
        else:
            logging.debug("Using existing key-pair")

    @property
    def key_file_location(self) -> Optional[str]:
        return self._ec2_key_file

    @property
    def key_name(self) -> Optional[str]:
        return self._key_name

    def close(self) -> None:
        if self._remove_key_on_close:
            os.remove(self._ec2_key_file)
            self._aws_access.delete_ec2_key_pair(key_name=self._key_name)


class KeyFileManagerContextManager:
    """
    The ContextManager-wrapper for KeyFileManager
    """
    def __init__(self, key_file_manager: KeyFileManager):
        self._key_file_manager = key_file_manager

    def __enter__(self) -> KeyFileManager:
        self._key_file_manager.create_key_if_needed()
        return self._key_file_manager

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._key_file_manager.close()
