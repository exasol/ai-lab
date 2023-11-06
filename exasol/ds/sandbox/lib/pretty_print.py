from datetime import datetime, timedelta


def elapsed(start: datetime, round_to_seconds=True) -> str:
    d = datetime.now() - start
    if round_to_seconds:
        d = d - timedelta(microseconds=d.microseconds)
    return str(d)


def size(num: int, factor: float = 1024, unit: str = "B") -> str:
    """
    Formats size into a human-readable string using ISO unit prefix K for
    kilo, G for Giga, etc..  By default uses steps of factor 1024, but user
    can override factor, e.g. with 1000.
    """
    factor = float(factor)
    suffix = "i" if factor == 1024.0 else ""
    for prefix in ("", "K", "M", "G", "T", "P", "E", "Z"):
        if abs(num) < factor:
            return f"{num:3.1f} {prefix}{suffix}{unit}"
        num /= factor
    return f"{num:.1f} Y{suffix}{unit}"
