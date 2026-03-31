import json
from argparse import ArgumentParser, Namespace
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Tuple

import yaml
from pydantic import BaseModel

import nox

ROOT = Path(__file__).parent

# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = []


class TestStatus(Enum):
    stable = "stable"
    unstable = "unstable"


class TestClassification(Enum):
    normal = "normal"
    large = "large"
    gpu = "gpu"


class WipStatus(Enum):
    wip = "wip"
    no_wip = "no-wip"


class NBTestBackend(Enum):
    on_prem = "onprem"
    saas = "saas"
    empty = ""


class NBTestDescription(BaseModel):
    """
    Description of a notebook test. 
    """
    name: str
    test_file: str
    test_backend: NBTestBackend
    wip: WipStatus

class TestList(BaseModel):
    tests: List[NBTestDescription]

class TestSets(BaseModel):
    stable: TestList
    unstable: TestList
    runner: str
    additional_pytest_parameters: Optional[str]

class TestRepository(BaseModel):
    normal: TestSets
    large: TestSets
    gpu: TestSets

def _load_test_repository() -> TestRepository:
    yaml_file_path = Path('nb_tests.yaml')
    with open(yaml_file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)
        return TestRepository(**yaml_data)



def _parse_args(session: nox.Session) -> Namespace:
    test_status_values = [ts.value for ts in TestStatus]
    test_classification_values = [ts.value for ts in TestClassification]
    test_status_values_str = ", ".join(test_status_values)
    test_classification_values_str = ", ".join(test_classification_values)
    usage = " ".join([
        "nox",
        "-s",
        session.name,
        "--",
        "--test-status",
        "{" + test_status_values_str + "}",
        "[",
        "--test-classification",
        "{" + test_classification_values_str + "}",
        "]"
    ])

    parser = ArgumentParser(usage=usage)
    parser.add_argument("--test-status", type=TestStatus, required=True, help="Test status", )
    parser.add_argument("--test-classification", type=TestClassification, default=TestClassification.normal.value,
                        help="Test classification", )
    args = parser.parse_args(session.posargs)
    return args

def _get_tests_for_classification(test_classification: TestClassification) -> TestSets:
    test_repository = _load_test_repository()
    mapping = {
        test_classification.normal: test_repository.normal,
        test_classification.large: test_repository.large,
        test_classification.gpu: test_repository.gpu,
    }
    return mapping[test_classification]


def _group_notebook_tests(tests: TestList) -> TestList:
    """
    Group notebook tests that share the same backend and WIP image so they can
    run in a single CI job while preserving coverage.
    """
    grouped: Dict[Tuple[NBTestBackend, WipStatus], List[NBTestDescription]] = {}
    group_order: List[Tuple[NBTestBackend, WipStatus]] = []

    for test in tests.tests:
        key = (test.test_backend, test.wip)
        if key not in grouped:
            grouped[key] = []
            group_order.append(key)
        grouped[key].append(test)

    merged: List[NBTestDescription] = []
    for key in group_order:
        group = grouped[key]
        if len(group) == 1:
            merged.append(group[0])
            continue

        backend, wip = key
        merged.append(
            NBTestDescription(
                name=" + ".join(test.name for test in group),
                test_file=" ".join(test.test_file for test in group),
                test_backend=backend,
                wip=wip,
            )
        )

    return TestList(tests=merged)

@nox.session(name="get-notebook-tests", python=False)
def get_notebook_tests(session: nox.Session):
    """
    Filters notebook tests for test-status and test-classification and prints as JSON.
    """
    args = _parse_args(session)
    nb_tests = _get_tests_for_classification(args.test_classification)
    tests = nb_tests.stable if args.test_status == TestStatus.stable else nb_tests.unstable
    print(_group_notebook_tests(tests).model_dump_json())


@nox.session(name="get-runner", python=False)
def get_runner(session: nox.Session):
    """
    Filters runner for test-status and test-classification and prints to stdout.
    """
    args = _parse_args(session)
    nb_tests = _get_tests_for_classification(args.test_classification)
    print(nb_tests.runner)


@nox.session(name="get-additional-pytest-parameter", python=False)
def get_additional_pytest_parameter(session: nox.Session):
    """
    Filters additional pytest parameters for test-status and test-classification and prints to stdout.
    """
    args = _parse_args(session)
    nb_tests = _get_tests_for_classification(args.test_classification)
    if nb_tests.additional_pytest_parameters:
        print(nb_tests.additional_pytest_parameters)