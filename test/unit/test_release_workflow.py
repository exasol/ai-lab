import pytest
from pathlib import Path
from unittest.mock import Mock, call

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.release_workflow import (
    ReleaseContext,
    load_context,
    run_build,
    run_check,
    run_notes,
    run_publish,
)
from exasol.ds.sandbox.lib.config import default_config_object


def test_load_context_manual(monkeypatch, tmp_path):
    monkeypatch.setenv("RELEASE_MODE", "workflow_dispatch")
    monkeypatch.setenv("RELEASE_TAG", "feature-branch")
    monkeypatch.setenv("RELEASE_TITLE", "Draft Release")
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    monkeypatch.setattr(
        "exasol.ds.sandbox.lib.release_workflow.get_poetry_version",
        Mock(return_value="5.1.0"),
    )

    context = load_context()

    assert context.release_is_manual is True
    assert context.release_ref == "manual-123-2"
    assert context.release_version == "5.1.0"
    assert context.release_asset_id == "Draft Release"
    assert context.release_title_input == "Draft Release"


def test_load_context_rejects_v_prefixed_tag(monkeypatch):
    monkeypatch.setenv("RELEASE_MODE", "push")
    monkeypatch.setenv("RELEASE_TAG", "v5.1.0")
    monkeypatch.setenv("GITHUB_REF_NAME", "v5.1.0")

    with pytest.raises(ValueError, match="bare versions without a leading 'v'"):
        load_context()


def test_run_check_routes_by_mode(monkeypatch):
    validate_release = Mock()
    monkeypatch.setattr("exasol.ds.sandbox.lib.release_workflow.validate_release", validate_release)
    manual_context = ReleaseContext(
        mode="workflow_dispatch",
        release_tag="feature-branch",
        release_version="5.1.0",
        release_ref="manual-123-2",
        release_title_input="Draft Release",
        release_asset_id="Draft Release",
        release_is_manual=True,
        release_notes_dir=Path("/tmp/release-notes"),
    )
    tag_context = ReleaseContext(
        mode="push",
        release_tag="5.1.0",
        release_version="5.1.0",
        release_ref="5.1.0",
        release_title_input="",
        release_asset_id="5.1.0",
        release_is_manual=False,
        release_notes_dir=Path("/tmp/release-notes"),
    )

    run_check(manual_context)
    run_check(tag_context)

    assert validate_release.call_args_list == [call(""), call("5.1.0")]


def test_run_build_uses_asset_id(monkeypatch):
    run_start_release_build = Mock()
    monkeypatch.setattr(
        "exasol.ds.sandbox.lib.release_workflow.run_start_release_build",
        run_start_release_build,
    )
    context = ReleaseContext(
        mode="workflow_dispatch",
        release_tag="feature-branch",
        release_version="5.1.0",
        release_ref="manual-123-2",
        release_title_input="Draft Release",
        release_asset_id="Draft Release",
        release_is_manual=True,
        release_notes_dir=Path("/tmp/release-notes"),
    )
    aws_access = AwsAccess(None)

    run_build(context, aws_access)

    run_start_release_build.assert_called_once()
    args, kwargs = run_start_release_build.call_args
    assert args == (default_config_object,)
    assert kwargs["aws_access"] is aws_access
    assert kwargs["publish"] is True
    assert kwargs["asset_id"] == "Draft Release"


def test_run_notes_uses_manual_title(monkeypatch, tmp_path):
    write_release_notes = Mock()
    monkeypatch.setattr(
        "exasol.ds.sandbox.lib.release_workflow.write_release_notes",
        write_release_notes,
    )
    context = ReleaseContext(
        mode="workflow_dispatch",
        release_tag="feature-branch",
        release_version="5.1.0",
        release_ref="manual-123-2",
        release_title_input="Draft Release",
        release_asset_id="Draft Release",
        release_is_manual=True,
        release_notes_dir=tmp_path / "release-notes",
    )

    run_notes(context)

    write_release_notes.assert_called_once()
    args, kwargs = write_release_notes.call_args
    assert args[0] == "5.1.0"
    assert args[2] == tmp_path / "release-notes"
    assert kwargs == {"asset_id": "Draft Release", "release_title": "Draft Release"}


def test_run_publish_manual_creates_draft_release(monkeypatch, tmp_path):
    release_dir = tmp_path / "release-notes"
    release_dir.mkdir()
    (release_dir / "release_title.txt").write_text("Draft Release\n")
    (release_dir / "release_notes.md").write_text("notes")
    (release_dir / "artifacts.md").write_text("artifacts")

    run_gh = Mock()
    monkeypatch.setattr("exasol.ds.sandbox.lib.release_workflow._run_gh", run_gh)
    context = ReleaseContext(
        mode="workflow_dispatch",
        release_tag="feature-branch",
        release_version="5.1.0",
        release_ref="manual-123-2",
        release_title_input="Draft Release",
        release_asset_id="Draft Release",
        release_is_manual=True,
        release_notes_dir=release_dir,
    )

    run_publish(context)

    run_gh.assert_called_once_with([
        "release",
        "create",
        "manual-123-2",
        "--draft",
        "--title",
        "Draft Release",
        "--notes-file",
        str(release_dir / "release_notes.md"),
        f"{release_dir / 'artifacts.md'}#artifacts.md",
    ])


def test_run_publish_tag_creates_release(monkeypatch, tmp_path):
    release_dir = tmp_path / "release-notes"
    release_dir.mkdir()
    (release_dir / "release_title.txt").write_text("5.1.0: Test Release\n")
    (release_dir / "release_notes.md").write_text("notes")
    (release_dir / "artifacts.md").write_text("artifacts")

    run_gh = Mock()
    monkeypatch.setattr("exasol.ds.sandbox.lib.release_workflow._run_gh", run_gh)
    context = ReleaseContext(
        mode="push",
        release_tag="5.1.0",
        release_version="5.1.0",
        release_ref="5.1.0",
        release_title_input="",
        release_asset_id="5.1.0",
        release_is_manual=False,
        release_notes_dir=release_dir,
    )

    run_publish(context)

    run_gh.assert_called_once_with([
        "release",
        "create",
        "5.1.0",
        "--title",
        "5.1.0: Test Release",
        "--notes-file",
        str(release_dir / "release_notes.md"),
        f"{release_dir / 'artifacts.md'}#artifacts.md",
    ])
