"""Types for the project."""

import json
from enum import Enum

from pydantic import BaseModel


class CommitType(Enum):
    """The type of commit."""

    FEAT = "feat"
    IMPROVEMENT = "improvement"
    FIX = "fix"
    BUG = "bug"
    LINT = "lint"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    PERF = "perf"
    TEST = "test"
    BUILD = "build"
    CI = "ci"
    CHORE = "chore"
    REVERT = "revert"
    DEPENDENCIES = "dependencies"
    PEER_DEPENDENCIES = "peerDependencies"
    DEV_DEPENDENCIES = "devDependencies"
    METADATA = "metadata"
    VERSION = "version"
    SECURITY = "security"
    CRITICAL = "critical"
    REVIEW = "review"
    OTHER = "other"


class CommitTypeProps(BaseModel):
    """Properties for a commit type."""

    commit_emoji: str
    preview_emoji: str
    commit_type: CommitType
    commit_meaning: str
    commit_title: str


class CommitMessage(BaseModel):
    """Commit message."""

    type: CommitType
    scope: str
    short_description: str
    description: str
    reason: str


def get_commit_types() -> list[CommitTypeProps]:
    """Get the commit types.

    Returns: A list of commit types.
    """
    return [
        CommitTypeProps(
            commit_emoji=":sparkles:",
            preview_emoji="✨",
            commit_type=CommitType.FEAT,
            commit_meaning="Useful when adding new features. Should be used carefully, for context a feature means a new class, function, component, etc.",
            commit_title="Feature",
        ),
        CommitTypeProps(
            commit_emoji=":adhesive_bandage:",
            preview_emoji="🩹",
            commit_type=CommitType.FIX,
            commit_meaning="Useful when overall fixes, not a new feature or something else.",
            commit_title="Fix",
        ),
        CommitTypeProps(
            commit_emoji=":bug:",
            preview_emoji="🐞",
            commit_type=CommitType.BUG,
            commit_meaning="Useful when fixing bugs.",
            commit_title="Bug",
        ),
        CommitTypeProps(
            commit_emoji=":books:",
            preview_emoji="📚",
            commit_type=CommitType.DOCS,
            commit_meaning="Useful when adding documentation, editing markdowns, etc.",
            commit_title="Documentation",
        ),
        CommitTypeProps(
            commit_emoji=":gem:",
            preview_emoji="💎",
            commit_type=CommitType.STYLE,
            commit_meaning="Useful when styling the code, styling the frontend, etc.",
            commit_title="Style",
        ),
        CommitTypeProps(
            commit_emoji=":package:",
            preview_emoji="📦",
            commit_type=CommitType.REFACTOR,
            commit_meaning="Useful when refactoring the code, changing the code structure, etc.",
            commit_title="Refactor",
        ),
        CommitTypeProps(
            commit_emoji=":racehorse:",
            preview_emoji="🐎",
            commit_type=CommitType.PERF,
            commit_meaning="Useful when improving the performance of the code.",
            commit_title="Performance",
        ),
        CommitTypeProps(
            commit_emoji=":recycle:",
            preview_emoji="♻️ ",
            commit_type=CommitType.IMPROVEMENT,
            commit_meaning="Useful when improving the code, not a new feature or something else.",
            commit_title="Improvements",
        ),
        CommitTypeProps(
            commit_emoji=":white_check_mark:",
            preview_emoji="✅",
            commit_type=CommitType.TEST,
            commit_meaning="Useful when writing tests.",
            commit_title="Test",
        ),
        CommitTypeProps(
            commit_emoji=":rotating_light:",
            preview_emoji="🚨",
            commit_type=CommitType.LINT,
            commit_meaning="Useful when fixing compiler / linter warnings.",
            commit_title="Lint",
        ),
        CommitTypeProps(
            commit_emoji=":wrench:",
            preview_emoji="🔧",
            commit_type=CommitType.BUILD,
            commit_meaning="Useful when building the code.",
            commit_title="Build",
        ),
        CommitTypeProps(
            commit_emoji=":gear:",
            preview_emoji="⚙️ ",
            commit_type=CommitType.CI,
            commit_meaning="Useful when setting up the continuous integration.",
            commit_title="CI",
        ),
        CommitTypeProps(
            commit_emoji=":recycle:",
            preview_emoji="♻️ ",
            commit_type=CommitType.CHORE,
            commit_meaning="Useful when doing chores, like cleaning the code, etc.",
            commit_title="Chore",
        ),
        CommitTypeProps(
            commit_emoji=":rewind:",
            preview_emoji="⏪",
            commit_type=CommitType.REVERT,
            commit_meaning="Useful when reverting a commit.",
            commit_title="Revert",
        ),
        CommitTypeProps(
            commit_emoji=":arrow_double_up:",
            preview_emoji="⏫",
            commit_type=CommitType.DEPENDENCIES,
            commit_meaning="Useful when updating the dependencies.",
            commit_title="Dependencies",
        ),
        CommitTypeProps(
            commit_emoji=":arrow_double_up:",
            preview_emoji="⏫",
            commit_type=CommitType.PEER_DEPENDENCIES,
            commit_meaning="Useful when updating the peer dependencies.",
            commit_title="Peer Dependencies",
        ),
        CommitTypeProps(
            commit_emoji=":arrow_double_up:",
            preview_emoji="⏫",
            commit_type=CommitType.DEV_DEPENDENCIES,
            commit_meaning="Useful when updating the dev dependencies.",
            commit_title="Dev Dependencies",
        ),
        CommitTypeProps(
            commit_emoji=":card_index:",
            preview_emoji="📇",
            commit_type=CommitType.METADATA,
            commit_meaning="Useful when updating the metadata.",
            commit_title="Metadata",
        ),
        CommitTypeProps(
            commit_emoji=":bookmark:",
            preview_emoji="🔖",
            commit_type=CommitType.VERSION,
            commit_meaning="Useful when updating the version.",
            commit_title="Version",
        ),
        CommitTypeProps(
            commit_emoji=":lock:",
            preview_emoji="🔒",
            commit_type=CommitType.SECURITY,
            commit_meaning="Useful when updating the security issues.",
            commit_title="Security",
        ),
        CommitTypeProps(
            commit_emoji=":ambulance:",
            preview_emoji="🚑",
            commit_type=CommitType.CRITICAL,
            commit_meaning="Useful when updating the critical changes that may break the code.",
            commit_title="Critical",
        ),
        CommitTypeProps(
            commit_emoji=":ok_hand:",
            preview_emoji="👌",
            commit_type=CommitType.REVIEW,
            commit_meaning="Useful when reviewing the code.",
            commit_title="Review",
        ),
        CommitTypeProps(
            commit_emoji=":bricks:",
            preview_emoji="🧱",
            commit_type=CommitType.OTHER,
            commit_meaning="Useful when doing other things not related to the other commit types.",
            commit_title="Other",
        ),
    ]


def get_commit_types_resume() -> str:
    """Get the commit types resume as a CSV string.

    Returns: A CSV string containing the commit types.
    """
    return "type;meaning\n" + "\n".join(
        f"{item.commit_type.value.upper()};{item.commit_meaning}"
        for item in get_commit_types()
    )
