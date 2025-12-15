from typing import Any


class DictAccessor:
    """
    Access values in a nested dictionary via key sequences.
    """

    def __init__(self, raw: dict[str, Any], prefixes: list[str]|None = None):
        self._raw = raw
        self.prefixes = prefixes or []

    def _nested(self, *keys: str) -> Any:
        current = self._raw
        for key in keys:
            if key not in current:
                return None
            current = current[key]  # type: ignore
        return current

    def get(self, *keys: str) -> Any:
        return self._nested(*self.prefixes, *keys)

    def as_dict(
        self,
        spec: dict[str, tuple[str, ...]],
    ) -> dict[str, Any]:
        """
        Parameter ``spec`` maps output entries to a tuple of access keys.
        Each output entry is a string, while the access keys is tuple of keys
        to access the nested entries.

        spec = { "output-entry": ("key-1", "key-2") }

        Method as_dict() returns the the dict with the access keys being
        replaced by the value retrieved from the entries. If None is returned
        for a key tuple, then the output-entry is missing in the resulting
        dict.

        Here is an example:

        spec = {"E1": ("a", "b"), "E2": ("a", "c")}
        DictAccessor({"a": {"b": "value"}}).as_dict(spec)

        will return {"E1": "value"}
        """
        return {
            entry: value for entry, keys in spec.items()
            if (value := self.get(*keys))
        }
