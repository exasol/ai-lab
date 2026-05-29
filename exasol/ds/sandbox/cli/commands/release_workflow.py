from exasol.ds.sandbox.cli.cli import cli
from exasol.ds.sandbox.lib import release_workflow as release_workflow_lib


@cli.group(name="release-workflow")
def release_workflow() -> None:
    """Release workflow commands."""


@release_workflow.command()
def check() -> None:
    context = release_workflow_lib.load_context()
    release_workflow_lib.run_check(context)


@release_workflow.command()
def build() -> None:
    context = release_workflow_lib.load_context()
    release_workflow_lib.run_build(context)


@release_workflow.command()
def notes() -> None:
    context = release_workflow_lib.load_context()
    release_workflow_lib.run_notes(context)


@release_workflow.command()
def publish() -> None:
    context = release_workflow_lib.load_context()
    release_workflow_lib.run_publish(context)


main = release_workflow


if __name__ == "__main__":
    main()
