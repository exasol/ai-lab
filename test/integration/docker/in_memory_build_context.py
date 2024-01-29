import io
import tarfile
import time


class InMemoryBuildContext:

    def __init__(self):
        super().__init__()
        self.fileobj = io.BytesIO()
        self._tar = tarfile.open(fileobj=self.fileobj, mode="x")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._tar.close()
        self.fileobj.seek(0)

    def __del__(self):
        self._tar.close()

    def add_string_to_file(self, name: str, string: str):
        self.add_bytes_to_file(name, string.encode("UTF-8"))

    def add_bytes_to_file(self, name: str, bytes: bytes):
        file_obj = io.BytesIO(bytes)
        self.add_fileobj_to_file(bytes, file_obj, name)

    def add_fileobj_to_file(self, bytes, file_obj, name):
        tar_info = tarfile.TarInfo(name=name)
        tar_info.mtime = time.time()
        tar_info.size = len(bytes)
        self._tar.addfile(tarinfo=tar_info, fileobj=file_obj)

    def add_host_path(self, host_path: str, path_in_tar: str, recursive: bool):
        self._tar.add(host_path, path_in_tar, recursive)

    def add_directory(self, name: str):
        tar_info = tarfile.TarInfo(name=name)
        tar_info.type = tarfile.DIRTYPE
        self._tar.addfile(tarinfo=tar_info)
