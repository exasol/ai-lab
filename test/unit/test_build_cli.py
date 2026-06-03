from unittest.mock import Mock

import exasol.ds.sandbox.cli.commands.release_workflow as release_workflow_module
from exasol.ds.sandbox.cli.commands.release_workflow import release as release_cli
from test.unit.cli import CliRunner


def test_release_workflow_check_cli_invokes_validator(monkeypatch):
    run_check = Mock()
    monkeypatch.setattr("exasol.ds.sandbox.lib.release_workflow.run_check", run_check)
    monkeypatch.setattr(
        "exasol.ds.sandbox.lib.release_workflow.load_context",
        Mock(return_value=Mock()),
    )

    cli = CliRunner(release_cli)
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

    cli = CliRunner(release_cli)
    cli.run("notes")

    assert cli.succeeded
    run_notes.assert_called_once()


def test_release_workflow_build_cli_sets_default_log_level_and_invokes_builder(monkeypatch):
    set_log_level = Mock()
    run_build = Mock()
    monkeypatch.setattr(release_workflow_module, "set_log_level", set_log_level)
    monkeypatch.setattr("exasol.ds.sandbox.lib.release_workflow.run_build", run_build)
    monkeypatch.setattr(
        "exasol.ds.sandbox.lib.release_workflow.load_context",
        Mock(return_value=Mock()),
    )

    cli = CliRunner(release_cli)
    cli.run("build")

    assert cli.succeeded
    set_log_level.assert_called_once_with("info")
    run_build.assert_called_once()
