import logging
import tempfile

from exasol.ds.sandbox.lib.asset_id import AssetId
from exasol.ds.sandbox.lib.asset_printing.print_assets import print_assets, AssetTypes
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.github_release_access import GithubReleaseAccess
from exasol.ds.sandbox.lib.render_template import render_template


def run_update_release(aws_access: AwsAccess, gh_access: GithubReleaseAccess,
                       release_id: int, asset_id: AssetId) -> None:
    logging.info(f"run_update_release for aws profile {aws_access.aws_profile_for_logging}")

    additional_release_notes = render_template("additional_release_notes.jinja")
    with tempfile.TemporaryDirectory() as temp_dir:
        artifacts_file = f"{temp_dir}/artifacts.md"
        asset_types = tuple(
            AssetTypes.DOCKER,
            AssetTypes.AMI,
            AssetTypes.VM_S3,
        )
        with open(artifacts_file, "w") as file:
            print_assets(aws_access, asset_id, file, asset_types)
        content = additional_release_notes + open(artifacts_file, "r").read()
        gh_access.update_release_message(release_id, content)
        gh_access.upload(archive_path=artifacts_file, label="artifacts.md",
                         release_id=release_id, content_type="text/markdown")
