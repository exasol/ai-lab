import os
from pathlib import Path

import pytest

from notebook_test_utils import (access_to_temp_secret_store,
                                 access_to_temp_saas_secret_store,
                                 run_notebook,
                                 uploading_hack)
from exasol.nb_connector.ai_lab_config import AILabConfig as CKey, StorageBackend
from exasol.nb_connector.secret_store import Secrets


def _slc_repo_dir() -> Path:
    return Path.cwd() / "script_languages_release"


def _store_slc_config(store_path: Path, store_password: str, clone_repo: bool):

    slc_source = "Clone script languages release repository" if clone_repo else "Use the existing clone"
    conf = Secrets(store_path, store_password)
    conf.connection()
    conf.save(CKey.slc_source, slc_source)
    conf.save(CKey.slc_target_dir, str(_slc_repo_dir()))

@pytest.fixture()
def cleanup_slc_repo_dir():
    import shutil
    yield
    p = Path.cwd() / "script_languages_container" / "script_languages_release"
    shutil.rmtree(p)


@pytest.mark.parametrize('access_to_temp_secret_store', [StorageBackend.onprem], indirect=True)
def test_script_languages_container_cloning_slc_repo(access_to_temp_secret_store,
                                                     cleanup_slc_repo_dir) -> None:
    current_dir = Path.cwd()
    store_path, store_password = access_to_temp_secret_store
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


def _clone_slc_repo():
    from git import Repo
    repo = Repo.clone_from("https://github.com/exasol/script-languages-release", _slc_repo_dir())
    repo.submodule_update(recursive=True)


@pytest.mark.parametrize('access_to_temp_secret_store', [StorageBackend.onprem], indirect=True)
def test_script_languages_container_with_existing_slc_repo(access_to_temp_secret_store,
                                                           cleanup_slc_repo_dir) -> None:
    current_dir = Path.cwd()
    store_path, store_password = access_to_temp_secret_store
    store_file = str(store_path)
    try:
        run_notebook('main_config.ipynb', store_file, store_password)
        os.chdir('./script_languages_container')
        slc_repo_path = _slc_repo_dir()
        assert not slc_repo_path.is_dir()
        _clone_slc_repo()
        _store_slc_config(store_path, store_password, False)
        run_notebook('configure_slc_repository.ipynb', store_file, store_password)
        run_notebook('export_as_is.ipynb', store_file, store_password)
        run_notebook('customize.ipynb', store_file, store_password)
        run_notebook('test_slc.ipynb', store_file, store_password)
        run_notebook('advanced.ipynb', store_file, store_password)
        run_notebook('using_the_script_languages_container_tool.ipynb', store_file, store_password)
    finally:
        os.chdir(current_dir)
