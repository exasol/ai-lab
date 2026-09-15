from __future__ import annotations

from pathlib import Path

from exasol.toolbox.config import BaseConfig
from pydantic import computed_field


class Config(BaseConfig):
    @computed_field  # type: ignore[misc]
    @property
    def has_documentation(self) -> bool:
        """
        Indicates that the project serves Sphinx-based documentation. With a few
        exceptions, this should be the case for most projects.

        This will be analyzed further in:
           https://github.com/exasol/ai-lab/issues/549
        """
        return False


PROJECT_CONFIG = BaseConfig(
    project_name="ds/sandbox",
    root_path=Path(__file__).parent,
    python_versions=("3.10",),
)
