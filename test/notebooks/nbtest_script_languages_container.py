import os
from pathlib import Path
import shutil

import pytest

# We need to manually import all fixtures that we use, directly or indirectly,
# since the pytest won't do this for us.
from notebook_test_utils import (backend_setup,
                                 run_notebook)
from exasol.nb_connector.ai_lab_config import AILabConfig as CKey
from exasol.nb_connector.slct_manager import SlctManager
from exasol.nb_connector.secret_store import Secrets
from exasol.pytest_backend import BACKEND_ONPREM


def _slc_repo_dir() -> Path:
    return Path.cwd() / "script_languages_release"


def _store_slc_config(store_path: Path, store_password: str, clone_repo: bool) -> Secrets:

    slc_source = "Clone script languages release repository" if clone_repo else "Use the existing clone"
    conf = Secrets(store_path, store_password)
    conf.connection()
    conf.save(CKey.slc_source, slc_source)
    conf.save(CKey.slc_target_dir, str(_slc_repo_dir()))
    return conf


@pytest.fixture()
def cleanup_slc_repo_dir(backend):
    yield
    if backend == BACKEND_ONPREM:
        p = Path.cwd() / "script_languages_container" / "script_languages_release"
        shutil.rmtree(p)


def test_script_languages_container_cloning_slc_repo(backend,
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
        _store_slc_config(store_path, store_password, True)
        run_notebook('configure_slc_repository.ipynb', store_file, store_password)
        run_notebook('export_as_is.ipynb', store_file, store_password)
        run_notebook('customize.ipynb', store_file, store_password)
        run_notebook('test_slc.ipynb', store_file, store_password)
        run_notebook('advanced.ipynb', store_file, store_password)
        run_notebook('using_the_script_languages_container_tool.ipynb', store_file, store_password)
    finally:
        os.chdir(current_dir)


def test_script_languages_container_with_existing_slc_repo(backend,
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
        slc_repo_path = _slc_repo_dir()
        assert not slc_repo_path.is_dir()
        secrets = _store_slc_config(store_path, store_password, False)
        slct_manager = SlctManager(secrets)
        slct_manager.clone_slc_repo()
        run_notebook('configure_slc_repository.ipynb', store_file, store_password)
        run_notebook('export_as_is.ipynb', store_file, store_password)
        run_notebook('customize.ipynb', store_file, store_password)
        run_notebook('test_slc.ipynb', store_file, store_password)
        run_notebook('advanced.ipynb', store_file, store_password)
        run_notebook('using_the_script_languages_container_tool.ipynb', store_file, store_password)
    finally:
        os.chdir(current_dir)
