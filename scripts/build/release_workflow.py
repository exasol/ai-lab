import argparse
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.config import default_config_object
from exasol.ds.sandbox.lib.release_build.run_release_build import run_start_release_build
from exasol.ds.sandbox.lib.release_notes import write_release_notes
from scripts.build.check_release import get_poetry_version, validate_release


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
    return release_tag.removeprefix("refs/tags/").removeprefix("v")


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


def write_workflow_env(context: ReleaseContext) -> None:
    github_env_path = _workflow_env("GITHUB_ENV")
    if not github_env_path:
        raise RuntimeError("GITHUB_ENV must be set")
    lines = {
        "AWS_DEFAULT_REGION": _workflow_env("AWS_DEFAULT_REGION"),
        "RELEASE_MODE": context.mode,
        "RELEASE_TAG": context.release_tag,
        "RELEASE_VERSION": context.release_version,
        "RELEASE_REF": context.release_ref,
        "RELEASE_TITLE_INPUT": context.release_title_input,
        "RELEASE_ASSET_ID": context.release_asset_id,
        "RELEASE_IS_MANUAL": "true" if context.release_is_manual else "false",
        "RELEASE_NOTES_DIR": str(context.release_notes_dir),
    }
    with open(github_env_path, "a", encoding="utf-8") as handle:
        for key, value in lines.items():
            handle.write(f"{key}={value}\n")


def run_check(context: ReleaseContext) -> None:
    if context.release_is_manual:
        validate_release("")
    else:
        validate_release(context.release_tag)


def run_build(context: ReleaseContext) -> None:
    run_start_release_build(
        default_config_object,
        publish=True,
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

    if context.release_is_manual:
        if _release_exists(context.release_ref):
            _run_gh(
                [
                    "release",
                    "edit",
                    context.release_ref,
                    "--title",
                    release_title,
                    "--notes-file",
                    release_notes,
                ]
            )
            _run_gh([
                "release",
                "upload",
                context.release_ref,
                f"{artifacts_file}#artifacts.md",
                "--clobber",
            ])
        else:
            _run_gh(
                [
                    "release",
                    "create",
                    context.release_ref,
                    "--draft",
                    "--title",
                    release_title,
                    "--notes-file",
                    release_notes,
                    f"{artifacts_file}#artifacts.md",
                ]
            )
        return

    if _release_exists(context.release_ref):
        _run_gh(
            [
                "release",
                "edit",
                context.release_ref,
                "--title",
                release_title,
                "--notes-file",
                release_notes,
            ]
        )
        _run_gh([
            "release",
            "upload",
            context.release_ref,
            f"{artifacts_file}#artifacts.md",
            "--clobber",
        ])
    else:
        _run_gh(
            [
                "release",
                "create",
                context.release_ref,
                "--title",
                release_title,
                "--notes-file",
                release_notes,
                f"{artifacts_file}#artifacts.md",
            ]
        )


def _release_exists(release_ref: str) -> bool:
    try:
        subprocess.run(["gh", "release", "view", release_ref], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("context")
    subparsers.add_parser("check")
    subparsers.add_parser("build")
    subparsers.add_parser("notes")
    subparsers.add_parser("publish")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    context = load_context()
    if args.command == "context":
        write_workflow_env(context)
    elif args.command == "check":
        run_check(context)
    elif args.command == "build":
        run_build(context)
    elif args.command == "notes":
        run_notes(context)
    elif args.command == "publish":
        run_publish(context)
    else:
        raise RuntimeError(f"Unknown command {args.command}")


if __name__ == "__main__":
    main()
