"""Utilities for the LLM."""

from typing import Optional

import git

from .types import get_commit_types_resume
from .files import load_all


def prompt_resume_changes(repo: git.Repo, explanation: str = None) -> Optional[str]:
    """Resume the changes on the given repository.

    Args:
        repo (git.Repo): The repository to resume the changes for.
        explanation (str, optional): A short explanation of the changes. Defaults to None.

    Returns:
        str: The resume of the changes.
    """
    changes = load_all(repo)

    if changes is None:
        return None

    contents = [
        "You are a helpful assistant that resume changes applyed to a git repository.",
        "You should generate a meaningful resume about the changes below.",
        "Please follow rules:",
        "0. When analyzing the changes, new files (aka untracked files) has priority over modified files;",
        "1. You can do file references, e.g: 'The file 'file.txt' was modified to add a new function';",
        "2. You can inline short code snippets, e.g: 'The function 'sum' was added to the file 'math.py' to sum two numbers';",
        "3. You should not include huge code snippets;",
        "4. You should not explain the changes step by step, must be focused on the overall changes;",
        "5. If provided, use the user short explanation to understand what changed;",
        ":>> changes",
        changes,
        "<<: end of changes",
    ]

    if explanation is not None:
        contents.append(":>> user short explanation about what changed")
        contents.append(explanation)
        contents.append("<<: end of user short explanation about what changed")

    return "\n".join(contents)


def prompt_commit_from_resume(
    resume: str, explanation: Optional[str] = None
) -> Optional[str]:
    """Generate a commit message from the resume of the changes.

    Args:
        repo (git.Repo): The repository to generate the commit message for.
        resume (str): The resume of the changes.
        explanation (str, optional): A short explanation of the changes. Defaults to None.

    Returns:
        str: The generated commit message.
    """
    contents = [
        "You are a helpful assistant that generates commit messages for changes on a git repository.",
        "You should generate a commit message from the resume below and set the commit type based on it.",
        "Please follow rules:",
        "1. You must use an existing commit type from the CSV 'type' property below. To choose the commit type, you should see the resume below and choose the most appropriate commit type that covers the changes. See the 'meaning' property to understand the commit type;",
        "2. If you can't choose a commit type or no commit type is suitable, use the 'other' commit type;",
        "3. When answering, the 'scope' is a overall categorization for the resume. Not related to type. E.g: If main resume are about entity, the scope will be 'entities'. When is a version update, will be 'v1.0.0', etc;",
        "4. When answering, the 'short_description' should resume the changes with less than 80 characters. It will be used as the title of the commit message; E.g: 'Add the FileEntity class';",
        "5. When answering, the 'description' should be a detailed description of the resume with less than 500 characters. It will be used as the body of the commit message. E.g: 'This commit adds the FileEntity class to the project. This class is responsible for representing a file in the system. It contains the following properties: name, size, type, etc.';",
        "6. When answering, the 'reason' should be a brief explanation of why you choose the commit type.",
        "7. If provided, use the user short explanation to understand what changed;",
        ":>> available commit types",
        get_commit_types_resume(),
        "<<: end of available commit types",
        ":>> resume",
        resume,
        "<<: end of resume",
    ]

    if explanation is not None:
        contents.append(":>> user short explanation about what changed")
        contents.append(explanation)
        contents.append("<<: end of user short explanation about what changed")

    return "\n".join(contents)


def prompt_commit_from_files(
    repo: git.Repo, explanation: Optional[str] = None
) -> Optional[str]:
    """Generate a commit message for the changes on the given repository.

    Args:
        repo (git.Repo): The repository to generate the commit message for.
        explanation (str, optional): A short explanation of the changes. Defaults to None.

    Returns:
        Optional[str]: The generated commit message.
    """
    changes = load_all(repo)

    if changes is None:
        return None

    contents = [
        "You are a helpful assistant that generates commit messages for changes on a git repository.",
        "You should generate a commit message from the changes below and set the commit type based on the changes.",
        "Please follow rules:",
        "0. When analyzing the changes, new files (aka untracked files) has priority over modified files;",
        "1. You must use an existing commit type from the CSV 'type' property below. To choose the commit type, you should see the changes and choose the most appropriate commit type that covers the changes. See the 'meaning' property to understand the commit type;",
        "2. If you can't choose a commit type or no commit type is suitable, use the 'other' commit type;",
        "3. When answering, the 'scope' is a overall categorization for the changes. Not related to type. E.g: If main changes are about entity, the scope will be 'entities'. When is a version update, will be 'v1.0.0', etc;",
        "4. When answering, the 'short_description' should resume changes with less than 80 characters. It will be used as the title of the commit message; E.g: 'Add the FileEntity class';",
        "5. When answering, the 'description' should be a detailed description of the changes with less than 500 characters. It will be used as the body of the commit message. E.g: 'This commit adds the FileEntity class to the project. This class is responsible for representing a file in the system. It contains the following properties: name, size, type, etc.';",
        "6. When answering, the 'reason' should be a brief explanation of why you choose the commit type.",
        "7. If provided, use the user short explanation to understand what changed;",
        ":>> available commit types",
        get_commit_types_resume(),
        "<<: end of available commit types",
        ":>> changes",
        changes,
        "<<: end of changes",
    ]

    if explanation is not None:
        contents.append(":>> user short explanation about what changed")
        contents.append(explanation)
        contents.append("<<: end of user short explanation about what changed")

    return "\n".join(contents)
