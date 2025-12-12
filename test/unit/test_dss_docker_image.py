from datetime import datetime
from typing import Dict, List
from unittest.mock import MagicMock, Mock, create_autospec, patch

import pytest

from exasol.ds.sandbox.lib.ansible.ansible_run_context import AnsibleRunContext
from exasol.ds.sandbox.lib.ansible.facts import AnsibleFacts
from exasol.ds.sandbox.lib.config import AI_LAB_VERSION
from exasol.ds.sandbox.lib.dss_docker import create_image, DockerRegistry
from exasol.ds.sandbox.lib.dss_docker.create_image import DssDockerImage


@pytest.fixture
def sample_repo():
    return "avengers/tower"


def test_constructor_defaults(sample_repo):
    testee = DssDockerImage(sample_repo)
    assert testee.image_name == f"{sample_repo}:{AI_LAB_VERSION}"
    assert testee.keep_container == False
    assert testee.work_in_progress_notebooks == False


def test_constructor(sample_repo):
    version = "1.2.3"
    testee = DssDockerImage(
        repository=sample_repo,
        version=version,
        keep_container=True,
        work_in_progress_notebooks=True
    )
    assert testee.image_name == f"{sample_repo}:{version}"
    assert testee.keep_container == True
    assert testee.work_in_progress_notebooks == True


def test_entrypoint_with_copy_args():
    raw_facts = {
        "dss_facts": {
            "docker_group": "docker-group-name",
            "jupyter": {
                "virtualenv": "/home/jupyter/jupyterenv",
                "server": "/home/jupyter/jupyterenv/bin/jupyter-lab",
                "core": "/home/jupyter/jupyterenv/bin/jupyter",
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
    facts = AnsibleFacts(raw_facts)

    def fact(*args):
        return facts.get(*args)

    expected_args = [
        "sudo",
        "--preserve-env=JUPYTER_PASSWORD",
        "python3",
        fact("entrypoint"),
    ]
    expected_kwargs = {
        "--docker-group": fact("docker_group"),
        "--notebook-defaults": fact("notebook_folder", "initial"),
        "--notebooks": fact("notebook_folder", "final"),
        "--home": fact("jupyter", "home"),
        "--venv": fact("jupyter", "virtualenv"),
        "--jupyter-server": fact("jupyter", "server"),
        "--jupyter-core": fact("jupyter", "core"),
        "--port": fact("jupyter", "port"),
        "--user": fact("jupyter", "user"),
        "--group": fact("jupyter", "group"),
        "--password": fact("jupyter", "password"),
        "--jupyter-logfile": fact("jupyter", "logfile"),
    }
    actual = create_image.build_entrypoint(facts)

    def as_dict(lst: List[str]) -> Dict[str, str]:
        return {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}

    n = len(expected_args)
    assert expected_args == actual[:n]
    assert expected_kwargs == as_dict(actual[n:])


def create_testee() -> DssDockerImage:
    testee = DssDockerImage("org/sample_repo", "version")
    return testee


@pytest.fixture
def mocked_docker_image() -> DssDockerImage:
    testee = create_testee()
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


@patch("exasol.ds.sandbox.lib.dss_docker.create_image.run_install_dependencies")
def test_work_in_progress_notebooks(mocked_run_install_dependencies: Mock,
                                    mocked_docker_image: DssDockerImage):
    testee = mocked_docker_image
    testee._install_dependencies = create_testee()._install_dependencies
    testee.create()
    assert len(mocked_run_install_dependencies.mock_calls) == 1
    ansible_run_context = mocked_run_install_dependencies.mock_calls[0].kwargs["ansible_run_context"]
    assert isinstance(ansible_run_context, AnsibleRunContext)
    assert ansible_run_context.extra_vars["work_in_progress_notebooks"] == False
