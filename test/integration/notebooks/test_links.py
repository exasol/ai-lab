from notebook_test_utils import verify_links_for_directory


def test_all_notebooks() -> None:

    missing_links = verify_links_for_directory()
    assert not missing_links
