from typing import List, Tuple, Optional, Callable
from pathlib import Path
from functools import partial
import random
import string
import textwrap
import logging
from inspect import cleandoc

import pytest
import nbformat
from nbclient import NotebookClient
import requests

from exasol.nb_connector.secret_store import Secrets
from exasol.nb_connector.ai_lab_config import AILabConfig as CKey, StorageBackend
from exasol.nb_connector.itde_manager import (
    bring_itde_up,
    take_itde_down
)
from exasol.pytest_backend import BACKEND_ONPREM, BACKEND_SAAS


LOG = logging.getLogger(__name__)


def generate_password(pwd_length):
    pwd_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(pwd_characters) for _ in range(pwd_length))


def url_exists(url):
    try:
        response = requests.head(url)
        return response.status_code < 400
    except requests.ConnectionError:
        return False


def _insert_hacks(nb: nbformat.NotebookNode, hacks: List[Tuple[str, str]]):

    def cell_match(nb_cell, ins_tag: str) -> bool:
        return ('tags' in nb_cell.metadata) and (ins_tag in nb_cell.metadata['tags'])

    for hack in hacks:
        insertion_tag, hack_content = hack
        # Find the sequential numbers of the target cells.
        location_cell_nums = [cell_no for cell_no, nb_cell in enumerate(nb.cells)
                              if cell_match(nb_cell, insertion_tag)]
        # Insert the hack cell after each cell located at the previous step.
        for cell_no in location_cell_nums[::-1]:
            hack_cell = nbformat.v4.new_code_cell(hack_content)
            nb.cells.insert(cell_no + 1, hack_cell)


def run_notebook(notebook_file: str, store_file: str, store_password: str,
                 timeout: int = -1, hacks: Optional[List[Tuple[str, str]]] = None) -> None:
    """
    Executes notebook with added access to the configuration store.

    Parameters:
        notebook_file:  Notebook file.
        store_file:     Configuration store file.
        store_password: Configuration store password.
        timeout:        Optional timeout in seconds
        hacks:          Optional hacks to be inserted into the notebook
                        before running it.
    """

    nb = nbformat.read(notebook_file, as_version=4)

    if hacks:
        _insert_hacks(nb, hacks)

    # Insert the following code at the beginning of the notebook
    init_code = f'''
    def init_notebook_test():
        from pathlib import Path
        from exasol.nb_connector.secret_store import Secrets
        global ai_lab_config
        ai_lab_config = Secrets(Path("{store_file}"), "{store_password}")
    init_notebook_test()
    '''
    nb.cells.insert(0, nbformat.v4.new_code_cell(init_code))

    # Execute the notebook object, expecting to get no exceptions.
    nb_client = NotebookClient(nb, timeout=timeout, kernel_name='python3')
    nb_client.execute()


# ~/git/ai-lab/test/notebooks/notebook_test_utils.py
def set_log_level_for_libraries(level=logging.WARNING):
    modules = cleandoc(
        """
        traitlets
        luigi-interface
        luigi-interface.PrepareDockerNetworkForTestEnvironment
        luigi-interface.SpawnTestDockerDatabase
        luigi-interface.SpawnTestEnvironmentWithDockerDB
        luigi-interface.WaitForTestDockerDatabase
        httpx
        """
    ).split()
    LOG.info(
        f"Setting log level to '%s' for modules\n  - %s",
        logging.getLevelName(level),
        "\n  - ".join(modules),
    )
    for m in modules:
        logging.getLogger(m).setLevel(level)


@pytest.fixture(scope='session')
def backend_setup(backend,
                  saas_host,
                  saas_pat,
                  saas_account_id,
                  database_name,
                  backend_aware_onprem_database,
                  backend_aware_saas_database_id,
                  tmp_path_factory) -> Tuple[Path, str]:
    """
    Creates a temporary configuration store and initialises it according to the
    backend in use.
    """

    store_path = tmp_path_factory.mktemp('tmp_config_dir') / 'tmp_config_saas.sqlite'
    store_password = generate_password(12)
    secrets = Secrets(store_path, master_password=store_password)
    secrets.save(CKey.db_schema, 'NOTEBOOK_TESTS')

    if backend == BACKEND_ONPREM:
        secrets.save(CKey.storage_backend, StorageBackend.onprem.name)
        secrets.save(CKey.use_itde, 'yes')
        bring_itde_up(secrets, backend_aware_onprem_database)
        try:
            yield store_path, store_password
        finally:
            take_itde_down(secrets, False)

    elif backend == BACKEND_SAAS:
        secrets.save(CKey.storage_backend, StorageBackend.saas.name)
        secrets.save(CKey.saas_url, saas_host)
        secrets.save(CKey.saas_token, saas_pat)
        secrets.save(CKey.saas_account_id, saas_account_id)
        # Although we know the database id, we want to test the
        # case when we don't and have to look up the db name.
        secrets.save(CKey.saas_database_name, database_name)
        yield store_path, store_password

    else:
        raise RuntimeError(f'Unknown backend {backend}')


@pytest.fixture
def notebook_runner(backend_setup) -> Callable:
    """
    A fixture for running a notebook.
    """
    store_path, store_password = backend_setup
    return partial(run_notebook,
                   store_file=str(store_path),
                   store_password=store_password)


@pytest.fixture
def uploading_hack() -> Tuple[str, str]:
    """
    This fixture is a hack that inserts a pause after uploading a big archive into the BucketFS.
    The BucketFS performs the decompression and file copying asynchronously. The files may still
    not be ready after the call to the BucketFS function returns. This hack ensures that this
    operation is completed before resuming the notebook execution from the next cell.
    """
    return (
        'uploading_model',
        textwrap.dedent("""
        def pause_notebook_execution():
            import time
            time.sleep(20)

        pause_notebook_execution()
        """)
    )
