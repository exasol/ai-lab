import pytest
import os
import re
import stat

from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint

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


@pytest.fixture
def accessible_file(tmp_path):
    mode = os.stat(tmp_path).st_mode | stat.S_IRGRP | stat.S_IWGRP
    os.chmod(tmp_path, mode)
    return tmp_path


@pytest.fixture
def non_accessible_file(tmp_path):
    mode = stat.S_IRUSR | stat.S_IWUSR
    os.chmod(tmp_path, mode)
    return tmp_path


def test_file_inspector_group_accessible(accessible_file):
    testee = entrypoint.FileInspector(accessible_file)
    assert testee.is_group_accessible()


def test_file_inspector_not_group_accessible(non_accessible_file, caplog):
    testee = entrypoint.FileInspector(non_accessible_file)
    assert not testee.is_group_accessible()
    assert re.match(r"ERROR .* No rw permissions for group", caplog.text)
