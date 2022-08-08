import tempfile
from pathlib import Path
from typing import Tuple

from exasol_script_languages_developer_sandbox.lib.ansible.ansible_access import AnsibleAccess
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_repository import AnsibleRepository
from exasol_script_languages_developer_sandbox.lib.ansible.ansible_runner import AnsibleRunner


class AnsibleContextManager:
    """
    Context manager which creates a temporary working directory where ansible files are stored.
    During creation, the content of all given ansible repositories is copied ot the temporary directory.
    Deletes the directory during cleanup.
    """

    def __init__(self, ansible_access: AnsibleAccess, repositories: Tuple[AnsibleRepository]):
        self._work_dir = None
        self._ansible_access = ansible_access
        self._ansible_repositories = repositories

    def __enter__(self):
        self._work_dir = tempfile.TemporaryDirectory()
        for repo in self._ansible_repositories:
            repo.copy_to(Path(self._work_dir.name))
        return AnsibleRunner(self._ansible_access, Path(self._work_dir.name))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._work_dir.cleanup()
        pass

