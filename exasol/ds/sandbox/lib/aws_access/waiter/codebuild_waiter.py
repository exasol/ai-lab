import time
from typing import Iterable, Any

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

    @staticmethod
    def _wait_for(seconds: int, interval: int) -> Iterable[int]:
        for _ in range(int(seconds / interval)):
            yield interval

    def wait(self, timeout_in_seconds: int = 60*60*2, interval_in_seconds: int = 30):
        """
        Waits until the build finishes or runs into the timeout given by parameter "timeout_in_minutes".
        If the build finishes with an error or ran into the timeout, it throws an exception;
        otherwise it returns normally.
        :param timeout_in_seconds: Timeout to wait for the build to finish. If exceeds it throws a RuntimeError.
        :param interval_in_seconds: Interval for polling the status info of the CodeBuild.
        :raises RuntimeError: If the build finishes with an error.
        :raises TimeoutError: If the build did not finish before the timeout time was reached.
        """
        for seconds_to_wait in self._wait_for(seconds=timeout_in_seconds, interval=interval_in_seconds):
            time.sleep(seconds_to_wait)
            LOG.debug(f"Checking status of codebuild id {self._build_id}.")
            build_response = self._codebuild_client.batch_get_builds(ids=[self._build_id])
            LOG.debug(f"Build response of codebuild id {self._build_id} is {build_response}")
            if len(build_response['builds']) != 1:
                LOG.error(f"Unexpected return value from 'batch_get_builds': {build_response}")
            build_status = build_response['builds'][0]['buildStatus']
            LOG.info(f"Build status of codebuild id {self._build_id} is {build_status}")
            if build_status == 'SUCCEEDED':
                break
            elif build_status in ['FAILED', 'FAULT', 'STOPPED', 'TIMED_OUT']:
                raise RuntimeError(f"Build ({self._build_id}) failed with status: {build_status}")
            elif build_status != "IN_PROGRESS":
                raise RuntimeError(f"Build {self._build_id} has unknown build status: {build_status}")
        # if loop does not break early, build wasn't successful
        else:
            raise TimeoutError(f"Build {self._build_id} ran into timeout.")

