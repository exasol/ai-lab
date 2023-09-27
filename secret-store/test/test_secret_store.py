import os
import pytest
from pathlib import Path
from secret_store import Secrets, Credentials
from sqlcipher3 import dbapi2 as sqlcipher


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
    secrets.save("key", credentials).close()
    assert secrets.get_credentials("key") == credentials


def test_config_item(secrets):
    config_item = "some configuration"
    secrets.save("key", config_item).close()
    assert secrets.get_config_item("key") == config_item


def test_update_credentials(secrets):
    initial = Credentials("user", "password")
    secrets.save("key", initial).close()
    other = Credentials("other", "changed")
    secrets.save("key", other)
    secrets.close()
    assert secrets.get_credentials("key") == other


def test_update_config_item(secrets):
    initial = "initial value"
    secrets.save("key", initial).close()
    other = "other value"
    secrets.save("key", other).close()
    assert secrets.get_config_item("key") == other


def test_wrong_password(sample_file):
    secrets = Secrets(sample_file, "correct password")
    secrets.save("key", Credentials("usr", "pass")).close()
    invalid = Secrets(sample_file, "wrong password")
    with pytest.raises(sqlcipher.DatabaseError) as ex:
        invalid.get_credentials("key")
    assert "file is not a database" == str(ex.value)
