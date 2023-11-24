import pytest

from exasol.ds.sandbox.lib.dss_docker.create_image import (
    DssDockerImage,
    DSS_VERSION,
)


@pytest.fixture
def sample_repo():
    return "avengers/tower"


def test_constructor_defaults(sample_repo):
    testee = DssDockerImage(sample_repo)
    assert testee.image_name == f"{sample_repo}:{DSS_VERSION}"
    assert testee.publish == False
    assert testee.keep_container == False


def test_constructor(sample_repo):
    version = "1.2.3"
    testee = DssDockerImage(
        repository=sample_repo,
        version=version,
        publish=True,
        keep_container=True,
    )
    assert testee.image_name == f"{sample_repo}:{version}"
    assert testee.publish == True
    assert testee.keep_container == True


@pytest.mark.parametrize(
    "facts",
    [
        {},
        {"other": "other value"},
        {"dss_ansible_facts": {}},
        {"dss_ansible_facts": {"b": {}}},
     ])
def test_fact_empty(facts):
    assert DssDockerImage._get_fact(facts, "a", "b", "c") is None


def test_fact_found():
    facts = {"dss_ansible_facts": {"b": {"c": "expected"}}}
    assert DssDockerImage._get_fact(facts, "b", "c") == "expected"


@pytest.mark.parametrize(
    "facts",
    [
        {},
        {"key": "value"},
        {"dss_ansible_facts": {}},
        {"dss_ansible_facts": {"key": "value"}},
     ])
def test_entrypoint_default(facts):
    assert DssDockerImage._entrypoint(facts) == ["sleep", "infinity"]


def test_entrypoint_with_copy_args():
    entrypoint = "/path/to/entrypoint.py"
    defaults = "/path/to/defaults"
    final = "/path/to/final"
    facts = {
        "dss_ansible_facts": {
            "entrypoint": entrypoint,
            "notebook_folder": {
                "defaults": defaults,
                "final": final,
            }}}
    assert DssDockerImage._entrypoint(facts) == [
        "python3",
        entrypoint,
        "--copy-from", defaults,
        "--copy-to", final,
        "--jupyter-server",
    ]
