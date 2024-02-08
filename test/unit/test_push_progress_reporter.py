from exasol.ds.sandbox.lib.dss_docker.push_image import ProgressReporter
from typing import List, Optional


class Simulation:
    def __init__(self, verbosity: Optional[float] = 1):
        self._impl = ProgressReporter(verbosity, self._on_status, self._on_progress)
        self.output = ""

    def _on_status(self, message):
        self.output += f"[LOG] {message}\n"

    def _on_progress(self, message="", end="\n"):
        self.output += message + end

    def feed(self, *args):
        self._impl.report(*args)
        return self


def test_non_verbosity():
    assert (
        Simulation(verbosity=None)
        .feed("S1", "(ignore)")
        .feed("S1", "progress")
        .output
    ) == ""


def test_1_status():
    assert (
        Simulation()
        .feed("Status 1", "(ignore)")
        .output
    ) == "[LOG] Status 1\n"


def test_2_status():
    assert (
        Simulation()
        .feed("S1", "(ignore 1)")
        .feed("S2", "(ignore 2)")
        .output
    ) == (
        "[LOG] S1\n"
        "[LOG] S2\n"
    )


def test_status_progress():
    assert (
        Simulation()
        .feed("S1", "(ignore)")
        .feed("S1", "some progress")
        .output
    ) == (
        "[LOG] S1\n"
        "some progress\r"
    )


def test_status_2_progress_status():
    assert (
        Simulation()
        .feed("init", "(ignore 1)")
        .feed("init", "P1")
        .feed("init", "P2")
        .feed("main", "(ignore 2)")
        .output
    ) == (
        "[LOG] init\n"
        "P1\r"
        "P2\r\n"
        "[LOG] main\n"
    )

def test_verbosity_50_percent():
    assert (
        Simulation(verbosity=0.5)
        .feed("S1", "(ignore 1)")
        .feed("S1", "P1-1")
        .feed("S1", "P1-2")
        .feed("S2", "(ignore 2)")
        .feed("S2", "P2-1")
        .feed("S2", "P2-2")
        .output
    ) == (
        "[LOG] S1\n"
        "P1-2\r\n"
        "[LOG] S2\n"
        "P2-2\r"
    )
