from pathlib import Path
from unittest.mock import MagicMock

from scripts.build.release_workflow import (
    ReleaseContext,
    load_context,
    run_build,
    run_check,
    run_notes,
    run_publish,
    write_workflow_env,
)


def test_load_context_manual(monkeypatch, tmp_path):
    monkeypatch.setenv("RELEASE_MODE", "workflow_dispatch")
    monkeypatch.setenv("RELEASE_TAG", "feature-branch")
    monkeypatch.setenv("RELEASE_TITLE", "Draft Release")
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    monkeypatch.setattr("scripts.build.release_workflow.get_poetry_version", lambda: "5.1.0")

    context = load_context()

    assert context.release_is_manual is True
    assert context.release_ref == "manual-123-2"
    assert context.release_version == "5.1.0"
    assert context.release_asset_id == "Draft Release"
    assert context.release_title_input == "Draft Release"


def test_write_workflow_env(monkeypatch, tmp_path):
    env_file = tmp_path / "github_env"
    monkeypatch.setenv("GITHUB_ENV", str(env_file))
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-central-1")
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

    write_workflow_env(context)

    content = env_file.read_text()
    assert "AWS_DEFAULT_REGION=eu-central-1" in content
    assert "RELEASE_IS_MANUAL=true" in content
    assert "RELEASE_REF=manual-123-2" in content
    assert "RELEASE_VERSION=5.1.0" in content
    assert "RELEASE_ASSET_ID=Draft Release" in content
    assert f"RELEASE_NOTES_DIR={tmp_path / 'release-notes'}" in content


def test_run_check_routes_by_mode(monkeypatch):
    calls = []
    monkeypatch.setattr("scripts.build.release_workflow.validate_release", lambda release_tag: calls.append(release_tag))
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

    assert calls == ["", "5.1.0"]


def test_run_build_uses_asset_id(monkeypatch):
    captured = {}
    monkeypatch.setattr("scripts.build.release_workflow.run_start_release_build", lambda config, publish, asset_id: captured.update(
        {"publish": publish, "asset_id": asset_id}
    ))
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

    run_build(context)

    assert captured == {"publish": True, "asset_id": "Draft Release"}


def test_run_notes_uses_manual_title(monkeypatch, tmp_path):
    captured = {}
    monkeypatch.setattr("scripts.build.release_workflow.write_release_notes", lambda release_ref, aws_access, output_dir, asset_id=None, release_title=None: captured.update(
        {
            "release_ref": release_ref,
            "asset_id": asset_id,
            "release_title": release_title,
            "output_dir": output_dir,
        }
    ))
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

    assert captured["release_ref"] == "5.1.0"
    assert captured["asset_id"] == "Draft Release"
    assert captured["release_title"] == "Draft Release"
    assert captured["output_dir"] == tmp_path / "release-notes"


def test_run_publish_manual_creates_draft_release(monkeypatch, tmp_path):
    release_dir = tmp_path / "release-notes"
    release_dir.mkdir()
    (release_dir / "release_title.txt").write_text("Draft Release\n")
    (release_dir / "release_notes.md").write_text("notes")
    (release_dir / "artifacts.md").write_text("artifacts")

    calls = []
    monkeypatch.setattr("scripts.build.release_workflow._release_exists", lambda release_ref: False)
    monkeypatch.setattr("scripts.build.release_workflow._run_gh", lambda args: calls.append(args))
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

    assert calls == [[
        "release",
        "create",
        "manual-123-2",
        "--draft",
        "--title",
        "Draft Release",
        "--notes-file",
        str(release_dir / "release_notes.md"),
        f"{release_dir / 'artifacts.md'}#artifacts.md",
    ]]


def test_run_publish_tag_updates_existing_release(monkeypatch, tmp_path):
    release_dir = tmp_path / "release-notes"
    release_dir.mkdir()
    (release_dir / "release_title.txt").write_text("5.1.0: Test Release\n")
    (release_dir / "release_notes.md").write_text("notes")
    (release_dir / "artifacts.md").write_text("artifacts")

    calls = []
    monkeypatch.setattr("scripts.build.release_workflow._release_exists", lambda release_ref: True)
    monkeypatch.setattr("scripts.build.release_workflow._run_gh", lambda args: calls.append(args))
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

    assert calls == [
        ["release", "edit", "5.1.0", "--title", "5.1.0: Test Release", "--notes-file", str(release_dir / "release_notes.md")],
        ["release", "upload", "5.1.0", f"{release_dir / 'artifacts.md'}#artifacts.md", "--clobber"],
    ]
