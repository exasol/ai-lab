from typing import Any

import exasol.ansible as ansible
import pytest

SAMPLE_FACTS = {"a": {"b": {"c": "value"}}}


@pytest.fixture
def sample_facts() -> ansible.Facts:
    return ansible.Facts({"dss_facts": SAMPLE_FACTS}, prefixes=["dss_facts"])


@pytest.mark.parametrize("keys, expected", [
    ([], SAMPLE_FACTS),
    (["missing"], None),
    (["a"], SAMPLE_FACTS["a"]),
    (["a", "b", "c"], "value"),
])
def test_ansible_facts(
    sample_facts: ansible.Facts,
    keys: list[str],
    expected: Any,
) -> None:
    assert sample_facts.get(*keys) == expected


def test_as_dict() -> None:
    inner = {
        "a": {"a1": "AA"},
        "b": {"b1": "BB"},
    }
    facts = ansible.Facts({"dss_facts": inner}, prefixes=["dss_facts"])
    spec = {
        "MISSING": ("c",),
        "VA": ("a", "a1"),
        "VB": ("b", "b1"),
    }
    actual = facts.as_dict(spec)
    expected = {"VA": "AA", "VB": "BB"}
    assert expected == actual
