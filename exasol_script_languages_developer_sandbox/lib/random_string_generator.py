import base64
import uuid


def get_random_str_of_length_n(length: int) -> str:
    """
    Creates a random string of given length.
    """
    return get_random_str()[:length]


def get_random_str() -> str:
    """
    Creates a random string of length 22.
    Uses uuid.uuid4() as input for Base64,
    which replaces "+","/" with "A"/"B" and removes any filling characters ("=") and
    we use Base64 (and not for example hex) as it uses all alphanumerical characters.
    """
    return base64.b64encode(uuid.uuid4().bytes, altchars="AB".encode("utf-8")).decode("utf-8").replace('=', '')
