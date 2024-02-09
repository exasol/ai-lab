from typing import List, Tuple, Optional, Callable
from pathlib import Path
from functools import partial
import random
import string
import textwrap

import pytest
import nbformat
from nbclient import NotebookClient
import requests

from exasol.nb_connector.secret_store import Secrets
from exasol.nb_connector.ai_lab_config import AILabConfig as CKey
from exasol.nb_connector.itde_manager import (
    bring_itde_up,
    take_itde_down
)


def generate_password(pwd_length):
    pwd_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(pwd_characters) for _ in range(pwd_length))


def url_exists(url):
    try:
        response = requests.head(url)
        return response.status_code < 400
    except requests.ConnectionError:
        return False


def _init_secret_store(secrets: Secrets) -> None:
    secrets.save(CKey.use_itde, 'yes')
    secrets.save(CKey.mem_size, '4')
    secrets.save(CKey.disk_size, '4')
    secrets.save(CKey.db_schema, 'NOTEBOOK_TESTS')


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


@pytest.fixture
def access_to_temp_secret_store(tmp_path: Path) -> Tuple[Path, str]:
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
    _init_secret_store(secrets)

    # Start the Exasol Docker-DB and then destroy it after the test finishes.
    bring_itde_up(secrets)
    try:
        yield store_path, store_password
    finally:
        take_itde_down(secrets)


@pytest.fixture
def notebook_runner(access_to_temp_secret_store) -> Callable:
    """
    A fixture for running a notebook.
    """

    store_path, store_password = access_to_temp_secret_store
    return partial(run_notebook, store_file=str(store_path), store_password=store_password)


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
