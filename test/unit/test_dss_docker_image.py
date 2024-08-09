import pytest

from unittest.mock import MagicMock, Mock, create_autospec
from datetime import datetime
from exasol.ds.sandbox.lib.dss_docker import create_image, DockerRegistry
from exasol.ds.sandbox.lib.config import AI_LAB_VERSION
from exasol.ds.sandbox.lib.dss_docker.create_image import DssDockerImage
from typing import Dict, List

@pytest.fixture
def sample_repo():
    return "avengers/tower"


def test_constructor_defaults(sample_repo):
    testee = DssDockerImage(sample_repo)
    assert testee.image_name == f"{sample_repo}:{AI_LAB_VERSION}"
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
    facts = {
        "dss_facts": {
            "docker_group": "docker-group-name",
            "jupyter": {
                "command": "/home/jupyter/jupyterenv/bin/jupyter-lab",
                "port": "port",
                "user": "jupyter-user-name",
                "group": "jupyter-group-name",
                "home": "/home/user",
                "password": "jupyter-default-password",
                "logfile": "/path/to/jupyter-server.log",
            },
            "entrypoint": "/path/to/entrypoint.py",
            "notebook_folder": {
                "initial": "/path/to/initial",
                "final": "/path/to/final",
            }}}

    def fact(*args):
        return create_image.get_fact(facts, *args)

    expected = {
        "--docker-group": fact("docker_group"),
        "--notebook-defaults": fact("notebook_folder", "initial"),
        "--notebooks": fact("notebook_folder", "final"),
        "--home": fact("jupyter", "home"),
        "--jupyter-server": fact("jupyter", "command"),
        "--port": fact("jupyter", "port"),
        "--user": fact("jupyter", "user"),
        "--group": fact("jupyter", "group"),
        "--password": fact("jupyter", "password"),
        "--jupyter-logfile": fact("jupyter", "logfile"),
    }
    actual = create_image.entrypoint(facts)

    def as_dict(lst: List[str]) -> Dict[str, str]:
        return { lst[i]: lst[i + 1] for i in range(0, len(lst), 2) }

    assert [ "sudo", "python3", fact("entrypoint") ] == actual[:3] \
        and expected == as_dict(actual[3:])


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
    expected = [
        mocker.call(testee.repository, testee.version),
        mocker.call(testee.repository, "latest"),
    ]
    assert testee.registry.push.call_args_list == expected


@pytest.mark.parametrize(
    "env, expected", (
        ( ["A=1"], "jupyterenv/bin"),
        ( ["A=1", "PATH=a:b:c"], "a:b:c:jupyterenv/bin"),
    )
)
def test_path(sample_repo, env, expected):
    testee = DssDockerImage(sample_repo)
    container = Mock(attrs={"Config": {"Env": env}})
    assert expected == testee._path(container, "jupyterenv/bin")
