import os
import textwrap
import pytest

# We need to manually import all fixtures that we use, directly or indirectly,
# since the pytest won't do this for us.
from notebook_test_utils import (
    backend_setup,
    notebook_runner,
    uploading_hack,
    set_log_level_for_libraries,
)


set_log_level_for_libraries()


@pytest.mark.parametrize(
    "notebook_file",
    [
        'sequence_classification.ipynb',
        'question_answering.ipynb',
        'masked_modelling.ipynb',
        'token_classification.ipynb',
        'text_generation.ipynb',
        'translation.ipynb',
        'zero_shot_classification.ipynb',

    ]
)
def test_transformers(notebook_runner, uploading_hack, notebook_file) -> None:

    running_hack = (
        'running_model',
        textwrap.dedent("""
            errors = %sql --with udf_output SELECT error_message FROM udf_output WHERE error_message != 'None'
            assert not errors, str(errors)
        """)
    )
    running_pyexasol_hack = (
        'running_model_pyexasol',
        'assert str(result["ERROR_MESSAGE"]) == "nan"'
    )

    current_dir = os.getcwd()
    try:
        notebook_runner('main_config.ipynb')
        os.chdir('./transformers')
        notebook_runner(notebook_file='te_init.ipynb', hacks=[uploading_hack])
        notebook_runner(notebook_file=notebook_file,
                        hacks=[uploading_hack, running_hack, running_pyexasol_hack])
    finally:
        os.chdir(current_dir)

def test_model_mgmt(notebook_runner, uploading_hack) -> None:
    notebook_file = "model_administration.ipynb"

    running_hack = (
        'running_model',
        textwrap.dedent("""
            errors = %sql --with udf_output SELECT error_message FROM udf_output WHERE error_message != 'None'
            assert not errors, str(errors)
        """)
    )
    running_error_hack = (
        'running_model_error',
        textwrap.dedent("""
            errors = %sql --with udf_output_error SELECT error_message FROM udf_output_error WHERE error_message != 'None'
            assert len(errors) == 1
            assert "No such file or directory:" in str(errors[0])
        """)
    )
    running_pyexasol_hack = (
        'running_model_pyexasol',
        'assert str(result["ERROR_MESSAGE"]) == "nan"'
    )

    current_dir = os.getcwd()
    try:
        notebook_runner('main_config.ipynb')
        os.chdir('./transformers')
        notebook_runner(notebook_file='te_init.ipynb', hacks=[uploading_hack])
        notebook_runner(notebook_file=notebook_file,
                        hacks=[uploading_hack, running_hack, running_error_hack, running_pyexasol_hack])
    finally:
        os.chdir(current_dir)
