import argparse
from pathlib import Path

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.release_notes import write_release_notes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release-tag",
        required=True,
        help="The release tag or refs/tags/... reference to generate notes for.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory where release_title.txt, release_notes.md and artifacts.md are written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    write_release_notes(args.release_tag, AwsAccess(None), args.output_dir)


if __name__ == "__main__":
    main()
