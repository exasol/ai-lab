import contextlib
import pytest
import subprocess

from exasol.ds.sandbox.runtime.ansible.roles.entrypoint.files import entrypoint


@pytest.fixture
def src_dir(tmp_path):
    """
    Create a source directory with sample sub-directories and files.
    """
    @contextlib.contextmanager
    def directory(dir):
        dir.mkdir()
        dir.chmod(0o700)
        yield dir

    def create_file(path):
        file = tmp_path / path
        file.write_text(f"content of file {file}")
        file.chmod(0o600)
        return file

    with directory(tmp_path / "src") as root:
        create_file(root / "a.txt")
        create_file(root / "b.txt")
        with directory(root / "sub") as sub:
            create_file(sub / "s1.txt")
            create_file(sub / "s2.txt")

    return root


def test_copy_rec(src_dir):
    print(f'\n{src_dir}')
    subprocess.run(["ls", "-lR", src_dir])
    root = src_dir.parent
    dst = root / "dst"
    entrypoint.copy_rec(src_dir, dst)
    subprocess.run(["ls", "-lR", dst])
