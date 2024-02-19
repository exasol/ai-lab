import os
from notebook_test_utils import access_to_temp_secret_store, notebook_runner


def test_cloud_notebook(notebook_runner) -> None:

    current_dir = os.getcwd()
    try:
        notebook_runner('main_config.ipynb')
        notebook_runner('cloud_store_config.ipynb')
        os.chdir('../cloud')
        notebook_runner('01_import_data.ipynb')
    finally:
        os.chdir(current_dir)
