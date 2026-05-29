from functools import lru_cache
from pathlib import Path

from git import Repo


@lru_cache(maxsize=1)
def get_repo_root() -> Path:
    repo = Repo(Path(__file__).resolve(), search_parent_directories=True)
    if repo.working_tree_dir is None:
        raise RuntimeError("Unable to determine repository root")
    return Path(repo.working_tree_dir)
