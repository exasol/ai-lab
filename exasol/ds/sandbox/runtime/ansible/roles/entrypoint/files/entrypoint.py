import argparse
import logging
import os
import re
import shutil
import subprocess
import sys
import time

from inspect import cleandoc
from pathlib import Path


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
        "--user", type=str,
        help="user name for running jupyter server",
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
        binary_path: str,
        notebook_dir: str,
        logfile: Path,
        user: str,
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
    with open(logfile, "w") as f:
        p = subprocess.Popen(command_line, stdout=f, stderr=f)

    success_message = cleandoc(f"""
        Server for Jupyter has been started successfully.
        You can connect with https://<ip address>:8888.
        If using a Docker daemon on your local machine then ip address is localhost.

        ┬ ┬┌─┐┌┬┐┌─┐┌┬┐┌─┐  ┬ ┬┌─┐┬ ┬┬─┐   ┬┬ ┬┌─┐┬ ┬┌┬┐┌─┐┬─┐  ┌─┐┌─┐┌─┐┌─┐┬ ┬┌─┐┬─┐┌┬┐ ┬
        │ │├─┘ ││├─┤ │ ├┤   └┬┘│ ││ │├┬┘   ││ │├─┘└┬┘ │ ├┤ ├┬┘  ├─┘├─┤└─┐└─┐││││ │├┬┘ ││ │
        └─┘┴  ─┴┘┴ ┴ ┴ └─┘   ┴ └─┘└─┘┴└─  └┘└─┘┴   ┴  ┴ └─┘┴└─  ┴  ┴ ┴└─┘└─┘└┴┘└─┘┴└──┴┘ o

        To update the password as user {user} run
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
            exit_on_error(p.wait(poll_sleep))
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


def sleep_inifinity():
    while True:
        time.sleep(1)


def main():
    args = arg_parser().parse_args()
    if args.notebook_defaults and args.notebooks:
        copy_rec(
            args.notebook_defaults,
            args.notebooks,
            args.warning_as_error,
        )
    if args.jupyter_server and args.notebooks and args.jupyter_logfile and args.user:
        start_jupyter_server(
            args.jupyter_server,
            args.notebooks,
            args.jupyter_logfile,
            args.user)
    else:
        sleep_inifinity()


if __name__ == "__main__":
    main()
