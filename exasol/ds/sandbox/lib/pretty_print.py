from datetime import datetime, timedelta


def elapsed(start: datetime, round_to_seconds=True) -> str:
    d = datetime.now() - start
    if round_to_seconds:
        d = d - timedelta(microseconds=d.microseconds)
    return str(d)
