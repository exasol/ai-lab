import os
import pprint
from pathlib import Path

import pytest
from exasol.nb_connector.secret_store import Secrets
from exasol.nb_connector.ai_lab_config import AILabConfig as CKey

# We need to manually import all fixtures that we use, directly or indirectly,
# since the pytest won't do this for us.
from notebook_test_utils import (
    backend_setup,
    notebook_runner,
    uploading_hack,
    set_log_level_for_libraries,
)

set_log_level_for_libraries()


def _store_pre_release_access(store_path: Path, store_password: str) -> None:
    conf = Secrets(store_path, store_password)
    conf.connection()
    conf.save(CKey.text_ai_pre_release_url, os.environ["NBTEST_TXAIE_ZIP_URL"])
    conf.save(CKey.text_ai_zip_password, os.environ["NBTEST_TXAIE_ZIP_PASSWORD"])


def test_text_ai(notebook_runner, backend_setup, uploading_hack) -> None:
    """
    This test currently requires some specific Jupyter notebooks which are work in progress
    and is only executed if the folder work_in_progress exists.
    """
    store_path, store_password = backend_setup
    _store_pre_release_access(store_path, store_password)

    current_dir = os.getcwd()
    try:
        notebook_runner('main_config.ipynb')
        os.chdir("data")
        notebook_runner(notebook_file="data_customer_support.ipynb", hacks=[uploading_hack])
        os.chdir(current_dir)
        os.chdir("text_ai")
        result = notebook_runner(notebook_file='txaie_init.ipynb', hacks=[uploading_hack])
        notebook_runner(notebook_file="txaie_preprocessing.ipynb", hacks=[uploading_hack])
    finally:
        os.chdir(current_dir)


