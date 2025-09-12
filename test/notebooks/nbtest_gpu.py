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
from exasol.slc.api import push as exaslct_push

def _upload_docker_img_to_cache(backend, backend_setup):
    """
    Building the SLC for the CUDA template flavor takes a very large amount of time.
    In order to speed up the tests, we upload the container
    """
    if "TARGET_DOCKER_PASSWORD" in os.environ and "TARGET_DOCKER_USERNAME" in os.environ:
        from exasol.nb_connector.slc import ScriptLanguageContainer
        store_path, store_password = backend_setup
        secrets = Secrets(store_path, master_password=store_password)
        slc = ScriptLanguageContainer(secrets=secrets, name="gpu_slc")

        target_docker_username = os.environ["TARGET_DOCKER_USERNAME"]

        exaslct_push(flavor_path=slc.flavor_path,
                     target_docker_username=target_docker_username)


@pytest.fixture()
def finish_slc_repo_dir(backend, backend_setup):
    yield
    if backend == BACKEND_ONPREM:
        p = Path.cwd() / "gpu_in_udf" / "slc_workspace"
        _upload_docker_img_to_cache(backend, backend_setup)
        shutil.rmtree(p)

def test_gpu_notebooks(backend, backend_setup, finish_slc_repo_dir) -> None:
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
        run_notebook('setup.ipynb', store_file, store_password)
        run_notebook('basic_udf_with_gpu.ipynb', store_file, store_password)
        run_notebook('advanced_udf_with_gpu.ipynb', store_file, store_password)
    finally:
        os.chdir(current_dir)
