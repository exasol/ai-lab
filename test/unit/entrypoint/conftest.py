import os
import pytest
import stat


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
