import pytest
import re
from exasol.ds.sandbox.lib import pretty_print
from datetime import datetime, timedelta


@pytest.fixture
def sample_duration():
    return timedelta(hours=2, minutes=3, seconds=4.2)


def test_elapsed_rounded(sample_duration):
    start = datetime.now() - sample_duration
    e = pretty_print.elapsed(start)
    assert e == "2:03:04"


def test_elapsed_full(sample_duration):
    start = datetime.now() - sample_duration
    e = pretty_print.elapsed(start, round_to_seconds=False)
    assert re.match(r'2:03:04\.2.*', e)
