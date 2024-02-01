import datetime
from typing import Union
from unittest.mock import create_autospec, Mock

from dateutil.tz import tzutc

from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess
from exasol.ds.sandbox.lib.aws_access.stack_resource import StackResource
from exasol.ds.sandbox.lib.aws_access.waiter.codebuild_waiter import CodeBuildWaiter
from exasol.ds.sandbox.lib.github_release_access import GithubReleaseAccess
from exasol.ds.sandbox.lib.release_build.run_release_build import run_start_release_build, \
    run_start_test_release_build
from test.mock_cast import mock_cast

UPLOAD_URL = "https://uploads.github.com/repos/exasol/ai-lab/releases/123/assets{?name,label}"
BRANCH = "main"
GITHUB_TOKEN = "gh_secret"

DUMMY_RESOURCES = [
    StackResource({'LogicalResourceId': 'CodeBuildLogGroup',
     'PhysicalResourceId': '/aws/codebuild/log-id',
     'ResourceType': 'AWS::Logs::LogGroup',
     'LastUpdatedTimestamp': datetime.datetime(2022, 5, 4, 18, 39, 11, 935000, tzinfo=tzutc()),
     'ResourceStatus': 'CREATE_COMPLETE', 'DriftInformation': {'StackResourceDriftStatus': 'NOT_CHECKED'}
     }),
    StackResource({'LogicalResourceId': 'CodeBuildRole',
     'PhysicalResourceId': 'role-id',
     'ResourceType': 'AWS::IAM::Role',
     'LastUpdatedTimestamp': datetime.datetime(2022, 5, 4, 18, 39, 1, 806000, tzinfo=tzutc()),
     'ResourceStatus': 'CREATE_COMPLETE', 'DriftInformation': {'StackResourceDriftStatus': 'NOT_CHECKED'}
     }),
    StackResource({'LogicalResourceId': 'dataScienceSandboxReleaseCodeBuild',
     'PhysicalResourceId': 'codebuild-id-123',
     'ResourceType': 'AWS::CodeBuild::Project',
     'LastUpdatedTimestamp': datetime.datetime(2022, 5, 4, 18, 39, 7, 850000, tzinfo=tzutc()),
     'ResourceStatus': 'CREATE_COMPLETE', 'DriftInformation': {'StackResourceDriftStatus': 'NOT_CHECKED'}
     })
]


def test_release_build(test_config):
    """
    Test that serialization and deserialization of KeyFileManager work!
    """
    aws_access_mock: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws_access_mock.get_all_stack_resources).return_value = DUMMY_RESOURCES
    mock_cast(aws_access_mock.start_codebuild).return_value = (123, create_autospec(CodeBuildWaiter))
    run_start_release_build(aws_access_mock, test_config, UPLOAD_URL, BRANCH, GITHUB_TOKEN)
    expected_overrides = [
        {"name": "RELEASE_ID", "value": "123", "type": "PLAINTEXT"},
        {"name": "ASSET_ID", "value": test_config.ai_lab_version, "type": "PLAINTEXT"},
        {"name": "GITHUB_TOKEN", "value": GITHUB_TOKEN, "type": "PLAINTEXT"},
        {"name": "MAKE_AMI_PUBLIC_OPTION", "value": "--make-ami-public", "type": "PLAINTEXT"}
    ]

    mock_cast(aws_access_mock.start_codebuild).\
        assert_called_once_with(
            "codebuild-id-123",
            environment_variables_overrides=expected_overrides,
            branch=BRANCH)


def test_test_release_build(test_config):
    """
    Test that serialization and deserialization of KeyFileManager work!
    """
    aws_access_mock: Union[AwsAccess, Mock] = create_autospec(AwsAccess, spec_set=True)
    mock_cast(aws_access_mock.start_codebuild).return_value = (123, create_autospec(CodeBuildWaiter))
    gh_release_access_mock: Union[GithubReleaseAccess, Mock] = create_autospec(GithubReleaseAccess, spec_set=True)
    release_title = "Test Release"
    release_id = 12345
    mock_cast(gh_release_access_mock.create_release).return_value = release_id
    mock_cast(aws_access_mock.get_all_stack_resources).return_value = DUMMY_RESOURCES
    run_start_test_release_build(aws_access_mock, gh_release_access_mock, BRANCH, release_title, GITHUB_TOKEN)
    expected_env_variable_overrides = [
        {"name": "RELEASE_ID", "value": str(release_id), "type": "PLAINTEXT"},
        {"name": "ASSET_ID", "value": release_title, "type": "PLAINTEXT"},
        {"name": "GITHUB_TOKEN", "value": GITHUB_TOKEN, "type": "PLAINTEXT"},
        {"name": "MAKE_AMI_PUBLIC_OPTION", "value": "--no-make-ami-public", "type": "PLAINTEXT"}
    ]

    mock_cast(gh_release_access_mock.create_release).assert_called_once_with(BRANCH, release_title)

    mock_cast(aws_access_mock.start_codebuild).\
        assert_called_once_with("codebuild-id-123",
                                environment_variables_overrides=expected_env_variable_overrides,
                                branch=BRANCH)
