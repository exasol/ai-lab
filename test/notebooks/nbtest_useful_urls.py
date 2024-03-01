import requests
from utils.useful_urls import UsefulURLs


def test_urls() -> None:

    bad_urls = []
    for url in UsefulURLs:
        try:
            response = requests.head(url.value, allow_redirects=True)
            if response.status_code >= 400:
                bad_urls.append(url.value)
        except requests.RequestException:
            bad_urls.append(url.value)

    assert not bad_urls, f"The following URL(s) are inaccessible {bad_urls}"
