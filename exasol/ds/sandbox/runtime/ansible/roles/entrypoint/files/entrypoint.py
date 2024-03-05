import argparse
import logging
import grp
import os
import pwd
import re
import resource
import shutil
import subprocess
import sys
import time

from inspect import cleandoc
from pathlib import Path
from typing import List, TextIO


_logger = logging.getLogger(__name__)


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
            print(
                f"Jupyter Server terminated with error code {rc},"
                f" Logfile {logfile} contains:\n{log_messages}",
                flush=True,
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
                print(success_message, flush=True)
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


def sleep_infinity():
    while True:
        time.sleep(1)


class Group:
    def __init__(self, name: str):
        self.name = name
        self._id = None

    @property
    def id(self):
        if self._id is None:
            self._id = grp.getgrnam(self.name).gr_gid
        return self._id


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
    def uid(self):
        if self._id is None:
            self._id = pwd.getpwnam(self.name).pw_uid
        return self._id

    def own(self, path: str):
        if Path(path).exists():
            unchanged_uid = -1
            os.chown(path, unchanged_uid, self.docker_group.id)
        return self

    def switch_to(self):
        uid = self.uid
        os.setresuid(uid, uid, uid)
        gid = self.group.id
        os.setresgid(gid, gid, gid)
        os.setgroups([self.docker_group.id])
        return self


def main():
    args = arg_parser().parse_args()
    user = User(args.user, Group(args.group), Group(args.docker_group))
    if user.is_specified:
        user.own("/var/run/docker.sock").switch_to()
    if args.notebook_defaults and args.notebooks:
        copy_rec(
            args.notebook_defaults,
            args.notebooks,
            args.warning_as_error,
        )
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
