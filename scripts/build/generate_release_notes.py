from pathlib import Path

import click

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.release_notes import write_release_notes


@click.command()
@click.option(
    "--release-version",
    "--release-tag",
    "release_version",
    required=True,
    help="The bare release version or refs/tags/... reference to generate notes for.",
)
@click.option(
    "--output-dir",
    required=True,
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
    help="Directory where release_title.txt, release_notes.md and artifacts.md are written.",
)
@click.option(
    "--asset-id",
    default=None,
    help="Asset identifier used to print the release artifacts. Defaults to the release version.",
)
@click.option(
    "--release-title",
    default=None,
    help="Optional explicit title for the GitHub release.",
)
def main(
    release_version: str,
    output_dir: Path,
    asset_id: str | None,
    release_title: str | None,
) -> None:
    write_release_notes(
        release_version,
        AwsAccess(None),
        output_dir,
        asset_id=asset_id,
        release_title=release_title,
    )


if __name__ == "__main__":
    main()
