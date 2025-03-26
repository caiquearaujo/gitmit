"""Ollama LLM service."""

from typing import Optional

from ollama import Client
from git import Repo

from src.llms import LLMService
from src.tools.commit import CommitMessage

from src.resources import llms


class OllamaLLMService(LLMService):
    """Service for the Ollama LLM."""

    def __init__(
        self, host: str = "http://localhost:11434", model: str = "llama3.1:8b"
    ):
        """Initialize the Ollama LLM service."""
        self.client = Client(host=host)
        self.model = model

    def count_tokens(self, prompt: str) -> int:
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
            raise ValueError("No response from the LLM")

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
        prompt = None

        if resume is not None:
            prompt = llms.prompt_commit_from_resume(
                resume.resume_changes(repo, explanation), explanation
            )
        else:
            prompt = llms.prompt_commit_from_files(repo, explanation)

        if prompt is None:
            return None

        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            format=CommitMessage.model_json_schema(),
        )

        if response is None:
            raise ValueError("No response from the LLM")

        return CommitMessage.model_validate_json(response["response"])
