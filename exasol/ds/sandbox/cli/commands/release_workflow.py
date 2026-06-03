from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.lib import release_workflow as release_workflow_lib
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.logging import set_log_level


@cli.group(name="release")
def release() -> None:
    """Release workflow commands."""


@release.command()
def check() -> None:
    context = release_workflow_lib.load_context()
    release_workflow_lib.run_check(context)


@release.command()
def build() -> None:
    # Release builds are long-running; surface progress by default.
    set_log_level("info")
    context = release_workflow_lib.load_context()
    release_workflow_lib.run_build(context, AwsAccess(None))


@release.command()
def notes() -> None:
    context = release_workflow_lib.load_context()
    release_workflow_lib.run_notes(context)


@release.command()
def publish() -> None:
    context = release_workflow_lib.load_context()
    release_workflow_lib.run_publish(context)


main = release


if __name__ == "__main__":
    main()
