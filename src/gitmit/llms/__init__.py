"""LLM services."""

from abc import ABC, abstractmethod
from enum import Enum

from git import Repo

from ..resources.types import CommitMessage


class LLMAction(Enum):
    """LLM action."""

    RESUME_CHANGES = "resume_changes"
    COMMIT_MESSAGE = "commit_message"
    COUNT_TOKENS = "count_tokens"
    TOKENS_USED = "tokens_used"


class LLMService(ABC):
    """LLM service."""

    @abstractmethod
    def tokens_used(self) -> int:
        """Get the number of tokens used."""

    @abstractmethod
    def count_tokens(
        self,
        repo: Repo,
        explanation: str | None = None,
        resume: "LLMService | None" = None,
        no_feat: bool = False,
        debug: bool = False,
    ) -> int:
        """Count the tokens in the prompt.

        Args:
            repo (git.Repo): The repository to count the tokens for.
            explanation (str, optional): The explanation of the changes. Defaults to None.
            resume (LLMService, optional): The resume of the changes. Defaults to None.

        Returns:
            int: The number of tokens in the prompt.
        """

    @abstractmethod
    def resume_changes(self, repo: Repo, explanation: str | None = None) -> str | None:
        """Resume changes.

        Args:
            repo (git.Repo): The repository to resume the changes for.
            explanation (str, optional): The explanation of the changes. Defaults to None.

        Returns:
            str: The resumed changes.
        """

    @abstractmethod
    def commit_message(
        self,
        repo: Repo,
        explanation: str | None = None,
        resume: "LLMService | None" = None,
        no_feat: bool = False,
        debug: bool = False,
    ) -> CommitMessage | None:
        """Generate a commit message.

        Args:
            repo (git.Repo): The repository to generate the commit message for.
            explanation (str, optional): The explanation of the changes. Defaults to None.
            resume (LLMService, optional): The resume of the changes. Defaults to None.

        Returns:
            CommitMessage: The generated commit message.
        """

    @abstractmethod
    def supports(self, action: LLMAction) -> bool:
        """Check if the LLM supports the action.

        Args:
            action (str): The action to check.

        Returns:
            bool: True if the LLM supports the action, False otherwise.
        """
