from datetime import datetime, timezone
from dataclasses import dataclass

from exasol.ds.sandbox.lib.aws_access.ami import Ami
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess


class FindAmiError(Exception):
    ...


@dataclass
class AmiFinder:
    aws_access: AwsAccess
    default_filters: dict[str, str]

    def _list(self, filters: dict[str, str]) -> list[Ami]:
        filter_list = [
            {"Name": key, "Values": [value]}
            for key, value in filters.items()
        ]
        return self.aws_access.list_amis(filters=filter_list)

    def unique(self, filters: dict[str, str]) -> Ami:
        amis = self._list(filters)
        if len(amis) == 1:
            return amis[0]
        prefix = "Found more than one" if amis else "Couldn't find any"
        raise FindAmiError(f"{prefix} AMI matching {filters}.")

    @property
    def latest(self) -> Ami:
        def as_datetime(value: str) -> datetime:
            if value.endswith("Z"):
                return datetime.fromisoformat(value[:-1]).replace(tzinfo=timezone.utc)
            return datetime.fromisoformat(value)

        amis = self._list(self.default_filters)
        if len(amis) < 1:
            raise FindAmiError(f"Couldn't find any AMI matching: {self.default_filters}")
        latest = max(amis, key=lambda ami: as_datetime(ami.creation_date))
        return latest

    def find(self, ami_id: str | None) -> Ami:
        if ami_id:
            return self.unique({"image-id": ami_id})
        return self.latest
