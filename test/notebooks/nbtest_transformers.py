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

running_hack = (
    'running_model',
    textwrap.dedent("""
        errors = %sql --with udf_output SELECT error_message FROM udf_output WHERE error_message != 'None'
        assert not errors, str(errors)
    """)
)

running_delete_hack = (
    'running_model_delete',
    textwrap.dedent("""
        df = model_delete.DataFrame()
        assert df.loc[0, 'success'], df.loc[0, 'success']
        assert not df.loc[0, 'error_message'], df.loc[0, 'error_message']
    """)
)

running_delete_error_hack = (
    'running_model_delete_error',
    textwrap.dedent("""
        df = model_delete_with_error.DataFrame()
        assert not df.loc[0, 'success'], df.loc[0, 'success']
        assert "No such file or directory:" in df.loc[0, 'error_message'], df.loc[0, 'error_message']
    """)
)

running_pyexasol_hack = (
    'running_model_pyexasol',
    'assert str(result["ERROR_MESSAGE"]) == "nan"'
)


@pytest.mark.parametrize(
    "notebook_file, hacks",
    [
        ('sequence_classification.ipynb',[running_hack, running_pyexasol_hack]),
        ('question_answering.ipynb',[running_hack, running_pyexasol_hack]),
        ('masked_modelling.ipynb',[running_hack, running_pyexasol_hack]),
        ('token_classification.ipynb',[running_hack, running_pyexasol_hack]),
        ('text_generation.ipynb',[running_hack, running_pyexasol_hack]),
        ('translation.ipynb',[running_hack, running_pyexasol_hack]),
        ('zero_shot_classification.ipynb',[running_hack, running_pyexasol_hack]),
        ("model_management.ipynb", [running_hack, running_delete_hack, running_pyexasol_hack, running_delete_error_hack])
    ]
)
def test_transformers(notebook_runner, uploading_hack, notebook_file, hacks) -> None:

    current_dir = os.getcwd()
    try:
        notebook_runner('main_config.ipynb')
        os.chdir('./transformers')
        notebook_runner(notebook_file='te_init.ipynb', hacks=[uploading_hack])
        notebook_runner(notebook_file=notebook_file,
                        hacks=hacks)
    finally:
        os.chdir(current_dir)
