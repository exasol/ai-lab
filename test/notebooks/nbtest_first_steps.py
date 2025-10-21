# We need to manually import all fixtures that we use, directly or indirectly,
# since the pytest won't do this for us.
from notebook_test_utils import (
    backend_setup,
    notebook_runner,
    set_log_level_for_libraries,
)

set_log_level_for_libraries()


def test_first_steps_notebook(notebook_runner) -> None:
    notebook_runner('main_config.ipynb')
    notebook_runner('first_steps.ipynb')
