import grp
import os
import pwd
import pytest

from unittest.mock import MagicMock
from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint


@pytest.fixture
def user():
    return entrypoint.User("jennifer", "heroes")


@pytest.fixture
def user_with_id(mocker, user):
    mocker.patch("pwd.getpwnam", return_value=MagicMock(pw_uid=123))
    mocker.patch("grp.getgrnam", return_value=MagicMock(gr_gid=456))
    return user


def test_uid(mocker, user):
    mocker.patch("pwd.getpwnam")
    user.uid
    assert pwd.getpwnam.called
    assert pwd.getpwnam.call_args == mocker.call("jennifer")


def test_gid(mocker, user):
    mocker.patch("grp.getgrnam")
    user.gid
    assert grp.getgrnam.called
    assert grp.getgrnam.call_args == mocker.call("heroes")


def test_chown_file_absent(mocker, user):
    mocker.patch("os.chown")
    user.own("/non/existing/path")
    assert not os.chown.called


def test_chown_file_exists(mocker, tmp_path, user_with_id):
    mocker.patch("os.chown")
    user_with_id.own(tmp_path)
    assert os.chown.called
    assert os.chown.call_args == mocker.call(tmp_path, -1, 456)


def test_switch_to(mocker, user_with_id):
    mocker.patch("os.setresuid")
    mocker.patch("os.setresgid")
    user_with_id.switch_to()
    assert os.setresuid.called
    assert os.setresuid.call_args == mocker.call(123, 123, 123)
    assert os.setresgid.called
    assert os.setresgid.call_args == mocker.call(456, 456, 456)
