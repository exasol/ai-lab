import os
import textwrap
from pathlib import Path

import pytest

from notebook_test_utils import (access_to_temp_secret_store,
                                 access_to_temp_saas_secret_store,
                                 run_notebook,
                                 uploading_hack)
from exasol.nb_connector.ai_lab_config import AILabConfig as CKey, StorageBackend
from exasol.nb_connector.secret_store import Secrets


def _store_slc_config(store_path: Path, store_password: str, target_dir: Path):

    conf = Secrets(store_path, store_password)
    conf.connection()
    conf.save(CKey.slc_source, "Clone script languages release repository")
    conf.save(CKey.slc_target_dir, str(target_dir))

@pytest.mark.parametrize(
    "notebook_file",
    [
        'using_a_script_languages_container.ipynb',
    ]
)
@pytest.mark.parametrize('access_to_temp_secret_store', [StorageBackend.onprem], indirect=True)
def test_script_languages_container(access_to_temp_secret_store, uploading_hack, notebook_file) -> None:
    current_dir = os.getcwd()
    store_path, store_password = access_to_temp_secret_store
    store_file = str(store_path)
    try:

        run_notebook('main_config.ipynb', store_file, store_password)
        os.chdir('./script_languages_container')
        run_notebook('configure_slc_flavor.ipynb', store_file, store_password)
        run_notebook('using_a_script_language_container.ipynb', store_file, store_password)
    finally:
        os.chdir(current_dir)
