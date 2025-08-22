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
        "YOU ARE a helpful assistant with HIGH EXPERIENCE at software engineering.",
        "YOUR GOAL is to generate a VERY SPECIFIC commit message for a git repository.",
        "TO ACHIEVE YOUR GOAL you need to ANALYZE CAREFULLY the changes related below. Then, YOU SHOULD to write a message and categorize the changes and set the valid commit type to them.",
        "YOU SHOULD STRICT FOLLOW THE RULES BELOW:",
        "0. Modified files has HIGHER PRIORITY than new files (aka untracked files), UNLESS user explicitly says otherwise;",
        "1. YOU MUST TO USE an existing commit type from the CSV 'type' property below. To choose the commit type, YOU SHOULD CATEGORIZE the changes and choose the most appropriate commit type that covers them. At CSV, see the 'meaning' property to understand the context of a commit type and categorize it accordingly;",
        "2. IF YOU CANNOT CHOOSE a commit type or NO COMMIT TYPE IS SUITABLE, YOU SHOULD USE the 'other' commit type;",
        "3. JSON 'scope' PROPERTY is a overall categorization for the changes. Not related to type. E.g: If main changes are about entity, the scope will be 'entities'. When is a version update, will be 'v1.0.0', etc. IF YOU CANNOT CHOOSE a scope, use 'other' scope;",
        "4. JSON 'short_description' PROPERTY SHOULD resume changes with less than 80 characters. It will be used as the title of the commit message. IT MUST BE SIMPLE, CONCISE AND VERY MEANINGFUL. E.g: 'Add the FileEntity class';",
        "5. JSON 'description' PROPERTY SHOULD BE a detailed description of the changes with less than 500 characters. It will be used as the body of the commit message. DO NOT REPEAT YOURSELF, IT MUST BE DETAILED AND VERY MEANINGFUL DESCRIPTION. E.g: 'This commit adds the FileEntity class to the project. This class is responsible for representing a file in the system. It contains the following properties: name, size, type, etc.';",
        "6. JSON 'reason' PROPERTY SHOULD BE a bried explanation to user which explain what you have understood about the changes;",
        "7. IF USER PROVIDE AN EXPLANATION ABOUT COMMIT, what he said will have HIGH PRIORITY and you SHOULD RELATE this information to the changes seen in the code;",
        "8. BE CAREFUL WITH THE COMMIT TYPE 'feat', YOU MUST USE IT ONLY MAIN CHANGES ARE ABOUT A NEW FEATURE OR A EXPLICIT FEATURE ADDITION. OTHERWISE, CHOOSE ANOTHER COMMIT TYPE.",
        ":>> AVAILABLE COMMIT TYPES",
        get_commit_types_resume(),
        "<<: end of AVAILABLE COMMIT TYPES",
        ":>> CHANGES",
        resume,
        "<<: end of CHANGES",
    ]

    if explanation is not None:
        contents.append(":>> USER EXPLANATION")
        contents.append(explanation)
        contents.append("<<: end of USER EXPLANATION")

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
        "YOU ARE a helpful assistant with HIGH EXPERIENCE at software engineering.",
        "YOUR GOAL is to generate a VERY SPECIFIC commit message for a git repository.",
        "TO ACHIEVE YOUR GOAL you need to ANALYZE CAREFULLY the changes related below. Then, YOU SHOULD to write a message and categorize the changes and set the valid commit type to them.",
        "YOU SHOULD STRICT FOLLOW THE RULES BELOW:",
        "0. Modified files has HIGHER PRIORITY than new files (aka untracked files), UNLESS user explicitly says otherwise;",
        "1. YOU MUST TO USE an existing commit type from the CSV 'type' property below. To choose the commit type, YOU SHOULD CATEGORIZE the changes and choose the most appropriate commit type that covers them. At CSV, see the 'meaning' property to understand the context of a commit type and categorize it accordingly;",
        "2. IF YOU CANNOT CHOOSE a commit type or NO COMMIT TYPE IS SUITABLE, YOU SHOULD USE the 'other' commit type;",
        "3. JSON 'scope' PROPERTY is a overall categorization for the changes. Not related to type. E.g: If main changes are about entity, the scope will be 'entities'. When is a version update, will be 'v1.0.0', etc. IF YOU CANNOT CHOOSE a scope, use 'other' scope;",
        "4. JSON 'short_description' PROPERTY SHOULD resume changes with less than 80 characters. It will be used as the title of the commit message. IT MUST BE SIMPLE, CONCISE AND VERY MEANINGFUL. E.g: 'Add the FileEntity class';",
        "5. JSON 'description' PROPERTY SHOULD BE a detailed description of the changes with less than 500 characters. It will be used as the body of the commit message. DO NOT REPEAT YOURSELF, IT MUST BE DETAILED AND VERY MEANINGFUL DESCRIPTION. E.g: 'This commit adds the FileEntity class to the project. This class is responsible for representing a file in the system. It contains the following properties: name, size, type, etc.';",
        "6. JSON 'reason' PROPERTY SHOULD BE a bried explanation to user which explain what you have understood about the changes;",
        "7. IF USER PROVIDE AN EXPLANATION ABOUT COMMIT, what he said will have HIGH PRIORITY and you SHOULD RELATE this information to the changes seen in the code;",
        "8. BE CAREFUL WITH THE COMMIT TYPE 'feat', YOU MUST USE IT ONLY MAIN CHANGES ARE ABOUT A NEW FEATURE OR A EXPLICIT FEATURE ADDITION. OTHERWISE, CHOOSE ANOTHER COMMIT TYPE.",
        ":>> AVAILABLE COMMIT TYPES",
        get_commit_types_resume(),
        "<<: end of AVAILABLE COMMIT TYPES",
        ":>> CHANGES",
        changes,
        "<<: end of CHANGES",
    ]

    if explanation is not None:
        contents.append(":>> USER EXPLANATION")
        contents.append(explanation)
        contents.append("<<: end of USER EXPLANATION")

    return "\n".join(contents)
