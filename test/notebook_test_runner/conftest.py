import pytest


def pytest_addoption(parser):
    parser.addoption("--nb-test-file", action="store", help="Notebook test file nbtest_*.py")


@pytest.fixture
def nb_test_file(request):
    return request.config.getoption("--nb-test-file")
