from __future__ import annotations

from pathlib import Path

from exasol.toolbox.config import BaseConfig


PROJECT_CONFIG = BaseConfig(
    project_name="ds/sandbox",
    root_path=Path(__file__).parent,
    python_versions=("3.10", "3.11", "3.12"),
)
