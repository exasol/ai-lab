import pytest


def pytest_addoption(parser):
    parser.addoption("--nb-test-file", action="store", help="Notebook test file nbtest_*.py")
    parser.addoption("--nb-test-backend", action="store", help="Backend to run the notebook test on")
    parser.addoption("--nb-test-db-mem-size", action="store", help="The Docker-DB memory size for the notebook tests",
                     default="4 GiB")
    parser.addoption("--nb-test-with-gpu", action="store_true", help="Runs the notebook test with a Docker-DB with a GPU device attached.",
                     default=False)


@pytest.fixture
def notebook_test_file(request):
    return request.config.getoption("--nb-test-file")


@pytest.fixture
def notebook_test_backend(request):
    return request.config.getoption("--nb-test-backend")


@pytest.fixture
def notebook_test_mem_size(request):
    return request.config.getoption("--nb-test-db-mem-size")


@pytest.fixture
def notebook_test_with_gpu(request) -> bool:
    return request.config.getoption("--nb-test-with-gpu")
