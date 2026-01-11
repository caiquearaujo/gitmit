"""Module for manipulating files."""

from enum import Enum
from pathlib import Path
from typing import Optional, Union

from git import Repo
from pydantic import BaseModel


class FileType(Enum):
    """File type enum"""

    UNTRACKED = "untracked"
    MODIFIED = "modified"


class File(BaseModel):
    """File class"""

    name: str
    content: str
    type: FileType


class GitignoreParser:
    """
    Simple gitignore-style parser for .gitmitignore files.

    This is a simplified implementation. For production, consider using
    the `pathspec` library which handles all gitignore edge cases.
    """

    def __init__(self, patterns: list[str]):
        self.patterns = [
            p.strip() for p in patterns if p.strip() and not p.startswith("#")
        ]

    @classmethod
    def from_file(cls, repo_path: Path) -> "GitignoreParser":
        """Load patterns from .gitmitignore file."""
        gitmitignore_path = repo_path / ".gitmitignore"

        if not gitmitignore_path.exists():
            return cls([])

        with open(gitmitignore_path, "r", encoding="utf-8") as f:
            patterns = f.readlines()

        return cls(patterns)

    def should_ignore(self, filepath: str) -> bool:
        """Check if a filepath should be ignored."""
        from fnmatch import fnmatch

        for pattern in self.patterns:
            # Handle directory patterns (ending with /)
            if pattern.endswith("/"):
                if filepath.startswith(pattern) or f"/{pattern}" in filepath:
                    return True
            # Handle negation patterns
            elif pattern.startswith("!"):
                if fnmatch(filepath, pattern[1:]):
                    return False
            # Standard pattern matching
            elif fnmatch(filepath, pattern) or fnmatch(Path(filepath).name, pattern):
                return True

        return False


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
        ignore_parser: Optional parser for .gitmitignore patterns.

    Returns:
        list[File]: A collection of all untracked files.
    """
    files = []
    repo_path = Path(repo.working_dir)

    for file in repo.untracked_files:
        # Check if file should be ignored
        if ignore_parser and ignore_parser.should_ignore(file):
            continue

        try:
            file_path = repo_path / file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                files.append(File(name=file, content=content, type=FileType.UNTRACKED))
        except Exception:
            files.append(
                File(
                    name=file, content="<binary or unreadable>", type=FileType.UNTRACKED
                )
            )
            continue

    return files


def load_modified_files(
    repo: Repo, ignore_parser: Optional[GitignoreParser] = None
) -> list[File]:
    """Load modified files from the given repository.

    Args:
        repo (Repo): Current git repository.
        ignore_parser: Optional parser for .gitmitignore patterns.

    Returns:
        list[File]: A collection of all modified files.
    """
    files = []

    try:
        lookup = repo.git.diff("HEAD", "--name-only").splitlines()
    except Exception:
        # Repository might not have any commits yet
        return files

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
            # File might have been deleted or is binary
            print(f"Warning: Cannot load file {file}: {e}")
            continue

    return files


def load_all(repo: Repo, debug: bool = False) -> Union[str, None]:
    """Load all untracked and modified files as raw string.

    Args:
        repo (Repo): Current git repository.
        debug: If True, print debug information.

    Returns:
        str: A raw string containing all files.
        None: If no changes were found on current repository.
    """
    parser = _get_gitignore_parser(repo)
    files = load_untracked_files(repo, parser) + load_modified_files(repo, parser)

    if not files or len(files) == 0:
        return None

    if debug:
        print("=== Files related to commit ===")
        for file in files:
            print(f"  {file.name} ({file.type.value})")
        print()

    txt = []

    for file in files:
        txt.append(f">>>> {file.name} ({file.type.value})")
        txt.append(file.content)
        txt.append("<<<< end of file")

    return "\n".join(txt)
