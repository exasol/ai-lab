import os


def test_assert_working_directory():
    assert os.getcwd() == os.environ["NOTEBOOK_DEFAULTS"]


def test_assert_environ_nbtest_active():
    assert os.environ["NBTEST_ACTIVE"] == "TRUE"
