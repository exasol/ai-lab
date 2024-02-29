import nbformat
from nbclient import NotebookClient


def test_urls() -> None:

    nb = nbformat.read('utils/useful_urls.ipynb', as_version=4)

    # Add the following code at the end of the notebook
    test_code = '''
    def verify_all_urls():
        import requests
        bad_urls = []
        for url in UsefulURLs:
            try:
                response = requests.head(url.value, allow_redirects=True)
                if response.status_code >= 400:
                    bad_urls.append(url.value)
            except requests.RequestException:
                bad_urls.append(url.value)
        if bad_urls:
            raise RuntimeError(f"The following URL(s) are inaccessible {bad_urls}")
    verify_all_urls()
    '''
    nb.cells.append(nbformat.v4.new_code_cell(test_code))

    # Execute the notebook object, expecting to get no exceptions.
    nb_client = NotebookClient(nb, kernel_name='python3')
    nb_client.execute()
