"""Ollama LLM service."""

from typing import Optional

from ollama import Client
from git import Repo

from . import LLMService, LLMAction
from ..resources.types import CommitMessage

from ..resources import llms


class OllamaLLMService(LLMService):
    """Service for the Ollama LLM."""

    def __init__(
        self, host: str = "http://localhost:11434", model: str = "llama3.1:8b"
    ):
        """Initialize the Ollama LLM service."""
        self.client = Client(host=host)
        self.model = model

    def tokens_used(self) -> int:
        """Get the number of tokens used."""
        raise NotImplementedError("Tokens used is not implemented for Ollama LLM")

    def count_tokens(
        self,
        repo: Repo,
        explanation: Optional[str] = None,
        resume: Optional["LLMService"] = None,
    ) -> int:
        """Count the tokens in the prompt.

        Args:
            prompt (str): The prompt to count the tokens.
        """
        raise NotImplementedError("Count tokens is not implemented for Ollama LLM")

    def resume_changes(
        self, repo: Repo, explanation: Optional[str] = None
    ) -> Optional[str]:
        """Resume changes.

        Args:
            repo (git.Repo): The repository to resume the changes for.
            explanation (str, optional): The explanation of the changes. Defaults to None.
        """
        prompt = llms.prompt_resume_changes(repo, explanation)

        if prompt is None:
            return None

        response = self.client.generate(
            model=self.model,
            prompt=prompt,
        )

        if response is None:
            return None

        return response["response"]

    def commit_message(
        self,
        repo: Repo,
        explanation: Optional[str] = None,
        resume: Optional[LLMService] = None,
    ) -> Optional[CommitMessage]:
        """Generate a commit message.

        Args:
            repo (git.Repo): The repository to generate the commit message for.
            explanation (str, optional): The explanation of the changes. Defaults to None.
            resume (LLMService, optional): The resume of the changes. Defaults to None.
        """
        prompt = llms.prompt_commit_from_files(repo, explanation)

        if prompt is None:
            return None

        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            format=CommitMessage.model_json_schema(),
        )

        if response is None:
            return None

        return CommitMessage.model_validate_json(response["response"])

    def supports(self, action: LLMAction) -> bool:
        """Check if the LLM supports the action.

        Args:
            action (str): The action to check.

        Returns:
            bool: True if the LLM supports the action, False otherwise.
        """
        return action in [LLMAction.RESUME_CHANGES, LLMAction.COMMIT_MESSAGE]
