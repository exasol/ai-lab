import grp
import pytest
import os
import re
import stat

from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint
from unittest.mock import MagicMock

# def stat_result(
#         st_mode=0,
#         st_ino=0,
#         st_dev=0,
#         st_nlink=0,
#         st_uid=0,
#         st_gid=0,
#         st_size=0,
#         st_atime=0,
#         st_mtime=0,
#         st_ctime=0,
# ):
#     return os.stat_result((
#         st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size,
#         st_atime, st_mtime, st_ctime,
#     ))


def test_file_inspector_non_existing_file(mocker):
    mocker.patch("os.stat")
    # need to mock os.path.exists as os.path.exists seems to call os.stat :)
    mocker.patch("os.path.exists", return_value=False)
    testee = entrypoint.FileInspector("/non/existing/file")
    actual = testee.is_group_accessible()
    assert actual == False
    assert not os.stat.called


def test_file_inspector_group_accessible(accessible_file):
    testee = entrypoint.FileInspector(accessible_file)
    assert testee.is_group_accessible()


def test_file_inspector_not_group_accessible(non_accessible_file, caplog):
    testee = entrypoint.FileInspector(non_accessible_file)
    assert not testee.is_group_accessible()
    assert re.match(r"ERROR .* No rw permissions for group", caplog.text)


def test_group_access_unknown_group_id():
    testee = entrypoint.GroupAccess(None, None)
    assert testee._find_group(9999999) is None


def test_group_access_enable_existing_group(mocker, capsys):
    grdb_entry = MagicMock(gr_name="existing")
    mocker.patch("grp.getgrgid", return_value=grdb_entry)
    testee = entrypoint.GroupAccess("jennifer", entrypoint.Group("other", 666))
    testee._run = print
    actual = testee.enable()
    captured = capsys.readouterr()
    assert captured.out == "usermod --append --groups existing jennifer\n"
    assert actual == entrypoint.Group("existing", 666)


def test_group_access_enable_unknown_gid(mocker, capsys):
    mocker.patch("grp.getgrgid", side_effect=KeyError)
    testee = entrypoint.GroupAccess("jennifer", entrypoint.Group("other", 666))
    testee._run = print
    actual = testee.enable()
    captured = capsys.readouterr()
    assert captured.out == "groupmod -g 666 other\n"
    assert actual == entrypoint.Group("other", 666)
