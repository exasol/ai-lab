import os
import pytest

from exasol.nb_connector.ai_lab_config import StorageBackend
from notebook_test_utils import (
    access_to_temp_secret_store,
    access_to_temp_saas_secret_store,
    notebook_runner,
    set_log_level_for_libraries,
)


set_log_level_for_libraries()


@pytest.mark.parametrize('notebook_runner', [StorageBackend.onprem, StorageBackend.saas], indirect=True)
def test_regression(notebook_runner) -> None:

    current_dir = os.getcwd()
    try:
        notebook_runner('main_config.ipynb')
        os.chdir('./data')
        notebook_runner('data_abalone.ipynb')
        os.chdir('../sklearn')
        notebook_runner('sklearn_fix_version.ipynb')
        notebook_runner('sklearn_predict_udf.ipynb')
        notebook_runner('sklearn_train_abalone.ipynb')
        notebook_runner('sklearn_predict_abalone.ipynb')
    finally:
        os.chdir(current_dir)


@pytest.mark.parametrize('notebook_runner', [StorageBackend.onprem, StorageBackend.saas], indirect=True)
def test_classification(notebook_runner) -> None:

    current_dir = os.getcwd()
    try:
        notebook_runner('main_config.ipynb')
        os.chdir('./data')
        notebook_runner('data_telescope.ipynb')
        os.chdir('../sklearn')
        notebook_runner('sklearn_predict_udf.ipynb')
        notebook_runner('sklearn_train_telescope.ipynb')
        notebook_runner('sklearn_predict_telescope.ipynb')
    finally:
        os.chdir(current_dir)
