from typing import Any

import pytest

from exasol.ds.sandbox.lib.ansible.facts import AnsibleFacts

SAMPLE_FACTS = {"a": {"b": {"c": "value"}}}


@pytest.fixture
def sample_facts() -> AnsibleFacts:
    return AnsibleFacts({"dss_facts": SAMPLE_FACTS})


@pytest.mark.parametrize("keys, expected", [
    ([], SAMPLE_FACTS),
    (["missing"], None),
    (["a"], SAMPLE_FACTS["a"]),
    (["a", "b", "c"], "value"),
])
def test_ansible_facts(
    sample_facts: AnsibleFacts,
    keys: list[str],
    expected: Any,
) -> None:
    assert sample_facts.get(*keys) == expected


def test_as_dict() -> None:
    inner = {
        "a": {"a1": "AA"},
        "b": {"b1": "BB"},
    }
    facts = AnsibleFacts({"dss_facts": inner})
    spec = {
        "MISSING": ("c",),
        "VA": ("a", "a1"),
        "VB": ("b", "b1"),
    }
    actual = facts.as_dict(spec)
    expected = {"VA": "AA", "VB": "BB"}
    assert expected == actual
