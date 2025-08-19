import os
from pathlib import Path
import shutil

import pytest

# We need to manually import all fixtures that we use, directly or indirectly,
# since the pytest won't do this for us.
from notebook_test_utils import (backend_setup,
                                 run_notebook)
from exasol.nb_connector.ai_lab_config import AILabConfig as CKey
from exasol.nb_connector.slc import ScriptLanguageContainer
from exasol.nb_connector.secret_store import Secrets
from exasol.pytest_backend import BACKEND_ONPREM


TEST_FLAVOR = "template-Exasol-all-python-3.10"


@pytest.fixture()
def cleanup_slc_repo_dir(backend):
    yield
    if backend == BACKEND_ONPREM:
        p = Path.cwd() / "script_languages_container" / "slc_workspace"
        shutil.rmtree(p)


def test_script_languages_container(backend,
                                                     backend_setup,
                                                     cleanup_slc_repo_dir) -> None:
    if backend != BACKEND_ONPREM:
        pytest.skip()
    current_dir = Path.cwd()
    store_path, store_password = backend_setup
    store_file = str(store_path)
    try:
        run_notebook('main_config.ipynb', store_file, store_password)
        os.chdir('./script_languages_container')
        run_notebook('configure_slc_repository.ipynb', store_file, store_password)
        run_notebook('export_as_is.ipynb', store_file, store_password)
        run_notebook('customize.ipynb', store_file, store_password)
        run_notebook('test_slc.ipynb', store_file, store_password)
        run_notebook('advanced.ipynb', store_file, store_password)
        run_notebook('using_the_script_languages_container_tool.ipynb', store_file, store_password)
    finally:
        os.chdir(current_dir)
