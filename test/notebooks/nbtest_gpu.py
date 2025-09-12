import os
from pathlib import Path
import shutil

import pytest

# We need to manually import all fixtures that we use, directly or indirectly,
# since the pytest won't do this for us.
from notebook_test_utils import (backend_setup,
                                 run_notebook, uploading_hack)
from exasol.nb_connector.ai_lab_config import AILabConfig as CKey
from exasol.nb_connector.slc import ScriptLanguageContainer
from exasol.nb_connector.secret_store import Secrets
from exasol.pytest_backend import BACKEND_ONPREM
from exasol.slc.api import push as exaslct_push

from exasol.nb_connector.language_container_activation import open_pyexasol_connection_with_lang_definitions

conn = open_pyexasol_connection_with_lang_definitions(secrets, schema=secrets.db_schema,
                                                      compression=True)
from exasol.python_extension_common.deployment.extract_validator import ExtractValidator
from datetime import (
    timedelta,
)
import exasol.bucketfs as bfs
from exasol.nb_connector.slc.constants import PATH_IN_BUCKET


def _upload_docker_img_to_cache(slc: ScriptLanguageContainer):
    """
    Building the SLC for the CUDA template flavor takes a very large amount of time.
    In order to speed up the tests, we upload the container
    """
    if "TARGET_DOCKER_PASSWORD" in os.environ and "TARGET_DOCKER_USERNAME" in os.environ:
        from exasol.nb_connector.slc import ScriptLanguageContainer
        target_docker_username = os.environ["TARGET_DOCKER_USERNAME"]
        exaslct_push(flavor_path=slc.flavor_path,
                     target_docker_username=target_docker_username)

def _wait_for_slc_to_become_available(secrets: Secrets, slc: ScriptLanguageContainer):
    def cb(nproc, pending):
        print(f"{len(pending)} of {nproc} nodes are still pending.")

    ev = ExtractValidator(pyexasol_connection=conn, timeout=timedelta(minutes=5), callback=cb)
    url = f"http://{secrets.bfs_host_name}:{secrets.bfs_port}"
    print(url)
    bfs_archive_path = bfs.path.build_path(
        backend=bfs.path.StorageBackend.onprem,
        url=url,
        bucket_name=secrets.bfs_bucket,
        service_name=secrets.bfs_service,
        username="",
        password="",
        verify=False,
        path=f"{PATH_IN_BUCKET}/{slc.flavor}-release-{slc.language_alias}",
    )
    print(bfs_archive_path.as_udf_path())
    ev.verify_all_nodes(schema=secrets.db_schema, language_alias=slc.language_alias,
                        bfs_archive_path=bfs_archive_path)


@pytest.fixture()
def finish_slc_repo_dir(backend, backend_setup):
    yield
    if backend == BACKEND_ONPREM:
        p = Path.cwd() / "gpu_in_udf" / "slc_workspace"
        shutil.rmtree(p)


def test_gpu_notebooks(backend, backend_setup, finish_slc_repo_dir, uploading_hack) -> None:
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
        secrets = Secrets(store_path, master_password=store_password)
        slc = ScriptLanguageContainer(secrets=secrets, name="gpu_slc")
        _wait_for_slc_to_become_available(secrets, slc)
        run_notebook('basic_udf_with_gpu.ipynb', store_file, store_password)
        run_notebook('advanced_udf_with_gpu.ipynb', store_file, store_password) #, hacks=[uploading_hack]
        _upload_docker_img_to_cache(slc)
    finally:
        os.chdir(current_dir)
