import grp
import os
import pwd
import pytest

from unittest.mock import MagicMock, create_autospec
from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint


def group(name: str, id: int):
    group = entrypoint.Group(name)
    group._id = id
    return group


@pytest.fixture
def user():
    return entrypoint.User(
        "jennifer",
        group("family", 901),
        group("docker", 902),
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
    mocker.patch("pwd.getpwnam")
    user.uid
    assert pwd.getpwnam.called
    assert pwd.getpwnam.call_args == mocker.call("jennifer")


def test_chown_file_absent(mocker, user):
    mocker.patch("os.chown")
    user.own("/non/existing/path")
    assert not os.chown.called


def test_chown_file_exists(mocker, tmp_path, user_with_id):
    mocker.patch("os.chown")
    user_with_id.own(tmp_path)
    assert os.chown.called
    assert os.chown.call_args == mocker.call(tmp_path, -1, 902)


def test_switch_to(mocker, user_with_id):
    mocker.patch("os.setresuid")
    mocker.patch("os.setresgid")
    mocker.patch("os.setgroups")
    user_with_id.switch_to()
    assert os.setresuid.called
    assert os.setresuid.call_args == mocker.call(100, 100, 100)
    assert os.setresgid.called
    assert os.setresgid.call_args == mocker.call(901, 901, 901)
    assert os.setgroups.called
    assert os.setgroups.call_args == mocker.call([902])
