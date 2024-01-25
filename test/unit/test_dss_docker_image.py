import pytest

from unittest.mock import MagicMock, Mock, create_autospec
from datetime import datetime
from exasol.ds.sandbox.lib.dss_docker import create_image, DockerRegistry
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
    assert testee.keep_container == False


def test_constructor(sample_repo):
    version = "1.2.3"
    testee = DssDockerImage(
        repository=sample_repo,
        version=version,
        keep_container=True,
    )
    assert testee.image_name == f"{sample_repo}:{version}"
    assert testee.keep_container == True


@pytest.mark.parametrize(
    "testee",
    [
        {},
        {"key": "sample value"},
     ])
def test_nested_value_missing_entry(testee):
    assert create_image.get_nested_value(testee, "missing_entry") == None
    assert create_image.get_nested_value(testee, "key", "key-2") == None


def test_nested_value_level_2():
    testee = {"key": {"key-2": "value"}}
    assert create_image.get_nested_value(testee, "key", "key-2") == "value"


@pytest.mark.parametrize(
    "facts",
    [
        {},
        {"other": "other value"},
        {"dss_facts": {}},
        {"dss_facts": {"b": {}}},
     ])
def test_fact_empty(facts):
    assert create_image.get_fact(facts, "a", "b", "c") is None


def test_fact_found():
    facts = {"dss_facts": {"b": {"c": "expected"}}}
    assert create_image.get_fact(facts, "b", "c") == "expected"


@pytest.mark.parametrize(
    "facts",
    [
        {},
        {"key": "value"},
        {"dss_facts": {}},
        {"dss_facts": {"key": "value"}},
     ])
def test_entrypoint_default(facts):
    assert create_image.entrypoint(facts) == ["sleep", "infinity"]


def test_entrypoint_with_copy_args():
    jupyter = "/root/jupyterenv/bin/jupyter-lab"
    entrypoint = "/path/to/entrypoint.py"
    initial = "/path/to/initial"
    final = "/path/to/final"
    user = "jupyter-user-name"
    password = "jupyter-default-password"
    logfile = "/path/to/jupyter-server.log"
    facts = {
        "dss_facts": {
            "jupyter": {
                "command": jupyter,
                "user": user,
                "password": password,
                "logfile": logfile,
            },
            "entrypoint": entrypoint,
            "notebook_folder": {
                "initial": initial,
                "final": final,
            }}}
    assert create_image.entrypoint(facts) == [
        "python3",
        entrypoint,
        "--notebook-defaults", initial,
        "--notebooks", final,
        "--jupyter-server", jupyter,
        "--user", user,
        "--password", password,
        "--jupyter-logfile", logfile,
    ]

@pytest.fixture
def mocked_docker_image():
    testee = DssDockerImage("org/sample_repo", "version")
    testee._start = datetime.now()
    testee._start_container = MagicMock()
    testee._install_dependencies = MagicMock()
    testee._cleanup = MagicMock()
    image = Mock(attrs={"Size": 1025})
    testee._commit_container = MagicMock(return_value=image)
    return testee


def test_push_called(mocker, mocked_docker_image):
    testee = mocked_docker_image
    testee.registry = create_autospec(DockerRegistry)
    testee.create()
    assert testee.registry.push.called
    expected = mocker.call(testee.repository, testee.version)
    assert testee.registry.push.call_args == expected
