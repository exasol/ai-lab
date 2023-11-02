import time
from typing import List, Iterator
from unittest.mock import MagicMock

import pytest

from exasol.ds.sandbox.lib.aws_access.waiter.codebuild_waiter import CodeBuildWaiter
from test.mock_cast import mock_cast

BUILD_ID = 123


def codebuild_client(build_duration: int, finish_status: str):

    start_time = time.time()

    def batch_get_builds(ids: List[int]):
        if len(ids) == 1 and ids[0] == BUILD_ID:
            time_elapsed = time.time() - start_time
            if time_elapsed < build_duration:
                return {
                    'builds': [{'buildStatus': "IN_PROGRESS"}]
                }
            else:
                return {
                    'builds': [{'buildStatus': finish_status}]
                }

    codebuild_mock = MagicMock()
    mock_cast(codebuild_mock.batch_get_builds).side_effect = batch_get_builds
    return codebuild_mock


@pytest.mark.parametrize("interval", list(range(1, 5)))
def test_code_build_waiter_success(interval):

    codebuild_mock = codebuild_client(build_duration=5, finish_status="SUCCEEDED")
    waiter = CodeBuildWaiter(codebuild_mock, BUILD_ID)
    waiter.wait(timeout_in_seconds=10, interval_in_seconds=interval)


@pytest.mark.parametrize("interval", list(range(1, 3)))
def test_code_build_waiter_timeout(interval):

    codebuild_mock = codebuild_client(build_duration=15, finish_status="SUCCEEDED")
    waiter = CodeBuildWaiter(codebuild_mock, BUILD_ID)
    with pytest.raises(TimeoutError, match=f"Build {BUILD_ID} ran into timeout."):
        waiter.wait(timeout_in_seconds=3, interval_in_seconds=interval)


@pytest.mark.parametrize("error_status", ['FAILED', 'FAULT', 'STOPPED', 'TIMED_OUT'])
def test_code_build_waiter_error(error_status):

    codebuild_mock = codebuild_client(build_duration=3, finish_status=error_status)
    waiter = CodeBuildWaiter(codebuild_mock, BUILD_ID)
    with pytest.raises(RuntimeError, match=f"Build \\({BUILD_ID}\\) failed with status: {error_status}"):
        waiter.wait(timeout_in_seconds=10, interval_in_seconds=1)


def test_code_build_waiter_unknown_error():

    codebuild_mock = codebuild_client(build_duration=3, finish_status="UNKNOWN_ERROR")
    waiter = CodeBuildWaiter(codebuild_mock, BUILD_ID)
    with pytest.raises(RuntimeError, match=f"Build {BUILD_ID} has unknown build status: UNKNOWN_ERROR"):
        waiter.wait(timeout_in_seconds=10, interval_in_seconds=1)
