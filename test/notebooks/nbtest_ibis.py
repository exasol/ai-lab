import os
import textwrap
import pytest

from exasol.nb_connector.ai_lab_config import StorageBackend
from notebook_test_utils import (
    access_to_temp_secret_store,
    access_to_temp_saas_secret_store,
    notebook_runner,
    set_log_level_for_libraries,
)


set_log_level_for_libraries()


@pytest.mark.parametrize('notebook_runner', [StorageBackend.onprem, StorageBackend.saas], indirect=True)
def test_quickstart(notebook_runner) -> None:

    data_import_hack = (
        'data_selection',
        textwrap.dedent("""
            load_flights_data(ai_lab_config, ['Jan 2024'])
            load_airlines_data(ai_lab_config)
        """)
    )

    current_dir = os.getcwd()
    try:
        notebook_runner('main_config.ipynb')
        os.chdir('./data')
        notebook_runner('data_flights.ipynb', hacks=[data_import_hack])
        os.chdir('../ibis')
        notebook_runner('quickstart.ipynb')
    finally:
        os.chdir(current_dir)
