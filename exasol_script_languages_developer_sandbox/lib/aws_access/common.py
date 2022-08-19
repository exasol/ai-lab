from typing import Dict, Any


def get_value_safe(key: str, aws_object: Dict[str, Any], default: str = "n/a") -> str:
    """
    Returns an element from a dictionary, otherwise returns the given default value.
    """
    if key in aws_object:
        return aws_object[key]
    return default

