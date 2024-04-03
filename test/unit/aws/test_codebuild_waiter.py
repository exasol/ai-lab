import time
from typing import List, Iterator
from unittest.mock import MagicMock
from datetime import datetime, timedelta

import pytest

from exasol.ds.sandbox.lib.aws_access.waiter.codebuild_waiter import CodeBuildWaiter
from test.mock_cast import mock_cast

BUILD_ID = 123


def ms(value: int) -> timedelta:
    return timedelta(milliseconds=value)


def codebuild_client(build_duration: timedelta, finish_status: str) -> MagicMock:
    end_time = datetime.now() + build_duration
    def batch_get_builds(ids: List[int]):
        if len(ids) == 1 and ids[0] == BUILD_ID:
            value = finish_status if datetime.now() > end_time else "IN_PROGRESS"
            return { 'builds': [{'buildStatus': value}] }
    codebuild_mock = MagicMock()
    mock_cast(codebuild_mock.batch_get_builds).side_effect = batch_get_builds
    return codebuild_mock


@pytest.mark.parametrize("interval", list(range(1, 5)))
def test_code_build_waiter_success(interval):
    codebuild_mock = codebuild_client(
        build_duration=ms(50),
        finish_status="SUCCEEDED",
    )
    waiter = CodeBuildWaiter(codebuild_mock, BUILD_ID)
    waiter.wait(timeout=ms(100), interval=ms(interval*30))


@pytest.mark.parametrize("interval", list(range(1, 3)))
def test_code_build_waiter_timeout(interval):
    codebuild_mock = codebuild_client(
        build_duration=ms(100),
        finish_status="SUCCEEDED",
    )
    waiter = CodeBuildWaiter(codebuild_mock, BUILD_ID)
    with pytest.raises(TimeoutError, match=f"Build {BUILD_ID} ran into timeout."):
        waiter.wait(timeout=ms(80), interval=ms(interval*20))


@pytest.mark.parametrize("error_status", ['FAILED', 'FAULT', 'STOPPED', 'TIMED_OUT'])
def test_code_build_waiter_error(error_status):
    codebuild_mock = codebuild_client(
        build_duration=ms(50),
        finish_status=error_status,
    )
    waiter = CodeBuildWaiter(codebuild_mock, BUILD_ID)
    with pytest.raises(RuntimeError, match=f"Build \\({BUILD_ID}\\) failed with status: {error_status}"):
        waiter.wait(timeout=ms(400), interval=ms(20))


def test_code_build_waiter_unknown_error():
    codebuild_mock = codebuild_client(
        build_duration=ms(50),
        finish_status="UNKNOWN_ERROR",
    )
    waiter = CodeBuildWaiter(codebuild_mock, BUILD_ID)
    with pytest.raises(RuntimeError, match=f"Build {BUILD_ID} has unknown build status: UNKNOWN_ERROR"):
        waiter.wait(timeout=ms(100), interval=ms(20))
