import os
import pwd
import pytest

from unittest.mock import MagicMock
from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint


@pytest.fixture
def user():
    return entrypoint.User("jennifer")


@pytest.fixture
def user_with_id(mocker, user):
    mocker.patch("pwd.getpwnam", return_value=MagicMock(pw_uid=123))
    return user


def test_id(mocker, user):
    mocker.patch("pwd.getpwnam")
    user.id
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
    assert os.chown.call_args == mocker.call(tmp_path, 123, -1)


def test_switch_to(mocker, user_with_id):
    mocker.patch("os.setresuid")
    user_with_id.switch_to()
    assert os.setresuid.called
    assert os.setresuid.call_args == mocker.call(123, 123, 123)
