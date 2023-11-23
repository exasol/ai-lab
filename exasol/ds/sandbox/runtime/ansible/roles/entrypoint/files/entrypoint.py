import argparse
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
        "--copy-from", action="append", type=Path, metavar="<SRC>",
        help="""Copy files recursively with permissions.
        For each option --copy-from there must be corresponding option --copy-to.""",
    )
    parser.add_argument(
        "--copy-to", action="append", type=Path, metavar="<DEST>",
        help="destination location for file to copy",
    )
    parser.add_argument(
        "--jupyter-server", action="store_true",
        help="start server for Jupyter notebooks",
    )
    parser.add_argument(
        "--sleep", action="store_true",
        help="keep script running infinitly",
    )
    return parser


def start_jupyter_server():
    subprocess.run([
        "/root/jupyterenv/bin/jupyter-lab",
        "--notebook-dir=/root/notebooks",
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
    permission 644 for files and 755 for directories.
    If directory src does not exit then do not copy anything.
    """
    if not src.exists() or dst.exists():
        return

    if src.is_file():
        shutil.copyfile(src, dst)
        dst.chmod(0o644)
        return

    dst.mkdir()
    dst.chmod(0o755)
    for sf in src.iterdir():
        copy_rec(sf, dst / sf.name)


def main():
    args = arg_parser().parse_args()
    if args.copy_from and args.copy_to:
        nfrom = len(args.copy_from)
        nto = len(args.copy_to)
        if nfrom != nto:
            raise RuntimeError(
                "Found CLI option"
                f" --copy-from {nfrom} times and"
                f" --copy-to {nto} times, but"
                " number must be identical."
            )
        for copy in zip(args.copy_from, args.copy_to):
            copy_rec(*copy)
    if args.jupyter_server:
        start_jupyter_server()
    if args.sleep:
        while True:
            time.sleep(0.2)


if __name__ == "__main__":
    main()
