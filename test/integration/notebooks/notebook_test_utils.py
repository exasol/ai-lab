from typing import Optional, List, Set, Tuple, Callable
from pathlib import Path
from itertools import chain
from functools import partial
import re
import random
import string

import pytest
import nbformat
from nbclient import NotebookClient
import requests

from exasol.secret_store import Secrets
from exasol.ai_lab_config import AILabConfig as CKey
from exasol.itde_manager import (
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


def run_notebook(notebook_file: str, store_file: str, store_password: str, timeout: int = -1) -> None:
    """
    Executes notebook with added access to the configuration store.

    Parameters:
        notebook_file:  Notebook file.
        store_file:     Configuration store file.
        store_password: Configuration store password.
        timeout:        Optional timeout in seconds.
    """

    # This code will be inserted at the beginning of the notebook
    init_code = f'''
    def init_notebook_test():
        from pathlib import Path
        from exasol.secret_store import Secrets
        global sb_config
        sb_config = Secrets(Path("{store_file}"), "{store_password}")
    init_notebook_test()
    '''

    # Read the notebook and insert a new cell with the above code into it.
    nb = nbformat.read(notebook_file, as_version=4)
    nb["cells"] = [nbformat.v4.new_code_cell(init_code)] + nb["cells"]

    # Execute the notebook object, expecting to get no exceptions.
    nb_client = NotebookClient(nb, timeout=timeout, kernel_name='python3')
    nb_client.execute()


@pytest.fixture
def access_to_temp_secret_store(tmp_path: Path) -> Tuple[Path, str]:
    """
    Creates a temporary configuration store.
    Brings up and subsequently destroys the Docker-DB.
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
    # manager will not set after starting the Docker-DB.
    _init_secret_store(secrets)

    # Start the Docker-DB and then destroy it after the test finishes.
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


def verify_links_for_notebook(nb_file: Path,
                              checked_urls: Optional[Set[str]] = None) -> List[Tuple[str, str]]:
    """
    Verifies all links in the specified notebook.
    Returns a list of invalid links[(nodebook name, link), (...)]

    Parameters:
        nb_file:        Notebook path
        checked_urls:   A set of already checked URLs.
    """

    nb = nbformat.read(str(nb_file), as_version=4)

    link_pattern = re.compile(r'\[.+?\]\((.+?)\)')
    hyperlink_pattern = re.compile(r'<a\s.*?href="(.+?)".*?>.*?</a>')
    invalid_links: List[Tuple[str, str]] = []
    if checked_urls is None:
        checked_urls = set()

    # Loop over all markdown cells in the notebook
    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            # Find all links or hyperlinks
            for match in chain(link_pattern.finditer(cell.source),
                               hyperlink_pattern.finditer(cell.source)):
                address = match.group(1)
                address_lo = address.lower()
                link_is_valid = True
                if address_lo.startswith('http://') or address_lo.startswith('https://'):
                    # Check that the URL is accessible.
                    # Skip those that have already been checked.
                    if address not in checked_urls:
                        link_is_valid = url_exists(address)
                        checked_urls.add(address)
                else:
                    # Check that the referenced file exists.
                    address_path = nb_file.parent / address
                    link_is_valid = address_path.exists()
                if not link_is_valid:
                    invalid_links.append((nb_file.name, match.group(0)))

    return invalid_links


def verify_links_for_directory(nb_dir: Path = Path('.'), include_subdir: bool = True,
                               checked_urls: Optional[Set[str]] = None) -> List[Tuple[str, str]]:
    """
    Verifies links in all notebooks in the specified directory.
    Returns a list of invalid links[(nodebook name, link), (...)]

    Parameters:
        nb_dir:         Directory path.
        include_subdir: Include notebooks in all subdirectories at any depth.
        checked_urls:   A set of already checked URLs.
    """

    invalid_links: List[Tuple[str, str]] = []
    if checked_urls is None:
        checked_urls = set()

    for child_obj in nb_dir.iterdir():
        if child_obj.is_dir():
            if include_subdir:
                invalid_links.extend(verify_links_for_directory(child_obj, include_subdir,
                                                                checked_urls))
        elif child_obj.match('*.ipynb') and not child_obj.match('*-checkpoint.ipynb'):
            invalid_links.extend(verify_links_for_notebook(child_obj, checked_urls))

    return invalid_links
