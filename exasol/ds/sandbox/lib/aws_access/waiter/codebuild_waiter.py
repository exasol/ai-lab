import time

from typing import Iterable, Any
from datetime import timedelta
from tenacity import retry, TryAgain, RetryError
from tenacity.wait import wait_fixed
from tenacity.stop import stop_after_delay
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType

LOG = get_status_logger(LogType.AWS_ACCESS)


class CodeBuildWaiter:
    """
    Provides method "wait" which waits until the build finishes or runs into the
    given timeout.
    """
    def __init__(self, codebuild_client: Any, build_id: int):
        self._build_id = build_id
        self._codebuild_client = codebuild_client

    def wait(
            self,
            timeout: timedelta = timedelta(hours=3, minutes=30),
            interval: timedelta = timedelta(minutes=10),
    ):
        """
        Waits until the build finishes or runs into the timeout given by parameter "timeout".
        If the build finishes with an error or ran into the timeout, it throws an exception;
        otherwise it returns normally.
        :param timeout: Timeout to wait for the build to finish.
        :param interval: Interval for polling the status of the CodeBuild.
        :raises RuntimeError: If the build finishes with an error.
        :raises TimeoutError: If the build did not finish before the timeout time was reached.
        """

        @retry(wait=wait_fixed(interval), stop=stop_after_delay(timeout))
        def poll_build_status():
            LOG.debug(f"Checking status of codebuild id {self._build_id}.")
            build_response = self._codebuild_client.batch_get_builds(ids=[self._build_id])
            LOG.debug(f"Build response of codebuild id {self._build_id} is {build_response}")
            if len(build_response['builds']) != 1:
                LOG.error(f"Unexpected return value from 'batch_get_builds': {build_response}")
            build_status = build_response['builds'][0]['buildStatus']
            LOG.info(f"Build status of codebuild id {self._build_id} is {build_status}")
            if build_status == "IN_PROGRESS":
                raise TryAgain
            return build_status

        try:
            status = poll_build_status()
            if status in ['FAILED', 'FAULT', 'STOPPED', 'TIMED_OUT']:
                raise RuntimeError(f"Build ({self._build_id}) failed with status: {status}")
            if status != "SUCCEEDED":
                raise RuntimeError(f"Build {self._build_id} has unknown build status: {status}")
        except RetryError:
            raise TimeoutError(f"Build {self._build_id} ran into timeout.")
