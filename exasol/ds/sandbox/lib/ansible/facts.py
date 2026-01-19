from typing import Any

from exasol.ds.sandbox.lib.dicts import DictAccessor


class AnsibleFacts(DictAccessor):
    def __init__(self, facts: dict[str, Any]):
        super().__init__(facts, prefixes=["dss_facts"])
