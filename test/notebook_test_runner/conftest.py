import pytest


def pytest_addoption(parser):
    parser.addoption("--nb-test-file", action="store", help="Notebook test file nbtest_*.py")
    parser.addoption("--nb-test-backend", action="store", help="Backend to run the notebook test on")


@pytest.fixture
def notebook_test_file(request):
    return request.config.getoption("--nb-test-file")


@pytest.fixture
def notebook_test_backend(request):
    return request.config.getoption("--nb-test-backend")
