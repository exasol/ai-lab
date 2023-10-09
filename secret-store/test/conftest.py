import pytest
from pathlib import Path
from secret_store import Secrets


@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    return tmp_path / "sample_database.db"


@pytest.fixture
def secrets(sample_file) -> Path:
    return Secrets(sample_file, master_password="abc")
