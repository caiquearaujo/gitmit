"""Types for the project."""

from enum import Enum

from pydantic import BaseModel


class CommitType(Enum):
    """The type of commit."""

    FEAT = "feat"
    BUGFIX = "bugfix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    PERF = "perf"
    ENHANCEMENT = "enhancement"
    TEST = "test"
    LINT = "lint"
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
    HOTFIX = "hotfix"
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
            commit_meaning="Use this when introducing a new feature that changes or adds functionality from the user's perspective.",
            commit_title="Feature",
        ),
        CommitTypeProps(
            commit_emoji=":bug:",
            preview_emoji="🐞",
            commit_type=CommitType.BUGFIX,
            commit_meaning="Use this when fixing an issue or bug. This typically addresses flaws in logic or unintended behavior.",
            commit_title="Bugfix",
        ),
        CommitTypeProps(
            commit_emoji=":books:",
            preview_emoji="📚",
            commit_type=CommitType.DOCS,
            commit_meaning="Use this when adding or improving documentation (e.g., README, comments, or any form of project documentation).",
            commit_title="Documentation",
        ),
        CommitTypeProps(
            commit_emoji=":gem:",
            preview_emoji="💎",
            commit_type=CommitType.STYLE,
            commit_meaning="Use this when making purely stylistic changes that do not affect code behavior (formatting, indentation, etc.).",
            commit_title="Style",
        ),
        CommitTypeProps(
            commit_emoji=":package:",
            preview_emoji="📦",
            commit_type=CommitType.REFACTOR,
            commit_meaning="Use this when restructuring or reorganizing the code without altering its external behavior.",
            commit_title="Refactor",
        ),
        CommitTypeProps(
            commit_emoji=":racehorse:",
            preview_emoji="🐎",
            commit_type=CommitType.PERF,
            commit_meaning="Use this when improving performance, optimizing code, or reducing resource usage.",
            commit_title="Performance",
        ),
        CommitTypeProps(
            commit_emoji=":recycle:",
            preview_emoji="♻️",
            commit_type=CommitType.ENHANCEMENT,
            commit_meaning="Use this when making minor improvements to existing functionality that are not fixes or new features.",
            commit_title="Enhancement",
        ),
        CommitTypeProps(
            commit_emoji=":white_check_mark:",
            preview_emoji="✅",
            commit_type=CommitType.TEST,
            commit_meaning="Use this when adding or updating tests.",
            commit_title="Test",
        ),
        CommitTypeProps(
            commit_emoji=":rotating_light:",
            preview_emoji="🚨",
            commit_type=CommitType.LINT,
            commit_meaning="Use this when fixing or adjusting linter, compiler warnings, or related code-quality checks.",
            commit_title="Lint",
        ),
        CommitTypeProps(
            commit_emoji=":wrench:",
            preview_emoji="🔧",
            commit_type=CommitType.BUILD,
            commit_meaning="Use this when making changes to the build process or external dependencies that affect the build system.",
            commit_title="Build",
        ),
        CommitTypeProps(
            commit_emoji=":gear:",
            preview_emoji="⚙️",
            commit_type=CommitType.CI,
            commit_meaning="Use this when modifying CI configuration or scripts (e.g., GitHub Actions, Jenkins, CircleCI).",
            commit_title="CI",
        ),
        CommitTypeProps(
            commit_emoji=":recycle:",
            preview_emoji="♻️",
            commit_type=CommitType.CHORE,
            commit_meaning="Use this when performing general maintenance tasks that do not affect source or test files directly (e.g., package updates, minor config changes).",
            commit_title="Chore",
        ),
        CommitTypeProps(
            commit_emoji=":rewind:",
            preview_emoji="⏪",
            commit_type=CommitType.REVERT,
            commit_meaning="Use this when reverting a previous commit.",
            commit_title="Revert",
        ),
        CommitTypeProps(
            commit_emoji=":arrow_double_up:",
            preview_emoji="⏫",
            commit_type=CommitType.DEPENDENCIES,
            commit_meaning="Use this when updating or modifying production dependencies.",
            commit_title="Dependencies",
        ),
        CommitTypeProps(
            commit_emoji=":arrow_double_up:",
            preview_emoji="⏫",
            commit_type=CommitType.PEER_DEPENDENCIES,
            commit_meaning="Use this when updating or changing peer dependencies (often relevant for libraries/plugins).",
            commit_title="Peer Dependencies",
        ),
        CommitTypeProps(
            commit_emoji=":arrow_double_up:",
            preview_emoji="⏫",
            commit_type=CommitType.DEV_DEPENDENCIES,
            commit_meaning="Use this when updating or modifying development dependencies (testing, linting, building, etc.).",
            commit_title="Dev Dependencies",
        ),
        CommitTypeProps(
            commit_emoji=":card_index:",
            preview_emoji="📇",
            commit_type=CommitType.METADATA,
            commit_meaning="Use this when updating metadata like project settings, documentation metadata, or repository information.",
            commit_title="Metadata",
        ),
        CommitTypeProps(
            commit_emoji=":bookmark:",
            preview_emoji="🔖",
            commit_type=CommitType.VERSION,
            commit_meaning="Use this when bumping or modifying version numbers.",
            commit_title="Version",
        ),
        CommitTypeProps(
            commit_emoji=":lock:",
            preview_emoji="🔒",
            commit_type=CommitType.SECURITY,
            commit_meaning="Use this when addressing security vulnerabilities or implementing security-related fixes.",
            commit_title="Security",
        ),
        CommitTypeProps(
            commit_emoji=":ambulance:",
            preview_emoji="🚑",
            commit_type=CommitType.HOTFIX,
            commit_meaning="Use this for urgent or high-priority fixes addressing critical issues in production.",
            commit_title="Hotfix",
        ),
        CommitTypeProps(
            commit_emoji=":ok_hand:",
            preview_emoji="👌",
            commit_type=CommitType.REVIEW,
            commit_meaning="Use this when reviewing code, merging PRs, or making changes based on code reviews.",
            commit_title="Review",
        ),
        CommitTypeProps(
            commit_emoji=":bricks:",
            preview_emoji="🧱",
            commit_type=CommitType.OTHER,
            commit_meaning="Use this for any commit that does not fit into the other categories.",
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
