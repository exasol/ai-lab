import os
from pathlib import Path

from exasol.nb_connector.secret_store import Secrets
from exasol.nb_connector.ai_lab_config import AILabConfig as CKey

# We need to manually import all fixtures that we use, directly or indirectly,
# since the pytest won't do this for us.
from notebook_test_utils import (
    backend_setup,
    notebook_runner,
    uploading_hack,
    set_log_level_for_libraries,
)

set_log_level_for_libraries()


def _store_pre_release_access(store_path: Path, store_password: str) -> None:

    conf = Secrets(store_path, store_password)
    conf.connection()
    conf.save(CKey.text_ai_pre_release_url, os.environ["NBTEST_ZIP_URL"])
    conf.save(CKey.text_ai_zip_password, os.environ["NBTEST_ZIP_PASSWORD"])


def test_text_ai(notebook_runner, uploading_hack) -> None:

    store_path, store_password = backend_setup
    _store_pre_release_access(store_path, store_password)

    current_dir = os.getcwd()
    try:
        notebook_runner('main_config.ipynb')
        os.chdir('./text_ai')
        notebook_runner(notebook_file='txaie_init.ipynb', hacks=[uploading_hack])
    finally:
        os.chdir(current_dir)
