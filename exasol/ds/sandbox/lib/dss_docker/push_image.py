import docker
import json
import logging
import requests

from docker.client import DockerClient

from typing import Callable, Optional
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType
from exasol.ds.sandbox.lib.dss_docker.create_image import get_nested_value


_logger = get_status_logger(LogType.DOCKER_IMAGE)


class ProgressReporter:
    def __init__(self, verbose: bool):
        self.last_status = None
        self.verbose = verbose
        self.need_linefeed = False

    def _report(self, printer: Callable, msg: Optional[str], **kwargs):
        if msg is not None:
            printer(msg, **kwargs)

    def _linefeed(self):
        if self.need_linefeed:
            self.need_linefeed = False
            print()

    def report(self, status: Optional[str], progress: Optional[str]):
        if not self.verbose:
            return
        if status == self.last_status:
            self._report(print, progress, end="\r")
            self.need_linefeed = progress
        else:
            self.last_status = status
            self._linefeed()
            self._report(_logger.info, status)


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
        resp = client.images.push(
            repository=repository,
            tag=tag,
            auth_config=auth_config,
            stream=True,
            decode=True,
        )
        reporter = ProgressReporter(_logger.isEnabledFor(logging.INFO))
        for el in resp:
            error = el.get("error", None)
            if error is not None:
                _logger.error(error)
                details = get_nested_value(el, "errorDetail", "message")
                if details is not None and details != error:
                    _logger.error(f"Details: {details}")
            reporter.report(
                el.get("status", None),
                el.get("progress", None),
            )
