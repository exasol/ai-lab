from pathlib import Path
from unittest.mock import Mock

from scripts.build.check_release import main as check_release_cli
from scripts.build.generate_release_notes import main as generate_release_notes_cli
from scripts.build.release_workflow import main as release_workflow_cli
from test.unit.cli import CliRunner


def test_check_release_cli_invokes_validator(monkeypatch):
    validate_release = Mock()
    monkeypatch.setattr("scripts.build.check_release.validate_release", validate_release)

    cli = CliRunner(check_release_cli)
    cli.run("--release-tag", "refs/tags/v5.1.0")

    assert cli.succeeded
    validate_release.assert_called_once_with("refs/tags/v5.1.0")


def test_generate_release_notes_cli_invokes_writer(monkeypatch, tmp_path):
    write_release_notes = Mock()
    monkeypatch.setattr(
        "scripts.build.generate_release_notes.write_release_notes",
        write_release_notes,
    )

    cli = CliRunner(generate_release_notes_cli)
    cli.run(
        "--release-tag",
        "v5.1.0",
        "--output-dir",
        str(tmp_path / "release-notes"),
        "--asset-id",
        "release-assets",
        "--release-title",
        "Draft Release",
    )

    assert cli.succeeded
    write_release_notes.assert_called_once()
    args, kwargs = write_release_notes.call_args
    assert args[0] == "v5.1.0"
    assert args[2] == Path(tmp_path / "release-notes")
    assert kwargs == {"asset_id": "release-assets", "release_title": "Draft Release"}


def test_release_workflow_cli_routes_to_check(monkeypatch):
    run_check = Mock()
    monkeypatch.setattr("scripts.build.release_workflow.run_check", run_check)
    monkeypatch.setattr(
        "scripts.build.release_workflow.load_context",
        Mock(return_value=Mock()),
    )

    cli = CliRunner(release_workflow_cli)
    cli.run("check")

    assert cli.succeeded
    run_check.assert_called_once()
