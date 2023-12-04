import docker
import json
import logging
import requests

from docker.client import DockerClient

from typing import Callable, Dict, Optional
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType


_logger = get_status_logger(LogType.DOCKER_IMAGE)


def get_from_dict(d: Dict[str, any], *keys: str) -> str:
    for key in keys:
        if not key in d:
            return None
        d = d[key]
    return d


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
    def __init__(self, repository: str, username: str, password: str):
        self.repository = repository
        self.username = username
        self.password = password
        self._client = None

    def client(self):
        if self._client is None:
            self._client = docker.from_env()
        return self._client

    def push(self, tag: str):
        auth_config = {
            "username": self.username,
            "password": self.password,
        }
        resp = self.client().images.push(
            repository=self.repository,
            tag=tag,
            auth_config=auth_config,
            stream=True,
            decode=True,
        )
        reporter = ProgressReporter(_logger.isEnabledFor(logging.INFO))
        for el in resp:
            reporter.report(
                el.get("status", None),
                el.get("progress", None),
            )
