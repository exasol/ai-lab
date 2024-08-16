from typing import List, Tuple, Optional, Callable
from pathlib import Path
from functools import partial
import random
import string
import textwrap
from contextlib import contextmanager, ExitStack
from datetime import timedelta
import logging
import os
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
from exasol.saas.client.api_access import (
    OpenApiAccess,
    create_saas_client,
    timestamp_name,
)

LOG = logging.getLogger(__name__)

def _env(var: str) -> str:
    result = os.environ.get(var)
    if result:
        return result
    raise RuntimeError(f"Environment variable {var} is empty.")


def generate_password(pwd_length):
    pwd_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(pwd_characters) for _ in range(pwd_length))


def url_exists(url):
    try:
        response = requests.head(url)
        return response.status_code < 400
    except requests.ConnectionError:
        return False


def _init_onprem_secret_store(secrets: Secrets) -> None:
    secrets.save(CKey.use_itde, 'yes')
    secrets.save(CKey.mem_size, '4')
    secrets.save(CKey.disk_size, '4')
    secrets.save(CKey.db_schema, 'NOTEBOOK_TESTS')


def _init_saas_secret_store(secrets: Secrets) -> None:
    secrets.save(CKey.storage_backend, StorageBackend.saas.name)
    secrets.save(CKey.saas_url, _env("SAAS_HOST"))
    secrets.save(CKey.saas_token, _env("SAAS_PAT"))
    secrets.save(CKey.saas_account_id, _env("SAAS_ACCOUNT_ID"))
    secrets.save(CKey.saas_database_name, timestamp_name('NBTEST'))
    secrets.save(CKey.db_schema, 'NOTEBOOK_TESTS_SAAS')


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
                 timeout: int = -1, hacks: Optional[List[Tuple[str, str]]] = None, ) -> None:
    """
    Executes notebook with added access to the configuration store.

    Parameters:
        notebook_file:  Notebook file.
        store_file:     Configuration store file.
        store_password: Configuration store password.
        timeout:        Optional timeout in seconds.
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


@contextmanager
def access_to_temp_onprem_secret_store(tmp_path: Path) -> Tuple[Path, str]:
    """
    Creates a temporary configuration store.
    Brings up and subsequently destroys the Exasol Docker-DB.
    Returns the temporary configuration store path and password.
    """

    # Create temporary secret store
    store_path = tmp_path / 'tmp_config.sqlite'
    # Should the password be constant or randomly generated is debatable.
    # Strictly speaking, random password makes a test non-deterministic.
    # On the other hand, it improves the security. If for some reason the
    # temporary configuration store is not deleted, there will be no access
    # to it since the password will be forgotten once the session is over.
    store_password = generate_password(12)
    secrets = Secrets(store_path, master_password=store_password)

    # Set the configuration required by the ITDE manager and those the
    # manager will not set after starting the Exasol Docker-DB.
    _init_onprem_secret_store(secrets)

    # Start the Exasol Docker-DB and then destroy it after the test finishes.
    bring_itde_up(secrets)
    try:
        yield store_path, store_password
    finally:
        take_itde_down(secrets)


@pytest.fixture(scope='session')
def access_to_temp_saas_secret_store(tmp_path_factory) -> Tuple[Path, str]:
    """
    Creates a temporary configuration store.
    Initiates the creation of a temporary SaaS database and waits till this database
    becomes operational.
    Saves the SaaS connection parameters in the configuration store.
    """

    store_path = tmp_path_factory.mktemp('tmp_config_dir') / 'tmp_config_saas.sqlite'
    # See access_to_temp_onprem_secret_store for considerations about the store password.
    store_password = generate_password(12)
    secrets = Secrets(store_path, master_password=store_password)

    _init_saas_secret_store(secrets)

    with ExitStack() as stack:
        client = stack.enter_context(create_saas_client(
            host=secrets.get(CKey.saas_url),
            pat=secrets.get(CKey.saas_token)))
        api_access = OpenApiAccess(
            client=client,
            account_id=secrets.get(CKey.saas_account_id))
        stack.enter_context(api_access.allowed_ip())
        db = stack.enter_context(api_access.database(
            name=secrets.get(CKey.saas_database_name),
            idle_time=timedelta(hours=12)))
        api_access.wait_until_running(db.id)
        yield store_path, store_password


@pytest.fixture
def access_to_temp_secret_store(request,
                                tmp_path: Path,
                                access_to_temp_saas_secret_store
                                ) -> Tuple[Path, str]:
    """
    Creates a temporary configuration store.
    Ensures that the database (either on-prem or SaaS, depending on the request parameter)
    is running for the duration of the fixture.
    """
    if request.param == StorageBackend.onprem:
        with access_to_temp_onprem_secret_store(tmp_path) as onprem_store:
            yield onprem_store
    elif request.param == StorageBackend.saas:
        yield access_to_temp_saas_secret_store
    else:
        raise ValueError(('Unrecognised testing backend in the access_to_temp_secret_store. '
                          'Should be either "onprem" or "saas"'))


@pytest.fixture
def notebook_runner(request,
                    tmp_path: Path,
                    access_to_temp_saas_secret_store
                    ) -> Callable:
    """
    A fixture for running a notebook.
    """
    if request.param == StorageBackend.onprem:
        with access_to_temp_onprem_secret_store(tmp_path) as onprem_store:
            store_path, store_password = onprem_store
            yield partial(run_notebook,
                          store_file=str(store_path),
                          store_password=store_password)
    elif request.param == StorageBackend.saas:
        store_path, store_password = access_to_temp_saas_secret_store
        yield partial(run_notebook,
                      store_file=str(store_path),
                      store_password=store_password)
    else:
        raise ValueError(('Unrecognised testing backend in the notebook_runner. '
                          'Should be either "onprem" or "saas"'))


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
