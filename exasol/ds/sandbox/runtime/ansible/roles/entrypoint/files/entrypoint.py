import argparse
import logging
import grp
import os
import pwd
import re
import resource
import shutil
import subprocess
import stat
import sys
import time

from inspect import cleandoc
from pathlib import Path
from typing import List, TextIO


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(asctime)s %(levelname)-7s %(filename)s: %(message)s",
    datefmt="%Y-%m-%d %X",
)


def arg_parser():
    parser = argparse.ArgumentParser(
        description="entry point for docker container",
    )
    parser.add_argument(
        "--notebook-defaults", type=Path,
        help="copy notebook files from this directory",
    )
    parser.add_argument(
        "--notebooks", type=Path,
        help="destination location for notebook files to copy",
    )
    parser.add_argument(
        "--jupyter-server", metavar="<PATH-TO-JUPYTER-BINARY>",
        help="start server for Jupyter notebooks",
    )
    parser.add_argument(
        "--port", type=int,
        help="IP port Jupyter server is listening to",
    )
    parser.add_argument(
        "--user", type=str,
        help="user name for running jupyter server",
    )
    parser.add_argument(
        "--group", type=str,
        help="user group for running jupyter server",
    )
    parser.add_argument(
        "--docker-group", type=str,
        help="user group for accessing Docker socket",
    )
    parser.add_argument(
        "--home", type=str,
        help="home directory of user running jupyter server",
    )
    parser.add_argument(
        "--password", type=str,
        help="initial default password for Jupyter server",
    )
    parser.add_argument(
        "--jupyter-logfile", type=Path,
        help="path to write Jupyter server log messages to",
    )
    parser.add_argument(
        "--warning-as-error", action="store_true",
        help="treat warning as error",
    )
    return parser


def start_jupyter_server(
        home_directory: str,
        binary_path: str,
        port: int,
        notebook_dir: str,
        logfile: Path,
        user: str,
        password: str,
        poll_sleep: float = 1,
):
    """
    :param poll_sleep: specifies the waiting time in seconds before reading
    a line from the logfile.
    """
    def exit_on_error(rc):
        if rc is not None and rc != 0:
            log_messages = logfile.read_text()
            _logger.error(
                f"Jupyter Server terminated with error code {rc},"
                f" Logfile {logfile} contains:\n{log_messages}",
            )
            sys.exit(rc)

    command_line = [
        binary_path,
        f"--notebook-dir={notebook_dir}",
        "--no-browser",
        "--allow-root",
    ]

    env = os.environ.copy()
    env["HOME"] = home_directory
    with open(logfile, "w") as f:
        p = subprocess.Popen(command_line, stdout=f, stderr=f, env=env)

    url = "http://<host>:<port>"
    localhost_url = url.replace("<host>", "localhost").replace("<port>", str(port))
    success_message = cleandoc(f"""
        Server for Jupyter has been started successfully.

        You can connect with {url}.

        If using a Docker daemon on your local machine and you forward the
        port to the same port then you can connect with {localhost_url}.

        ┬ ┬┌─┐┌┬┐┌─┐┌┬┐┌─┐  ┬ ┬┌─┐┬ ┬┬─┐   ┬┬ ┬┌─┐┬ ┬┌┬┐┌─┐┬─┐  ┌─┐┌─┐┌─┐┌─┐┬ ┬┌─┐┬─┐┌┬┐ ┬
        │ │├─┘ ││├─┤ │ ├┤   └┬┘│ ││ │├┬┘   ││ │├─┘└┬┘ │ ├┤ ├┬┘  ├─┘├─┤└─┐└─┐││││ │├┬┘ ││ │
        └─┘┴  ─┴┘┴ ┴ ┴ └─┘   ┴ └─┘└─┘┴└─  └┘└─┘┴   ┴  ┴ └─┘┴└─  ┴  ┴ ┴└─┘└─┘└┴┘└─┘┴└──┴┘ o

        The default password is "{password}".
        To update the password, log in to the Docker container as the user {user} and run
            {binary_path} server password
    """)
    with open(logfile, "r") as f:
        regexp = re.compile("Jupyter Server .* is running at:")
        while True:
            time.sleep(poll_sleep)
            line = f.readline()
            if re.search(regexp, line):
                _logger.info(success_message)
                break
            exit_on_error(p.poll())
        exit_on_error(p.wait())


def copy_rec(src: Path, dst: Path, warning_as_error: bool = False):
    """
    Copy files and directories missing in dst from src and set
    permission 666 for files and 777 for directories.
    If directory src does not exit then do not copy anything.
    """
    def ensure_dir(dir: Path):
        if not dir.exists():
            dir.mkdir()
            dir.chmod(0o777)

    def ensure_file(src: Path, dst: Path):
        if not dst.exists():
            shutil.copyfile(src, dst)
            dst.chmod(0o666)

    if not src.exists():
        msg = f"Source directory not found: {src}"
        if warning_as_error:
            raise RuntimeError(msg)
        else:
            _logger.warning(msg)
        return
    ensure_dir(dst)
    for root, dirs, files in os.walk(src):
        root = Path(root)
        copy = dst / root.relative_to(src)
        for name in files:
            ensure_file(root / name, copy / name)
        for name in dirs:
            ensure_dir(copy / name)


