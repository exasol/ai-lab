import os
import textwrap
import pytest

from notebook_test_utils import (
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
        'zero_shot_classification.ipynb'
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
