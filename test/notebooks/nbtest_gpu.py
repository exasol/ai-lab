import os
from pathlib import Path
import shutil
from typing import Tuple

import pytest

# We need to manually import all fixtures that we use, directly or indirectly,
# since the pytest won't do this for us.
from notebook_test_utils import (backend_setup,
                                 run_notebook, generate_password)
from exasol.nb_connector.ai_lab_config import AILabConfig as CKey
from exasol.nb_connector.slc import ScriptLanguageContainer
from exasol.nb_connector.secret_store import Secrets
from exasol.pytest_backend import BACKEND_ONPREM


@pytest.fixture()
def cleanup_slc_repo_dir(backend):
    yield
    if backend == BACKEND_ONPREM:
        p = Path.cwd() / "gpu_in_udf" / "slc_workspace"
        shutil.rmtree(p)

def test_gpu_notebooks(backend, backend_setup, cleanup_slc_repo_dir) -> None:
    if backend != BACKEND_ONPREM:
        pytest.skip()
    if os.getenv("NBTEST_USE_GPU", "false") != "true":
        pytest.skip()
    current_dir = Path.cwd()
    store_path, store_password = backend_setup
    store_file = str(store_path)
    try:
        run_notebook('main_config.ipynb', store_file, store_password)
        os.chdir('./cloud')
        run_notebook('02_s3_vs_reuters.ipynb', store_file, store_password)
        os.chdir('../gpu_in_udf')
        #run_notebook('setup.ipynb', store_file, store_password)
        run_notebook('basic_udf_with_gpu.ipynb', store_file, store_password)
        run_notebook('advanced_udf_with_gpu.ipynb', store_file, store_password)
    finally:
        os.chdir(current_dir)
