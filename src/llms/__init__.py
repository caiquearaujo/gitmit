"""LLM services."""

from abc import ABC, abstractmethod
from typing import Optional
from git import Repo

from src.tools.commit import CommitMessage


class LLMService(ABC):
    """LLM service."""

    @abstractmethod
    def count_tokens(self, prompt: str) -> int:
        """Count the tokens in the prompt.

        Args:
            prompt (str): The prompt to count the tokens.

        Returns:
            int: The number of tokens in the prompt.
        """

    @abstractmethod
    def resume_changes(
        self, repo: Repo, explanation: Optional[str] = None
    ) -> Optional[str]:
        """Resume changes.

        Args:
            prompt (str): The prompt to resume the changes.

        Returns:
            str: The resumed changes.
        """

    @abstractmethod
    def commit_message(
        self,
        repo: Repo,
        explanation: Optional[str] = None,
        resume: Optional["LLMService"] = None,
    ) -> Optional[CommitMessage]:
        """Generate a commit message.

        Args:
            repo (git.Repo): The repository to generate the commit message for.
            explanation (str, optional): The explanation of the changes. Defaults to None.
            resume (LLMService, optional): The resume of the changes. Defaults to None.

        Returns:
            CommitMessage: The generated commit message.
        """
