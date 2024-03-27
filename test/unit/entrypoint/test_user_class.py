import grp
import os
import pwd
import pytest
import unittest

from pathlib import Path
from unittest.mock import MagicMock, create_autospec
from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint
from test.unit.entrypoint.entrypoint_mock import entrypoint_method


@pytest.fixture
def user():
    return entrypoint.User(
        "jennifer",
        entrypoint.Group("users", 901),
        entrypoint.Group("docker", 902),
    )


@pytest.fixture
def user_with_id(mocker, user):
    user._id = 100
    return user


def test_group(mocker):
    mocker.patch("grp.getgrnam")
    testee = entrypoint.Group("my-group").id
    assert grp.getgrnam.called
    assert grp.getgrnam.call_args == mocker.call("my-group")


@pytest.mark.parametrize(
    "user, group, docker, expected", [
        (None, "group", "docker", False),
        ("user", None, "docker", False),
        ("user", "group", None, False),
        ("user", "group", "docker_group", True),
    ])
def test_user_specified(user, group, docker, expected):
    testee = entrypoint.User(
        user,
        entrypoint.Group(group),
        entrypoint.Group(docker),
    )
    assert expected == testee.is_specified


def test_uid(mocker, user):
    passwd_struct = MagicMock(pw_uid=444)
    mocker.patch("pwd.getpwnam", return_value=passwd_struct)
    assert 444 == user.id \
        and pwd.getpwnam.called \
        and pwd.getpwnam.call_args == mocker.call("jennifer")


def test_chown_recursive(mocker, user, tmp_path):
    child = tmp_path / "child"
    sub = tmp_path / "sub"
    grand_child = sub / "grand_child"
    child.touch()
    sub.mkdir()
    grand_child.touch()
    mocker.patch("os.chown")
    passwd_struct = MagicMock(pw_uid=444)
    mocker.patch("pwd.getpwnam", return_value=passwd_struct)
    user.chown_rec(tmp_path)
    expected = [ mocker.call(f, user.id, user.group.id) for f in (
        tmp_path, child, sub, grand_child,
    )]
    assert expected == os.chown.call_args_list


def test_enable_file_absent(mocker, user):
    mocker.patch(entrypoint_method("GroupAccess"))
    user.enable_group_access(Path("/non/existing/path"))
    assert not entrypoint.GroupAccess.called


def test_enable_non_accessible_file(mocker, user, non_accessible_file):
    mocker.patch(entrypoint_method("GroupAccess"))
    with pytest.raises(PermissionError, match="No rw permissions for group"):
        user.enable_group_access(non_accessible_file)
    assert not entrypoint.GroupAccess.called


def group_access(mocker, group: entrypoint.Group, find_result: str) -> entrypoint.GroupAccess:
    mocker.patch("subprocess.run")
    if find_result is None:
        mocker.patch("grp.getgrgid", side_effect=KeyError)
    else:
        grp_struct = MagicMock(gr_name=find_result)
        mocker.patch("grp.getgrgid", return_value=grp_struct)
    group_access = entrypoint.GroupAccess("user_name", group)
    return group_access


def test_enable_existing_group(mocker, user, accessible_file):
    gid = entrypoint.FileInspector(accessible_file).group_id
    group = entrypoint.Group(user.docker_group.name, gid)
    mocker.patch(
        entrypoint_method("GroupAccess"),
        return_value=group_access(mocker, group, group.name),
    )
    mocker.patch("os.setgroups")
    user.enable_group_access(accessible_file)
    assert os.setgroups.called and \
        os.setgroups.call_args == mocker.call([user.docker_group.id]) and \
        user.docker_group == group


def test_enable_unknown_group(mocker, user, accessible_file):
    group_name = user.docker_group.name
    gid = entrypoint.FileInspector(accessible_file).group_id
    group = entrypoint.Group(group_name, gid)
    mocker.patch(
        entrypoint_method("GroupAccess"),
        return_value=group_access(mocker, group, None),
    )
    mocker.patch("os.setgroups")
    user.enable_group_access(accessible_file)
    assert os.setgroups.called and \
        os.setgroups.call_args == mocker.call([user.docker_group.id]) and \
        user.docker_group == entrypoint.Group(group_name, gid)


def test_switch_to(mocker, user_with_id):
    mocker.patch("os.setresuid")
    mocker.patch("os.setresgid")
    user_with_id.switch_to()
    assert os.setresuid.called
    uid = user_with_id.id
    assert os.setresuid.call_args == mocker.call(uid, uid, uid)
    assert os.setresgid.called
    gid = user_with_id.group.id
    assert os.setresgid.call_args == mocker.call(gid, gid, gid)
