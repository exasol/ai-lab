from argparse import ArgumentParser
from enum import Enum
from pathlib import Path
from typing import List

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


class TestSet(BaseModel):
    tests: List[NBTestDescription]


NOTEBOOKS_TESTS = {
    TestStatus.stable: TestSet(tests=[
        NBTestDescription(name="CSE notebook", test_file="nbtest_cloud.py", test_backend=NBTestBackend.on_prem,
                          wip=WipStatus.no_wip),
        NBTestDescription(name="sklearn notebook", test_file="nbtest_sklearn.py", test_backend=NBTestBackend.on_prem,
                          wip=WipStatus.no_wip),
        NBTestDescription(name="ibis notebook", test_file="nbtest_ibis.py", test_backend=NBTestBackend.on_prem,
                          wip=WipStatus.no_wip),
        NBTestDescription(name="SLC notebook", test_file="nbtest_script_languages_container.py",
                          test_backend=NBTestBackend.on_prem, wip=WipStatus.no_wip),
        # NBTestDescription(name="SME notebooks", test_file="nbtest_sagemaker.py", test_backend=NBTestBackend.on_prem,
        #                   wip=WipStatus.no_wip),
        # NBTestDescription(name="TE notebooks", test_file="nbtest_transformers.py", test_backend=NBTestBackend.on_prem,
        #                   wip=WipStatus.no_wip),
        NBTestDescription(name="short notebook tests", test_file="\"nbtest_environment_test.py nbtest_itde.py\"",
                          test_backend=NBTestBackend.empty, wip=WipStatus.no_wip), ]),
    TestStatus.unstable: TestSet(tests=[
        NBTestDescription(name="CSE notebook", test_file="nbtest_cloud.py", test_backend=NBTestBackend.saas,
                          wip=WipStatus.no_wip),
        NBTestDescription(name="sklearn", test_file="nbtest_sklearn.py", test_backend=NBTestBackend.saas,
                          wip=WipStatus.no_wip),
        NBTestDescription(name="ibis notebook", test_file="nbtest_ibis.py", test_backend=NBTestBackend.saas,
                          wip=WipStatus.no_wip),
        NBTestDescription(name="SME notebooks", test_file="nbtest_sagemaker.py", test_backend=NBTestBackend.saas,
                          wip=WipStatus.no_wip),
        NBTestDescription(name="TE notebooks", test_file="nbtest_transformers.py", test_backend=NBTestBackend.saas,
                          wip=WipStatus.no_wip),
        NBTestDescription(name="TXAIE notebooks", test_file="nbtest_text_ai.py", test_backend=NBTestBackend.saas,
                          wip=WipStatus.no_wip), ])
}

LARGE_NOTEBOOKS_TESTS = {
    TestStatus.stable: TestSet(tests=[
        NBTestDescription(name="TXAIE notebooks onprem", test_file="nbtest_text_ai.py",
                          test_backend=NBTestBackend.on_prem,
                          wip=WipStatus.no_wip), ]), TestStatus.unstable: TestSet(tests=[]),
}


@nox.session(name="get-notebook-tests", python=False)
def get_notebook_tests(session: nox.Session):
    """
    Validates the correctness of the given tag.
    """
    test_status_values = [ts.value for ts in TestStatus]
    test_classification_values = [ts.value for ts in TestClassification]

    parser = ArgumentParser(
        usage=f"nox -s {session.name} -- --test-status {{{','.join(test_status_values)}}} <--test-classification {{{','.join(test_classification_values)}}}>")
    parser.add_argument("--test-status", type=TestStatus, required=True, help="Test status", )
    parser.add_argument("--test-classification", type=TestClassification, default=TestClassification.normal.value,
                        help="Test classification", )
    args = parser.parse_args(session.posargs)
    nb_tests = NOTEBOOKS_TESTS if args.test_classification == TestClassification.normal else LARGE_NOTEBOOKS_TESTS
    test_set = nb_tests[args.test_status]
    print(test_set.model_dump_json())
