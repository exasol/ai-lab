import logging
from dataclasses import dataclass

from exasol.ds.sandbox.lib.aws_access.ami import Ami
from exasol.ds.sandbox.lib.aws_access.aws_access import AwsAccess


@dataclass
class AmiFinder:
    aws_access: AwsAccess
    logger: logging.Logger

    def _list(self, filters: dict[str, str]) -> list[Ami]:
        filter_list = [
            {"Name": key, "Values": [value]}
            for key, value in filters.items()
        ]
        return self.aws_access.list_amis(filters=filter_list)

    def unique(self, filters: dict[str, str]) -> Ami | None:
        amis = self._list(filters)
        if len(amis) == 1:
            unique = amis[0]
            self.logger.info(f"Found unique AMI matching {filters}:\n{unique.name}")
            return unique
        prefix = "Found more than one" if amis else "Couldn't find any"
        self.logger.error(f"{prefix} AMI matching {filters}.")
        return None

    def latest(self, filters: dict[str, str]) -> Ami | None:
        amis = self._list(filters)
        if len(amis) < 1:
            self.logger.error(f"Couldn't find any AMI matching: {filters}")
            return None
        latest = max(amis, key=lambda ami: ami.creation_date)
        self.logger.info(f"Using source ami: '{latest.name}' from {latest.creation_date}")
        return latest
