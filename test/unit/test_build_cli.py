from unittest.mock import Mock

import exasol.ds.sandbox.cli.commands.release_workflow as release_workflow_module
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


def test_release_workflow_build_cli_sets_default_log_level_and_invokes_builder(monkeypatch):
    # The release_workflow package exports a Click group with the same name as the module,
    # so we patch the actual imported module object here.
    set_log_level = Mock()
    run_build = Mock()
    monkeypatch.setattr(release_workflow_module, "set_log_level", set_log_level)
    monkeypatch.setattr(release_workflow_module.release_workflow_lib, "run_build", run_build)
    monkeypatch.setattr(
        release_workflow_module.release_workflow_lib,
        "load_context",
        Mock(return_value=Mock()),
    )

    cli = CliRunner(release_workflow_cli)
    cli.run("build")

    assert cli.succeeded
    set_log_level.assert_called_once_with("info")
    run_build.assert_called_once()
