import os
import pytest
from pathlib import Path
from secret_store import Secrets, Credentials


@pytest.fixture
def sample_file(tmp_path) -> Path:
    return tmp_path / "sample_database.db"


@pytest.fixture
def secrets(sample_file) -> Path:
    return Secrets(sample_file, master_password="abc")


def test_no_database_file(secrets):
    assert not os.path.exists(secrets.db_file)


def test_database_file_from_credentials(secrets):
    assert secrets.get_credentials("a") is None
    assert os.path.exists(secrets.db_file)


def test_database_file_from_config_item(secrets):
    assert secrets.get_config_item("a") is None
    assert os.path.exists(secrets.db_file)


def test_credentials(secrets):
    credentials = Credentials("user", "password")
    secrets.save("app", credentials)
    secrets.close()
    assert secrets.get_credentials("app") == credentials


def test_config_item(secrets):
    config_item = "some configuration"
    secrets.save("url", config_item)
    secrets.close()
    assert secrets.get_config_item("url") == config_item


def test_update_credentials(secrets):
    initial = Credentials("user", "password")
    secrets.save("app", initial)
    secrets.close()
    other = Credentials("other", "changed")
    secrets.save("app", other)
    secrets.close()
    assert secrets.get_credentials("app") == other


def test_update_config_item(secrets):
    initial = "initial value"
    secrets.save("url", initial)
    secrets.close()
    other = "other value"
    secrets.save("url", other)
    secrets.close()
    assert secrets.get_config_item("url") == other
