import click
import os


@click.group()
def cli():
    pass


def option_with_env_default(envvar: str, *args, **kwargs):
    kwargs["help"] = f"{kwargs['help']} [defaults to environment variable '{envvar}']"
    return click.option(
        *args, **kwargs,
        default=lambda: os.environ.get(envvar, ""),
    )
