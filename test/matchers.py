import re


class re_search:
    def __init__(self, pattern: str, flags: re.RegexFlag = 0):
        self._re = re.compile(pattern, flags)

    def __eq__(self, other) -> bool:
        return isinstance(other, str) and self._re.search(other)

    def __repr__(self) -> str:
        return self._re.pattern
