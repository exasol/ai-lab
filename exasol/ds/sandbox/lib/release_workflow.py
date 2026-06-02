import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.check_release import get_poetry_version, validate_release
from exasol.ds.sandbox.lib.config import default_config_object
from exasol.ds.sandbox.lib.release_build.run_release_build import run_start_release_build
from exasol.ds.sandbox.lib.release_notes import write_release_notes
from exasol.ds.sandbox.lib.release_tag import release_version_from_tag


@dataclass(frozen=True)
class ReleaseContext:
    mode: str
    release_tag: str
    release_version: str
    release_ref: str
    release_title_input: str
    release_asset_id: str
    release_is_manual: bool
    release_notes_dir: Path


def _workflow_env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def _is_manual(mode: str) -> bool:
    return mode == "workflow_dispatch"


def _release_version_from_tag(release_tag: str) -> str:
    return release_version_from_tag(release_tag)


def load_context() -> ReleaseContext:
    mode = _workflow_env("RELEASE_MODE", _workflow_env("GITHUB_EVENT_NAME"))
    release_tag = _workflow_env("RELEASE_TAG", _workflow_env("GITHUB_REF_NAME"))
    release_title_input = _workflow_env("RELEASE_TITLE")
    release_is_manual = _is_manual(mode)
    if release_is_manual:
        if not release_title_input:
            raise RuntimeError("RELEASE_TITLE must be set for manual release runs")
        release_ref = f"manual-{_workflow_env('GITHUB_RUN_ID')}-{_workflow_env('GITHUB_RUN_ATTEMPT', '1')}"
        release_version = get_poetry_version()
        release_asset_id = release_title_input
    else:
        release_ref = release_tag
        release_version = _release_version_from_tag(release_tag)
        release_asset_id = release_version
    release_notes_dir = Path(
        _workflow_env(
            "RELEASE_NOTES_DIR",
            str(Path(_workflow_env("RUNNER_TEMP", "/tmp")) / "release-notes"),
        )
    )
    return ReleaseContext(
        mode=mode,
        release_tag=release_tag,
        release_version=release_version,
        release_ref=release_ref,
        release_title_input=release_title_input,
        release_asset_id=release_asset_id,
        release_is_manual=release_is_manual,
        release_notes_dir=release_notes_dir,
    )


def run_check(context: ReleaseContext) -> None:
    if context.release_is_manual:
        validate_release("")
    else:
        validate_release(context.release_tag)


def run_build(context: ReleaseContext, aws_access: AwsAccess) -> None:
    run_start_release_build(
        default_config_object,
        aws_access=aws_access,
        publish=not context.release_is_manual,
        asset_id=context.release_asset_id,
    )


def run_notes(context: ReleaseContext) -> None:
    write_release_notes(
        context.release_version,
        AwsAccess(None),
        context.release_notes_dir,
        asset_id=context.release_asset_id,
        release_title=context.release_title_input if context.release_is_manual else None,
    )


def _run_gh(args: list[str]) -> None:
    subprocess.run(["gh", *args], check=True)


def run_publish(context: ReleaseContext) -> None:
    release_dir = context.release_notes_dir
    release_title = (release_dir / "release_title.txt").read_text().strip()
    release_notes = str(release_dir / "release_notes.md")
    artifacts_file = str(release_dir / "artifacts.md")
    gh_args = [
        "release",
        "create",
        context.release_ref,
    ]
    if context.release_is_manual:
        gh_args.append("--draft")
    gh_args.extend([
        "--title",
        release_title,
        "--notes-file",
        release_notes,
        f"{artifacts_file}#artifacts.md",
    ])
    _run_gh(gh_args)
