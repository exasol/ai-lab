import logging
import re
from typing import Tuple, Dict, List

from exasol_script_languages_developer_sandbox.lib.aws_access.aws_access import AwsAccess
from exasol_script_languages_developer_sandbox.lib.aws_access.stack_resource import StackResource
from exasol_script_languages_developer_sandbox.lib.config import ConfigObject
from exasol_script_languages_developer_sandbox.lib.github_release_access import GithubReleaseAccess
from exasol_script_languages_developer_sandbox.lib.logging import get_status_logger, LogType
from exasol_script_languages_developer_sandbox.lib.setup_release_codebuild.release_codebuild import \
    RELEASE_CODE_BUILD_STACK_NAME

LOG = get_status_logger(LogType.RELEASE_BUILD)


def get_environment_variable_override(env_variable: Tuple[str, str]) -> Dict[str, str]:
    return {"name": env_variable[0], "value": env_variable[1], "type": "PLAINTEXT"}


def get_aws_codebuild_project(resources: List[StackResource]) -> StackResource:
    matching_project = [resource for resource in resources if resource.is_code_build]
    if len(matching_project) == 0:
        raise ValueError(f"No release codebuild project deployed. Found following resources: {resources}")
    if len(matching_project) > 1:
        raise RuntimeError(f"Multiple release codebuild projects match. Found following matches: {matching_project}")
    return matching_project[0]


def _parse_upload_url(upload_url: str) -> int:
    """
    upload_url is expected to have the following format: `https://uploads.github.com/repos/exasol/script-languages-repo/releases/123/assets{?name,label}`
    where `exasol/script-languages-repo` is the repository for which the release will be created and 123 is the id of the release.
    This method return release id as integer.
    """
    res = re.search(r"^https://uploads.github.com/repos/([a-zA-Z0-9\-_/]+)/releases/([\d]+)/assets", upload_url)
    if res is None:
        raise ValueError("Parameter upload_url is in unexpected format.")
    return int(res.groups()[1])


def _execute_release_build(aws_access: AwsAccess, branch: str, asset_id: str,
                           release_id: int, gh_token: str, make_ami_public: bool) -> None:
    """
    This function:
    1. Retrieve resources for the release codebuild stack for that given project
    2. Find the resource with type CodeBuild
    3. Creates the environment variables override
    4. Start and wait for build
    :raises:
        `RuntimeError` if build goes wrong or if anything on AWS CodeBuild is not as expected
        `ValueError` if project is not found on AWS CodeBuild or if the upload is not in expected format.
    The upload url is only be used to get the release id.
    """
    resources = aws_access.get_all_stack_resources(RELEASE_CODE_BUILD_STACK_NAME)
    matching_project = get_aws_codebuild_project(resources)

    if gh_token is None:
        raise RuntimeError("Parameter gh_token must not be None.")

    env_variables = [("RELEASE_ID", f"{release_id}"),
                     ("ASSET_ID", f"{asset_id}"),
                     ("GITHUB_TOKEN", gh_token)]
    if make_ami_public:
        env_variables.append(("MAKE_AMI_PUBLIC_OPTION", "--make-ami-public"))
    else:
        env_variables.append(("MAKE_AMI_PUBLIC_OPTION", "--no-make-ami-public"))
    environment_variables_overrides = list(map(get_environment_variable_override, env_variables))
    _, waiter = aws_access.start_codebuild(matching_project.physical_id,
                                           environment_variables_overrides=environment_variables_overrides,
                                           branch=branch)
    waiter.wait()


def run_start_release_build(aws_access: AwsAccess, config: ConfigObject,
                            upload_url: str, branch: str, gh_token: str) -> None:
    logging.info(f"run_start_release_build for aws profile {aws_access.aws_profile_for_logging} "
                 f"with upload url: {upload_url}")
    _execute_release_build(aws_access, branch, asset_id=config.slc_version,
                           release_id=_parse_upload_url(upload_url=upload_url), gh_token=gh_token,
                           make_ami_public=True)


def run_start_test_release_build(aws_access: AwsAccess, gh_access: GithubReleaseAccess,
                                 branch: str, release_title: str, gh_token: str) -> None:
    logging.info(f"run_start_test_release_build for aws profile {aws_access.aws_profile_for_logging} "
                 f"for branch: {branch} with title: {release_title}")
    release_id = gh_access.create_release(branch, release_title)
    _execute_release_build(aws_access, branch, asset_id=release_title, release_id=release_id,
                           gh_token=gh_token, make_ami_public=False)
