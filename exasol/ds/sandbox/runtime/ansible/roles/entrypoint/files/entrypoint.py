import argparse
import os
import shutil
import subprocess
import time

from inspect import cleandoc
from pathlib import Path


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
    return parser


def start_jupyter_server(binary_path: str, notebook_dir: str):
    subprocess.run([
        binary_path,
        f"--notebook-dir={notebook_dir}",
        "--no-browser",
        "--allow-root",
    ])
    print(cleandoc(
        """
        Server for Jupyter has been started.
        You can connect with https://localhost:8888
        """))


def copy_rec(src: Path, dst: Path):
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
        copy_rec(args.notebook_defaults, args.notebooks)
    if args.jupyter_server and args.notebooks:
        start_jupyter_server(args.jupyter_server, args.notebooks)
    else:
        sleep_inifinity()


if __name__ == "__main__":
    main()
