from unittest.mock import Mock

from exasol.ds.sandbox.cli.commands.release_workflow import main as release_workflow_cli
from test.unit.cli import CliRunner


def test_release_workflow_check_cli_invokes_validator(monkeypatch):
    run_check = Mock()
    monkeypatch.setattr("exasol.ds.sandbox.lib.release_workflow.run_check", run_check)
    monkeypatch.setattr(
        "exasol.ds.sandbox.lib.release_workflow.load_context",
        Mock(return_value=Mock()),
    )

    cli = CliRunner(release_workflow_cli)
    cli.run("check")

    assert cli.succeeded
    run_check.assert_called_once()


def test_release_workflow_notes_cli_invokes_writer(monkeypatch):
    run_notes = Mock()
    monkeypatch.setattr("exasol.ds.sandbox.lib.release_workflow.run_notes", run_notes)
    monkeypatch.setattr(
        "exasol.ds.sandbox.lib.release_workflow.load_context",
        Mock(return_value=Mock()),
    )

    cli = CliRunner(release_workflow_cli)
    cli.run("notes")

    assert cli.succeeded
    run_notes.assert_called_once()
