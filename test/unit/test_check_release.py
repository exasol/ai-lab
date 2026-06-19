from exasol.ds.sandbox.lib import check_release


def test_get_change_log_version_reads_repo_root_changelog(tmp_path, monkeypatch):
    changelog_file = tmp_path / "changelog.md"
    changelog_file.write_text(
        "* [6.0.0](https://example.invalid)\n"
    )

    monkeypatch.setattr(check_release, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(check_release, "CHANGELOG_FILE", changelog_file)

    assert check_release.get_change_log_version() == "6.0.0"
