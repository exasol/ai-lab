from exasol.ds.sandbox.lib.repo_paths import get_repo_root


def test_get_repo_root_returns_project_root():
    repo_root = get_repo_root()

    assert (repo_root / "pyproject.toml").exists()
    assert (repo_root / "doc" / "changes" / "changelog.md").exists()
