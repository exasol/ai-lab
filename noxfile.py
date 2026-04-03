import json
import shlex
from argparse import ArgumentParser, Namespace
from enum import Enum
from pathlib import Path
from typing import List, Optional

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


def _split_notebook_test_files(raw_test_file_value: str) -> List[str]:
    return [
        test_file
        for token in shlex.split(raw_test_file_value)
        for test_file in token.split()
        if test_file
    ]


def _merge_test_batch(batch: List[NBTestDescription]) -> NBTestDescription:
    base = batch[0]
    test_files: List[str] = []
    for test in batch:
        test_files.extend(_split_notebook_test_files(test.test_file))
    return NBTestDescription(
        name=f"SaaS notebook batch ({len(batch)} tests)",
        test_file=" ".join(test_files),
        test_backend=base.test_backend,
        wip=base.wip,
    )


def _batch_saas_tests_for_ci(tests: TestList) -> TestList:
    batches: List[List[NBTestDescription]] = []
    saas_batch_index_by_wip: dict[WipStatus, int] = {}

    for test in tests.tests:
        if test.test_backend != NBTestBackend.saas:
            batches.append([test])
            continue

        batch_index = saas_batch_index_by_wip.get(test.wip)
        if batch_index is None:
            batch_index = len(batches)
            batches.append([])
            saas_batch_index_by_wip[test.wip] = batch_index
        batches[batch_index].append(test)

    optimized_tests: List[NBTestDescription] = []
    for batch in batches:
        if len(batch) == 1:
            optimized_tests.append(batch[0])
        else:
            optimized_tests.append(_merge_test_batch(batch))
    return TestList(tests=optimized_tests)

@nox.session(name="get-notebook-tests", python=False)
def get_notebook_tests(session: nox.Session):
    """
    Filters notebook tests for test-status and test-classification and prints as JSON.
    """
    args = _parse_args(session)
    nb_tests = _get_tests_for_classification(args.test_classification)
    tests = nb_tests.stable if args.test_status == TestStatus.stable else nb_tests.unstable
    print(tests.model_dump_json())


@nox.session(name="get-notebook-tests-ci", python=False)
def get_notebook_tests_ci(session: nox.Session):
    """
    Same as get-notebook-tests, but groups SaaS tests into batches to reduce CI setup overhead.
    """
    args = _parse_args(session)
    nb_tests = _get_tests_for_classification(args.test_classification)
    tests = nb_tests.stable if args.test_status == TestStatus.stable else nb_tests.unstable
    print(_batch_saas_tests_for_ci(tests).model_dump_json())


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
