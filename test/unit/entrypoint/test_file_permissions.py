import grp
import pytest
import os
import re
import stat
import subprocess

from pathlib import Path
from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint
from unittest.mock import MagicMock


def test_file_inspector_non_existing_file(mocker):
    not_called_if_works = mocker.patch("pathlib.Path.stat")
    mocker.patch("pathlib.Path.exists", return_value=False)
    testee = entrypoint.FileInspector(Path("/non/existing/file"))
    actual = testee.is_group_accessible()
    assert actual == False
    assert not not_called_if_works.called


def test_file_inspector_group_id_non_existing_file():
    testee = entrypoint.FileInspector(Path("/non/existing/file"))
    with pytest.raises(FileNotFoundError):
        testee.group_id


def test_file_inspector_group_accessible(accessible_file):
    testee = entrypoint.FileInspector(accessible_file)
    assert testee.is_group_accessible()


def test_file_inspector_insufficient_group_permissions(non_accessible_file):
    testee = entrypoint.FileInspector(non_accessible_file)
    with pytest.raises(PermissionError, match="No rw permissions for group") as err:
        testee.is_group_accessible()

def test_group_access_enable_existing_group(mocker):
    grdb_entry = MagicMock(gr_name="existing")
    mocker.patch("grp.getgrgid", return_value=grdb_entry)
    mocker.patch("subprocess.run")
    testee = entrypoint.GroupAccess("jennifer", entrypoint.Group("other", 666))
    actual = testee.enable()
    usermod = mocker.call("usermod --append --groups existing jennifer".split())
    assert entrypoint.Group("existing", 666) == actual \
        and usermod == subprocess.run.call_args


def test_group_access_enable_unknown_gid(mocker):
    mocker.patch("grp.getgrgid", side_effect=KeyError)
    mocker.patch("subprocess.run")
    testee = entrypoint.GroupAccess("jennifer", entrypoint.Group("other", 666))
    actual = testee.enable()
    groupmod = mocker.call("groupmod -g 666 other".split())
    assert entrypoint.Group("other", 666) == actual\
        and groupmod == subprocess.run.call_args
