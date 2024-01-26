import os

from notebook_test_utils import (access_to_temp_secret_store, notebook_runner)


def test_regression(notebook_runner) -> None:

    current_dir = os.getcwd()
    try:
        notebook_runner('main_config.ipynb')
        os.chdir('./data')
        notebook_runner('data_abalone.ipynb')
        os.chdir('../sklearn')
        notebook_runner('sklearn_predict_udf.ipynb')
        notebook_runner('sklearn_train_abalone.ipynb')
        notebook_runner('sklearn_predict_abalone.ipynb')
    finally:
        os.chdir(current_dir)
