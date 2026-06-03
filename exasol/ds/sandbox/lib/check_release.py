import re
import sys

from git import Repo
import toml

from exasol.ds.sandbox.lib.release_tag import release_version_from_tag
from exasol.ds.sandbox.lib.repo_paths import get_repo_root

REPO_ROOT = get_repo_root()
CHANGELOG_FILE = REPO_ROOT / "doc" / "changes" / "changelog.md"


def get_git_version() -> str:
    repo = Repo()
    assert not repo.bare
    tag_strings = sorted([t.name for t in repo.tags], reverse=True)
    tag_strings = [t for t in tag_strings if t != "latest"]

    if len(tag_strings) == 0:
        return ""
    latest_tag = tag_strings[0].strip()
    assert len(latest_tag) > 0
    return latest_tag


def get_poetry_version() -> str:
    parsed_toml = toml.load("pyproject.toml")
    return parsed_toml["project"]["version"].strip()


def get_change_log_version() -> str:
    with open(CHANGELOG_FILE) as changelog:
        changelog_str = changelog.read()
        version_match = re.search(r"\* \[([0-9]+.[0-9]+.[0-9]+)]\(\S+\)", changelog_str)
        if version_match is None:
            raise ValueError(f"Unable to find release version in {CHANGELOG_FILE}")
        return version_match.groups()[0]


def validate_release(release_tag: str = "") -> None:
    poetry_version = get_poetry_version()
    latest_tag = get_git_version()
    changelog_version = get_change_log_version()
    release_tag = release_version_from_tag(release_tag)
    print(f'Changelog version: "{changelog_version}"', file=sys.stderr)
    print(f'Current version: "{poetry_version}"', file=sys.stderr)
    print(f'Latest git tag: "{latest_tag}"', file=sys.stderr)
    if release_tag:
        print(f'Release tag: "{release_tag}"', file=sys.stderr)

    if release_tag:
        if release_tag != poetry_version:
            raise ValueError("Release tag differs from Poetry version!")
    else:
        if poetry_version == latest_tag:
            raise ValueError("Poetry version needs to be updated!")

    if changelog_version != poetry_version:
        raise ValueError("Poetry version differs from Changelog version!")

    print("Everything looks good", file=sys.stderr)
