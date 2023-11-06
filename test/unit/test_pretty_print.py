import re
import time
from exasol.ds.sandbox.lib import pretty_print
from datetime import datetime, timedelta


def test_elapsed_rounded():
    start = datetime.now()
    time.sleep(1.2)
    e = pretty_print.elapsed(start)
    assert e == "0:00:01"


def test_elapsed_full():
    start = datetime.now()
    time.sleep(1.2)
    e = pretty_print.elapsed(start, round_to_seconds=False)
    assert re.match(r'0:00:01\.2.*', e)


def test_size_1000():
    s = pretty_print.size(3100, 1000, "g")
    print(f'size: {s}')
    assert s == "3.1 Kg"


def test_size_default():
    s = pretty_print.size(3100)
    print(f'size: {s}')
    assert s == "3.0 KiB"
