from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.asset_printing.print_assets import (
    AssetTypes,
    print_assets,
)
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.render_template import render_template

REPO_ROOT = Path(__file__).resolve().parents[4]
CHANGELOG_DIR = REPO_ROOT / "doc" / "changes"


@dataclass(frozen=True)
class ReleaseNotes:
    title: str
    notes: str
    artifacts: str


def _release_version(release_tag: str) -> str:
    return release_tag.removeprefix("refs/tags/").removeprefix("v")


def _changes_file(version: str) -> Path:
    return CHANGELOG_DIR / f"changes_{version}.md"


def _read_changes(version: str) -> str:
    path = _changes_file(version)
    if not path.exists():
        raise FileNotFoundError(f"Release notes file not found: {path}")
    return path.read_text()


def _split_changelog(version: str, changelog: str) -> tuple[str, str]:
    lines = changelog.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError(f"Could not parse release notes file {_changes_file(version)}")

    line_index = 1
    if line_index < len(lines) and lines[line_index] == "":
        line_index += 1

    if line_index >= len(lines) or not lines[line_index].startswith("Code name:"):
        raise ValueError(f"Could not parse release notes file {_changes_file(version)}")

    code_name = lines[line_index].split("Code name:", 1)[1].strip()
    line_index += 1
    while line_index < len(lines) and lines[line_index] == "":
        line_index += 1

    return code_name, "\n".join(lines[line_index:]).strip()


def _release_artifacts(version: str, aws_access: AwsAccess) -> str:
    buffer = StringIO()
    print_assets(
        aws_access=aws_access,
        asset_id=AssetId(version),
        out_file_obj=buffer,
        asset_types=(AssetTypes.DOCKER, AssetTypes.AMI, AssetTypes.VM_S3),
    )
    return buffer.getvalue().strip()


def build_release_notes(release_tag: str, aws_access: AwsAccess) -> ReleaseNotes:
    version = _release_version(release_tag)
    changelog = _read_changes(version).strip()
    code_name, changelog_body = _split_changelog(version, changelog)
    title = f"{version}: {code_name}"
    additional_notes = render_template("additional_release_notes.jinja").strip()
    artifacts = _release_artifacts(version, aws_access)

    notes_parts = [changelog_body, additional_notes]
    if artifacts:
        notes_parts.append(artifacts)

    notes = "\n\n".join(notes_parts).rstrip() + "\n"
    artifacts_text = artifacts.rstrip() + ("\n" if artifacts else "")
    return ReleaseNotes(title=title, notes=notes, artifacts=artifacts_text)


def write_release_notes(release_tag: str, aws_access: AwsAccess, output_dir: Path) -> ReleaseNotes:
    output_dir.mkdir(parents=True, exist_ok=True)
    release_notes = build_release_notes(release_tag, aws_access)
    (output_dir / "release_title.txt").write_text(f"{release_notes.title}\n")
    (output_dir / "release_notes.md").write_text(release_notes.notes)
    (output_dir / "artifacts.md").write_text(release_notes.artifacts)
    return release_notes
