import os

# We need to manually import all fixtures that we use, directly or indirectly,
# since the pytest won't do this for us.
from notebook_test_utils import (
    backend_setup,
    notebook_runner,
    set_log_level_for_libraries,
)

set_log_level_for_libraries()


def test_cloud_notebook(notebook_runner) -> None:
    current_dir = os.getcwd()
    try:
        notebook_runner('main_config.ipynb')
        os.chdir('cloud')
        notebook_runner('01_import_data.ipynb')
    finally:
        os.chdir(current_dir)


def test_s3_vs_notebook(notebook_runner) -> None:
    current_dir = os.getcwd()
    try:
        notebook_runner('main_config.ipynb')
        os.chdir('cloud')
        notebook_runner('02_s3_vs_reuters.ipynb')
    finally:
        os.chdir(current_dir)