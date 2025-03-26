"""Module for manipulating files."""

from enum import Enum
from typing import Union

from pydantic import BaseModel
from git import Repo

from src.utils.terminal import display_warning


class FileType(Enum):
    """File type enum"""

    UNTRACKED = "untracked"
    MODIFIED = "modified"


class File(BaseModel):
    """File class"""

    name: str
    content: str
    type: FileType


def load_untracked_files(repo: Repo) -> list[File]:
    """Load untracked files from the given repository.

    Args:
        repo (Repo): Current git repository.

    Returns:
        list[File]: A collection of all untracked files."""
    files = []

    for file in repo.untracked_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                files.append(File(name=file, content=content, type=FileType.UNTRACKED))
        except Exception as e:
            # display warning but ignore
            display_warning(f"Cannot load file {file}: {e}")
            continue

    return files


def load_modified_files(repo: Repo) -> list[File]:
    """Load modified files from the given repository.

    Args:
        repo (Repo): Current git repository.

    Returns:
        list[File]: A collection of all modified files."""
    files = []
    lookup = repo.git.diff("HEAD", "--name-only").splitlines()

    for file in lookup:
        try:
            files.append(
                File(
                    name=file,
                    content=repo.git.diff("HEAD", "--", file),
                    type=FileType.MODIFIED,
                )
            )
        except Exception as e:
            # display warning but ignore
            display_warning(f"Cannot load file {file}: {e}")
            continue

    return files


def load_all(repo: Repo) -> Union[str, None]:
    """Load all untracked and modified files as raw string

    Args:
        repo (Repo): Current git repository.

    Returns:
        str: A raw string containing all files.
        none: If no changes were found on current repository."""
    files = load_untracked_files(repo) + load_modified_files(repo)

    if not files or len(files) == 0:
        return None

    txt = []

    for file in files:
        txt.append(f">>>> {file.name} ({file.type.value})")
        txt.append(file.content)
        txt.append("<<<<")

    return "\n".join(txt)
