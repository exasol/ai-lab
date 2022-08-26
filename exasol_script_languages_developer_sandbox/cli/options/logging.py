import click

from exasol_script_languages_developer_sandbox.lib.logging import SUPPORTED_LOG_LEVELS

logging_options = [
    click.option('--log-level', type=click.Choice(list(SUPPORTED_LOG_LEVELS.keys())), default="normal",
                 show_default=True,
                 help="Level of information printed out. "
                      "'Normal' prints only necessary information. "
                      "'Info' prints also internal status info. 'Debug' prints detailed information."),
]