def disable_core_dumps():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    _logger.info("Disabled coredumps")


def sleep_infinity():
    while True:
        time.sleep(1)


class Group:
    def __init__(self, name: str, id: int = None):
        self.name = name
        self._id = id

    @property
    def id(self):
        if self._id is None:
            self._id = grp.getgrnam(self.name).gr_gid
        return self._id

    def __eq__(self, other) -> bool:
        if not isinstance(other, Group):
            return False
        return other.name == self.name

    def __repr__(self):
        return f"Group(name='{self.name}', id={self._id})"


class FileInspector:
    def __init__(self, path: Path):
        self._path = path
        self._stat = path.stat() if path.exists() else None

    @property
    def group_id(self) -> int:
        if self._stat is None:
            raise FileNotFoundError(self._path)
        return self._stat.st_gid

    def is_group_accessible(self) -> bool:
        if self._stat is None:
            _logger.debug(f"File not found {self._path}")
            return False
        permissions = stat.filemode(self._stat.st_mode)
        if permissions[4:6] == "rw":
            return True
        raise PermissionError(
            "No rw permissions for group in"
            f" {permissions} {self._path}."
        )


class GroupAccess:
    """
    If there is already a group with group-ID `gid`, then add the user to
    this group, otherwise change the group ID to `gid` for the specified group
    name.  The other group is expected to exist already and user to be added
    to it.
    """
    def __init__(self, user: str, group: Group):
        self._user = user
        self._group = group

    def _find_group_name(self, id: int) -> str:
        try:
            return grp.getgrgid(id).gr_name
        except KeyError:
            return None

    def _run(self, command: str) -> int:
        _logger.debug(f"Executing {command}")
        return subprocess.run(command.split()).returncode

    def enable(self) -> Group:
        gid = self._group.id
        existing = self._find_group_name(gid)
        if existing:
            self._run(f"usermod --append --groups {existing} {self._user}")
            return Group(existing, gid)
        else:
            self._run(f"groupmod -g {gid} {self._group.name}")
            return self._group


class User:
    def __init__(self, user_name: str, group: Group, docker_group: Group):
        self.name = user_name
        self._id = None
        self.group = group
        self.docker_group = docker_group

    @property
    def is_specified(self) -> bool:
        return bool(
            self.name
            and self.group.name
            and self.docker_group.name
        )

    @property
    def id(self):
        if self._id is None:
            self._id = pwd.getpwnam(self.name).pw_uid
        return self._id

    def chown_rec(self, path: Path):
        uid = self.id
        gid = self.group.id
        os.chown(path, uid, gid)
        for root, dirs, files in os.walk(path):
            root = Path(root)
            for name in files:
                os.chown(root / name, uid, gid)
            for name in dirs:
                os.chown(root / name, uid, gid)
        _logger.info(f"Did chown -R {self.name}:{self.group.name} {path}")

    def enable_group_access(self, path: Path):
        file = FileInspector(path)
        if file.is_group_accessible():
            group = GroupAccess(
                self.name,
                Group(self.docker_group.name, file.group_id),
            ).enable()
            os.setgroups([group.id])
            self.docker_group = group
            _logger.info(f"Enabled access to {path}")
        return self

    def switch_to(self):
        gid = self.group.id
        uid = self.id
        os.setresgid(gid, gid, gid)
        os.setresuid(uid, uid, uid)
        _logger.debug(
            f"uid = {os.getresuid()}"
            f" gid = {os.getresgid()}"
            f" extra groups = {os.getgroups()}"
        )
        _logger.info(f"Switched uid/gid to {self.name}/{self.group.name}")
        return self


def main():
    args = arg_parser().parse_args()
    user = User(args.user, Group(args.group), Group(args.docker_group))
    if user.is_specified:
        if args.notebooks:
            user.chown_rec(args.notebooks)
        user.enable_group_access(Path("/var/run/docker.sock")).switch_to()
    if args.notebook_defaults and args.notebooks:
        copy_rec(
            args.notebook_defaults,
            args.notebooks,
            args.warning_as_error,
        )
        _logger.info(
            "Copied notebooks from"
            f" {args.notebook_defaults} to {args.notebooks}")
    disable_core_dumps()
    if (args.jupyter_server
        and args.notebooks
        and args.jupyter_logfile
        and args.user
        and args.home
        and args.password
        ):
        start_jupyter_server(
            args.home,
            args.jupyter_server,
            args.port,
            args.notebooks,
            args.jupyter_logfile,
            args.user,
            args.password,
        )
    else:
        sleep_infinity()


if __name__ == "__main__":
    main()
