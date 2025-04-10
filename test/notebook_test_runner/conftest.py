import pytest


def pytest_addoption(parser):
    parser.addoption("--nb-test-file", action="store", help="Notebook test file nbtest_*.py")
    parser.addoption("--nb-test-backend", action="store", help="Backend to run the notebook test on")
    parser.addoption("--nb-test-db-mem-size", action="store", help="The Docker-DB memory size for the notebook tests",
                     default="4 GiB")


@pytest.fixture
def notebook_test_file(request):
    return request.config.getoption("--nb-test-file")


@pytest.fixture
def notebook_test_backend(request):
    return request.config.getoption("--nb-test-backend")


@pytest.fixture
def notebook_test_mem_size(request):
    return request.config.getoption("--nb-test-db-mem-size")
