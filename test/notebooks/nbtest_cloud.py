import os

import pytest

from notebook_test_utils import (
    access_to_temp_secret_store,
    access_to_temp_saas_secret_store,
    notebook_runner,
    set_log_level_for_libraries,
)
from exasol.nb_connector.ai_lab_config import StorageBackend

set_log_level_for_libraries()

@pytest.mark.parametrize('notebook_runner', [StorageBackend.onprem, StorageBackend.saas], indirect=True)
def test_cloud_notebook(notebook_runner) -> None:

    current_dir = os.getcwd()
    try:
        notebook_runner('main_config.ipynb')
        os.chdir('cloud')
        notebook_runner('01_import_data.ipynb')
    finally:
        os.chdir(current_dir)
