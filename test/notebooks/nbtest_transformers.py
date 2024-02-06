import os
import textwrap
import pytest

from notebook_test_utils import (access_to_temp_secret_store, notebook_runner, uploading_hack)


@pytest.mark.parametrize(
    "notebook_file",
    [
        'sequence_classification.ipynb',
        pytest.param('question_answering.ipynb', marks=pytest.mark.skip('leaving just one test')),
        pytest.param('masked_modelling.ipynb', marks=pytest.mark.skip('leaving just one test')),
        pytest.param('token_classification.ipynb', marks=pytest.mark.skip('leaving just one test')),
        pytest.param('text_generation.ipynb', marks=pytest.mark.skip('leaving just one test')),
        pytest.param('translation.ipynb', marks=pytest.mark.skip('leaving just one test')),
        pytest.param('zero_shot_classification.ipynb', marks=pytest.mark.skip('leaving just one test'))
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
