import pytest
from unittest.mock import MagicMock

from exasol.ds.sandbox.lib.release_notes import build_release_notes, write_release_notes


def test_build_release_notes(tmp_path, monkeypatch):
    repo_root = tmp_path
    changes_dir = repo_root / "doc" / "changes"
    changes_dir.mkdir(parents=True)
    (changes_dir / "changes_1.2.3.md").write_text(
        "# AI-Lab 1.2.3 released 2026-01-01\n"
        "Code name: Test Release\n"
        "\n"
        "## Summary\n"
        "\n"
        "This is the summary.\n"
    )

    monkeypatch.setattr("exasol.ds.sandbox.lib.release_notes.REPO_ROOT", repo_root)
    monkeypatch.setattr("exasol.ds.sandbox.lib.release_notes.CHANGELOG_DIR", changes_dir)
    monkeypatch.setattr(
        "exasol.ds.sandbox.lib.release_notes.render_template",
        lambda template: "### AMI Region availability\n\nRegion text.",
    )

    def fake_print_assets(**kwargs):
        kwargs["out_file_obj"].write("#### Docker Images\n\n```shell\nexample/image:1.2.3\n```\n")

    monkeypatch.setattr("exasol.ds.sandbox.lib.release_notes.print_assets", fake_print_assets)

    notes = build_release_notes("refs/tags/1.2.3", MagicMock())

    assert notes.title == "1.2.3: Test Release"
    assert notes.notes.startswith("## Summary")
    assert "# AI-Lab 1.2.3 released 2026-01-01" not in notes.notes
    assert "Code name: Test Release" not in notes.notes
    assert "This is the summary." in notes.notes
    assert "AMI Region availability" in notes.notes
    assert "Docker Images" in notes.notes
    assert "example/image:1.2.3" in notes.artifacts


def test_write_release_notes(tmp_path, monkeypatch):
    changes_dir = tmp_path / "doc" / "changes"
    changes_dir.mkdir(parents=True)
    (changes_dir / "changes_1.2.3.md").write_text(
        "# AI-Lab 1.2.3 released 2026-01-01\n"
        "Code name: Test Release\n"
        "\n"
        "## Summary\n"
        "\n"
        "This is the summary.\n"
    )

    monkeypatch.setattr("exasol.ds.sandbox.lib.release_notes.REPO_ROOT", tmp_path)
    monkeypatch.setattr("exasol.ds.sandbox.lib.release_notes.CHANGELOG_DIR", changes_dir)
    monkeypatch.setattr(
        "exasol.ds.sandbox.lib.release_notes.render_template",
        lambda template: "### AMI Region availability\n\nRegion text.",
    )

    def fake_print_assets(**kwargs):
        kwargs["out_file_obj"].write("#### Docker Images\n\n```shell\nexample/image:1.2.3\n```\n")

    monkeypatch.setattr("exasol.ds.sandbox.lib.release_notes.print_assets", fake_print_assets)

    release_notes = write_release_notes("1.2.3", MagicMock(), tmp_path / "release")

    assert (tmp_path / "release" / "release_title.txt").read_text() == "1.2.3: Test Release\n"
    assert (tmp_path / "release" / "release_notes.md").read_text() == release_notes.notes
    assert (tmp_path / "release" / "artifacts.md").read_text() == release_notes.artifacts


def test_build_release_notes_rejects_v_prefixed_tag(tmp_path, monkeypatch):
    repo_root = tmp_path
    changes_dir = repo_root / "doc" / "changes"
    changes_dir.mkdir(parents=True)
    (changes_dir / "changes_1.2.3.md").write_text(
        "# AI-Lab 1.2.3 released 2026-01-01\n"
        "Code name: Test Release\n"
        "\n"
        "## Summary\n"
        "\n"
        "This is the summary.\n"
    )

    monkeypatch.setattr("exasol.ds.sandbox.lib.release_notes.REPO_ROOT", repo_root)
    monkeypatch.setattr("exasol.ds.sandbox.lib.release_notes.CHANGELOG_DIR", changes_dir)
    monkeypatch.setattr(
        "exasol.ds.sandbox.lib.release_notes.render_template",
        lambda template: "### AMI Region availability\n\nRegion text.",
    )
    monkeypatch.setattr(
        "exasol.ds.sandbox.lib.release_notes.print_assets",
        lambda **kwargs: None,
    )

    with pytest.raises(ValueError, match="bare versions without a leading 'v'"):
        build_release_notes("v1.2.3", MagicMock())


def test_build_release_notes_reports_missing_code_name(tmp_path, monkeypatch):
    repo_root = tmp_path
    changes_dir = repo_root / "doc" / "changes"
    changes_dir.mkdir(parents=True)
    (changes_dir / "changes_1.2.3.md").write_text(
        "# AI-Lab 1.2.3 released 2026-01-01\n"
        "\n"
        "## Summary\n"
    )

    monkeypatch.setattr("exasol.ds.sandbox.lib.release_notes.REPO_ROOT", repo_root)
    monkeypatch.setattr("exasol.ds.sandbox.lib.release_notes.CHANGELOG_DIR", changes_dir)
    monkeypatch.setattr(
        "exasol.ds.sandbox.lib.release_notes.render_template",
        lambda template: "### AMI Region availability\n\nRegion text.",
    )
    monkeypatch.setattr(
        "exasol.ds.sandbox.lib.release_notes.print_assets",
        lambda **kwargs: None,
    )

    with pytest.raises(ValueError, match="unable to detect code name"):
        build_release_notes("1.2.3", MagicMock())


def test_build_release_notes_with_manual_title_and_asset_id(tmp_path, monkeypatch):
    repo_root = tmp_path
    changes_dir = repo_root / "doc" / "changes"
    changes_dir.mkdir(parents=True)
    (changes_dir / "changes_1.2.3.md").write_text(
        "# AI-Lab 1.2.3 released 2026-01-01\n"
        "Code name: Test Release\n"
        "\n"
        "## Summary\n"
        "\n"
        "This is the summary.\n"
    )

    monkeypatch.setattr("exasol.ds.sandbox.lib.release_notes.REPO_ROOT", repo_root)
    monkeypatch.setattr("exasol.ds.sandbox.lib.release_notes.CHANGELOG_DIR", changes_dir)
    monkeypatch.setattr(
        "exasol.ds.sandbox.lib.release_notes.render_template",
        lambda template: "### AMI Region availability\n\nRegion text.",
    )

    observed_assets = {}

    def fake_print_assets(**kwargs):
        observed_assets["asset_id"] = kwargs["asset_id"].tag_value
        kwargs["out_file_obj"].write("#### Docker Images\n\n```shell\nexample/image:draft\n```\n")

    monkeypatch.setattr("exasol.ds.sandbox.lib.release_notes.print_assets", fake_print_assets)

    notes = build_release_notes(
        "1.2.3",
        MagicMock(),
        asset_id="draft-release",
        release_title="Draft Release",
    )

    assert notes.title == "Draft Release"
    assert observed_assets["asset_id"] == "draft-release"
    assert "example/image:draft" in notes.artifacts
