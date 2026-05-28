import argparse
from pathlib import Path

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.release_notes import write_release_notes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release-version",
        "--release-tag",
        dest="release_version",
        required=True,
        help="The release version or refs/tags/... reference to generate notes for.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory where release_title.txt, release_notes.md and artifacts.md are written.",
    )
    parser.add_argument(
        "--asset-id",
        default=None,
        help="Asset identifier used to print the release artifacts. Defaults to the release version.",
    )
    parser.add_argument(
        "--release-title",
        default=None,
        help="Optional explicit title for the GitHub release.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    write_release_notes(
        args.release_version,
        AwsAccess(None),
        args.output_dir,
        asset_id=args.asset_id,
        release_title=args.release_title,
    )


if __name__ == "__main__":
    main()
