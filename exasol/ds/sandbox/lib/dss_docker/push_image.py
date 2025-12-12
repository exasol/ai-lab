import json
import logging
from typing import (
    Callable,
    Optional,
)

import docker
import requests
from docker.client import DockerClient

from exasol.ds.sandbox.lib.dicts import DictAccessor
from exasol.ds.sandbox.lib.logging import (
    LogType,
    get_status_logger,
)

_logger = get_status_logger(LogType.DOCKER_IMAGE)


class ProgressReporter:
    """
    Optional parameter :verbosity: controls the verbosity. If :verbosity:
    is :None: then report neither status nor progress.  If :verbosity: is a
    float value then report every status change and this fraction of the progress
    messages for a given status.

    For example, if :verbosity: is set to 0.1 then report only every 10th progress message.
    """
    def __init__(
            self,
            verbosity: Optional[float] = 1.0,
            on_status: Callable = None,
            on_progress: Callable = None,
    ):
        self._last_status = None
        self._verbosity = verbosity
        self._need_linefeed = False
        self._on_status = on_status or _logger.info
        self._on_progress = on_progress or print
        self._suppressed = 0

    def _report(self, printer: Callable, msg: Optional[str], **kwargs):
        printer(msg, **kwargs)

    def _linefeed(self):
        if self._need_linefeed:
            self._need_linefeed = False
            self._on_progress()

    def _needs_report(self, msg: Optional[str]):
        if msg is None or self._verbosity is None:
            return False
        self._suppressed += 1
        if self._suppressed * self._verbosity < 1:
            return False
        self._suppressed = 0
        return True


    def report(self, status: Optional[str], progress: Optional[str]):
        if self._verbosity is None:
            return
        if status == self._last_status:
            if self._needs_report(progress):
                self._report(self._on_progress, progress, end="\r")
                self._need_linefeed = progress
        else:
            self._last_status = status
            self._linefeed()
            self._report(self._on_status, status)


class DockerRegistry:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def push(self, repository: str, tag: str):
        auth_config = {
            "username": self.username,
            "password": self.password,
        }
        client = docker.from_env()
        responses = client.images.push(
            repository=repository,
            tag=tag,
            auth_config=auth_config,
            stream=True,
            decode=True,
        )
        verbosity = 0.01 if _logger.isEnabledFor(logging.INFO) else 0
        reporter = ProgressReporter(verbosity)
        for resp in responses:
            el = DictAccessor(resp)
            if error := el.get("error"):
                _logger.error(error)
                details = el.get("errorDetail", "message")
                if details is not None and details != error:
                    _logger.error(f"Details: {details}")
            reporter.report(el.get("status"), el.get("progress"))
