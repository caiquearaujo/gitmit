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
            commit_meaning="ONLY for genuinely NEW user-facing features. NOT for helper functions, internal refactoring, or supporting code.",
            commit_title="Feature",
        ),
        CommitTypeProps(
            commit_emoji=":bug:",
            preview_emoji="🐞",
            commit_type=CommitType.BUGFIX,
            commit_meaning="Fixing an issue or bug. Addresses flaws in logic or unintended behavior.",
            commit_title="Bugfix",
        ),
        CommitTypeProps(
            commit_emoji=":books:",
            preview_emoji="📚",
            commit_type=CommitType.DOCS,
            commit_meaning="Adding or improving documentation (README, comments, docstrings).",
            commit_title="Documentation",
        ),
        CommitTypeProps(
            commit_emoji=":gem:",
            preview_emoji="💎",
            commit_type=CommitType.STYLE,
            commit_meaning="Purely stylistic changes: formatting, indentation, variable renames, import ordering. NO behavior change.",
            commit_title="Style",
        ),
        CommitTypeProps(
            commit_emoji=":package:",
            preview_emoji="📦",
            commit_type=CommitType.REFACTOR,
            commit_meaning="Restructuring code without changing behavior. Moving code, extracting functions/classes, reorganizing.",
            commit_title="Refactor",
        ),
        CommitTypeProps(
            commit_emoji=":racehorse:",
            preview_emoji="🐎",
            commit_type=CommitType.PERF,
            commit_meaning="Improving performance, optimizing code, reducing resource usage.",
            commit_title="Performance",
        ),
        CommitTypeProps(
            commit_emoji=":recycle:",
            preview_emoji="♻️",
            commit_type=CommitType.ENHANCEMENT,
            commit_meaning="Minor improvements to EXISTING functionality. Not a new feature, not a bug fix.",
            commit_title="Enhancement",
        ),
        CommitTypeProps(
            commit_emoji=":white_check_mark:",
            preview_emoji="✅",
            commit_type=CommitType.TEST,
            commit_meaning="Adding or updating tests.",
            commit_title="Test",
        ),
        CommitTypeProps(
            commit_emoji=":rotating_light:",
            preview_emoji="🚨",
            commit_type=CommitType.LINT,
            commit_meaning="Fixing linter warnings, type errors, or code-quality checks.",
            commit_title="Lint",
        ),
        CommitTypeProps(
            commit_emoji=":wrench:",
            preview_emoji="🔧",
            commit_type=CommitType.BUILD,
            commit_meaning="Changes to the build process or build configuration.",
            commit_title="Build",
        ),
        CommitTypeProps(
            commit_emoji=":gear:",
            preview_emoji="⚙️",
            commit_type=CommitType.CI,
            commit_meaning="Modifying CI configuration or scripts (GitHub Actions, Jenkins, etc.).",
            commit_title="CI",
        ),
        CommitTypeProps(
            commit_emoji=":recycle:",
            preview_emoji="♻️",
            commit_type=CommitType.CHORE,
            commit_meaning="General maintenance tasks that don't affect source or test files directly.",
            commit_title="Chore",
        ),
        CommitTypeProps(
            commit_emoji=":rewind:",
            preview_emoji="⏪",
            commit_type=CommitType.REVERT,
            commit_meaning="Reverting a previous commit.",
            commit_title="Revert",
        ),
        CommitTypeProps(
            commit_emoji=":arrow_double_up:",
            preview_emoji="⏫",
            commit_type=CommitType.DEPENDENCIES,
            commit_meaning="Updating or modifying production dependencies.",
            commit_title="Dependencies",
        ),
        CommitTypeProps(
            commit_emoji=":arrow_double_up:",
            preview_emoji="⏫",
            commit_type=CommitType.PEER_DEPENDENCIES,
            commit_meaning="Updating or changing peer dependencies.",
            commit_title="Peer Dependencies",
        ),
        CommitTypeProps(
            commit_emoji=":arrow_double_up:",
            preview_emoji="⏫",
            commit_type=CommitType.DEV_DEPENDENCIES,
            commit_meaning="Updating or modifying development dependencies.",
            commit_title="Dev Dependencies",
        ),
        CommitTypeProps(
            commit_emoji=":card_index:",
            preview_emoji="📇",
            commit_type=CommitType.METADATA,
            commit_meaning="Updating metadata like project settings or repository information.",
            commit_title="Metadata",
        ),
        CommitTypeProps(
            commit_emoji=":bookmark:",
            preview_emoji="🔖",
            commit_type=CommitType.VERSION,
            commit_meaning="Bumping or modifying version numbers.",
            commit_title="Version",
        ),
        CommitTypeProps(
            commit_emoji=":lock:",
            preview_emoji="🔒",
            commit_type=CommitType.SECURITY,
            commit_meaning="Addressing security vulnerabilities or implementing security fixes.",
            commit_title="Security",
        ),
        CommitTypeProps(
            commit_emoji=":ambulance:",
            preview_emoji="🚑",
            commit_type=CommitType.HOTFIX,
            commit_meaning="Urgent fixes for critical issues in production.",
            commit_title="Hotfix",
        ),
        CommitTypeProps(
            commit_emoji=":ok_hand:",
            preview_emoji="👌",
            commit_type=CommitType.REVIEW,
            commit_meaning="Changes based on code reviews or PR feedback.",
            commit_title="Review",
        ),
        CommitTypeProps(
            commit_emoji=":bricks:",
            preview_emoji="🧱",
            commit_type=CommitType.OTHER,
            commit_meaning="Any commit that does not fit into the other categories.",
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
