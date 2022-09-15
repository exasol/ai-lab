from typing import Any, cast
from unittest.mock import Mock


def mock_cast(obj: Any) -> Mock:
    return cast(Mock, obj)
