from pathlib import Path
import importlib_resources as ir
import exasol.ds.sandbox.runtime.ansible
from exasol.ds.sandbox.lib.logging import get_status_logger, LogType

LOG = get_status_logger(LogType.ANSIBLE)


class AnsibleRepository:

    def copy_to(self, target: Path) -> None:
        pass


class AnsibleResourceRepository(AnsibleRepository):
    """
    Represents a repository containing ansible files (roles, playbooks, tasks, etc.).
    The repository is expected to be located within a Python module.
    Supports copy of the ansible files to a target folder.
    """

    def __init__(self, package):
        self._package = package

    @staticmethod
    def copy_importlib_resources_file(src_file: ir.abc.Traversable, target_file: Path) -> None:
        """
        Uses a given source path "src_file" given as an importlib_resources.abc.Traversable to copy the file it points to
        into the destination denoted by target_path.
        :param src_file: Location of the file to be copied, given as importlib_resources.abc.Traversable.
        :param target_file: Path object the location file should be copied to.
        :raises RuntimeError if parameter target_file already exists.
        """
        if src_file.name == "__init__.py":
            LOG.debug(f"Ignoring {src_file} for repository.")
            return
        if target_file.exists():
            raise RuntimeError(f"Repository target: {target_file} already exists.")

        content = src_file.read_bytes()
        with open(target_file, "wb") as file:
            file.write(content)

    @staticmethod
    def copy_importlib_resources_dir_tree(src_path: ir.abc.Traversable, target_path: Path) -> None:
        """
        Uses a given source path "scr_path" given as an importlib_resources.abc.Traversable to copy all files/directories
        in the directory tree whose root is scr_path into target_path.
        :param src_path: Root of the dir tree to be copied, given as importlib_resources.abc.Traversable.
        :param target_path: Path object the dir tree should be copied to.
        :raises RuntimeError if parameter target_file already exists.
        """
        if not target_path.exists():
            target_path.mkdir()
        for file in src_path.iterdir():
            file_target = target_path / file.name
            if file.is_file():
                AnsibleResourceRepository.copy_importlib_resources_file(file, file_target)
            else:
                file_target.mkdir(exist_ok=True)
                AnsibleResourceRepository.copy_importlib_resources_dir_tree(file, file_target)

    def copy_to(self, target: Path) -> None:
        """
        Copies this repository recursively to target.
        If any file already exists on target, a RuntimeError is thrown.
        :param target: Path object the repository tree should be copied to.
        :raises RuntimeError if parameter target_file already exists.
        """
        source_path = ir.files(self._package)
        self.copy_importlib_resources_dir_tree(source_path, target)


default_repositories = (AnsibleResourceRepository(exasol.ds.sandbox.runtime.ansible),)
