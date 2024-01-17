import os
import sys

from pathlib import Path

from github import Github, GithubException
from github.Repository import Repository

from exasol.ds.sandbox.lib.logging import get_status_logger, LogType


LOG = get_status_logger(LogType.RELEASE_ACCESS)
GITHUB_TOKEN_ENV = "GITHUB_TOKEN"


def github_token_or_exit() -> str:
    variable = GITHUB_TOKEN_ENV
    value = os.getenv(variable)
    if value is not None:
        return value
    LOG.error(f"Environment variable {variable} is not set")
    sys.exit(1)


class GithubReleaseAccess:

    def __init__(self, gh_token: str):
        self._gh_token = gh_token

    def create_release(self, branch: str, title: str) -> int:
        """
        Implements creation of a Github Draft Release.
        See https://docs.github.com/en/rest/releases/releases for details.
        Returns the internal ID of the new release.
        """
        release = self._get_repo.create_git_release(tag="", name=title, message="Test-Release",
                                                    draft=True, prerelease=False, target_commitish=branch)
        return release.id

    def update_release_message(self, release_id: int, message_to_append: str) -> None:
        """
        Updates an existing release, identified by parameter "release_id".
        The release message body will be extended by parameter "message_to_append".
        See https://docs.github.com/en/rest/releases/releases for details.
        """
        release = self._get_repo.get_release(release_id)
        body = release.body
        body += "\n\n" + message_to_append
        release.update_release(name=release.title, message=body, draft=True, prerelease=False)

    def upload(self, archive_path: str, label: str, release_id: int, content_type: str):
        """
        Attaches a file to the release. The file is given by parameter "archive_path", and will be labeled with value
        of parameter "label". The release is identified by parameter "release_id". Parameter "content_type" must
        contain the media type of the archive.
        See https://docs.github.com/en/rest/releases/assets for details.
        """
        release = self._get_repo.get_release(release_id)
        # Check GH limitation
        # https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases#storage-and-bandwidth-quotas
        if Path(archive_path).stat().st_size >= 2 * (2 ** 30):
            LOG.error("File larger than 2GB. Skipping it...")
        else:
            try:
                release.upload_asset(path=archive_path, label=label, content_type=content_type)
            except GithubException as ex:
                LOG.error(f"Upload of asset {archive_path} to release {release_id} failed: {ex}")
                raise ex

    @property
    def _get_repo(self) -> Repository:
        gh = Github(self._gh_token)
        gh_repo = gh.get_repo("exasol/data-science-sandbox")
        return gh_repo
