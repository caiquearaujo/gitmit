"""Module for manipulating files."""

from enum import Enum
from pathlib import Path
from typing import Union, Optional

from pydantic import BaseModel
from git import Repo

from ..utils.gitignore import GitignoreParser
from ..utils.terminal import (
    display_warning,
    display_info,
    Panel,
)


class FileType(Enum):
    """File type enum"""

    UNTRACKED = "untracked"
    MODIFIED = "modified"


class File(BaseModel):
    """File class"""

    name: str
    content: str
    type: FileType


def _get_gitignore_parser(repo: Repo) -> Optional[GitignoreParser]:
    """Get a GitignoreParser if .gitmitignore exists.

    Args:
        repo (Repo): Current git repository.

    Returns:
        GitignoreParser or None if .gitmitignore doesn't exist.
    """
    repo_path = Path(repo.working_dir)
    gitmitignore_path = repo_path / ".gitmitignore"

    if gitmitignore_path.exists():
        return GitignoreParser.from_file(repo_path)

    return None


def load_untracked_files(
    repo: Repo, ignore_parser: Optional[GitignoreParser] = None
) -> list[File]:
    """Load untracked files from the given repository.

    Args:
        repo (Repo): Current git repository.

    Returns:
        list[File]: A collection of all untracked files."""
    files = []

    for file in repo.untracked_files:
        # Check if file should be ignored
        if ignore_parser and ignore_parser.should_ignore(file):
            continue

        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                files.append(File(name=file, content=content, type=FileType.UNTRACKED))
        except Exception:
            files.append(File(name=file, content="<unknown>", type=FileType.UNTRACKED))
            continue

    return files


def load_modified_files(
    repo: Repo, ignore_parser: Optional[GitignoreParser] = None
) -> list[File]:
    """Load modified files from the given repository.

    Args:
        repo (Repo): Current git repository.

    Returns:
        list[File]: A collection of all modified files."""
    files = []
    lookup = repo.git.diff("HEAD", "--name-only").splitlines()

    for file in lookup:
        # Check if file should be ignored
        if ignore_parser and ignore_parser.should_ignore(file):
            continue

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


def load_all(repo: Repo, debug: bool = False) -> Union[str, None]:
    """Load all untracked and modified files as raw string

    Args:
        repo (Repo): Current git repository.

    Returns:
        str: A raw string containing all files.
        none: If no changes were found on current repository."""
    parser = _get_gitignore_parser(repo)
    files = load_untracked_files(repo, parser) + load_modified_files(repo, parser)

    if not files or len(files) == 0:
        return None

    if debug:
        display_info(
            Panel(
                "\n".join([f"{file.name} ({file.type.value})" for file in files]),
                style="bold yellow",
                title="(Debug) Files related to commit",
            )
        )

    txt = []

    for file in files:
        txt.append(f">>>> {file.name} ({file.type.value})")
        txt.append(file.content)
        txt.append("<<<< end of file")

    return "\n".join(txt)
