import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--nb_test_file", action="store", default="2", help="Notebook test file nbtest_*.py"
    )


@pytest.fixture
def nb_test_file(request):
    return int(request.config.getoption("--nb_test_file"))
