"""Ollama LLM service."""

from typing import override

import tiktoken
from git import Repo
from ollama import Client

from ..resources import llms
from ..resources.types import CommitMessage
from . import LLMAction, LLMService


class OllamaLLMService(LLMService):
    """Service for the Ollama LLM."""

    def __init__(
        self, host: str = "http://localhost:11434", model: str = "llama3.1:8b"
    ):
        """Initialize the Ollama LLM service."""
        self.client: Client = Client(host=host)
        self.model: str = model
        self.generator: llms.CommitPromptGenerator = llms.CommitPromptGenerator()

    @override
    def tokens_used(self) -> int:
        """Get the number of tokens used."""
        raise NotImplementedError("Tokens used is not implemented for Ollama LLM")

    @override
    def count_tokens(
        self,
        repo: Repo,
        explanation: str | None = None,
        resume: LLMService | None = None,
        no_feat: bool = False,
        debug: bool = False,
    ) -> int:
        """Count the tokens in the prompt.

        Args:
            prompt (str): The prompt to count the tokens.
        """
        prompt = None

        if resume is not None:
            _resume = resume.resume_changes(repo, explanation=explanation)

            if _resume is not None:
                prompt = self.generator.generate_from_resume(
                    _resume,
                    explanation=explanation,
                    no_feat=no_feat,
                )
        else:
            prompt = self.generator.generate(
                repo, explanation=explanation, no_feat=no_feat, debug=debug
            )

        if prompt is None:
            return 0

        encoding = tiktoken.get_encoding("cl100k_base")
        message = f"{prompt.system_prompt}\n\n---\n\n{prompt.user_prompt}"

        return len(encoding.encode(message))

    @override
    def resume_changes(
        self,
        repo: Repo,
        explanation: str | None = None,
    ) -> str | None:
        """Resume changes.

        Args:
            repo (git.Repo): The repository to resume the changes for.
            explanation (str, optional): The explanation of the changes. Defaults to None.
        """
        prompt = llms.generate_resume_prompt(repo, explanation)

        if prompt is None:
            return None

        response = self.client.generate(
            model=self.model,
            prompt=prompt,
        )

        return getattr(response, "response", None)

    @override
    def commit_message(
        self,
        repo: Repo,
        explanation: str | None = None,
        resume: LLMService | None = None,
        no_feat: bool = False,
        debug: bool = False,
    ) -> CommitMessage | None:
        """Generate a commit message.

        Args:
            repo (git.Repo): The repository to generate the commit message for.
            explanation (str, optional): The explanation of the changes. Defaults to None.
            resume (LLMService, optional): The resume of the changes. Defaults to None.
            no_feat (bool, optional): Whether to ignore the `feat` commit type. Defaults to False.
            debug (bool, optional): Whether to display debug information. Defaults to False.
        """
        prompt = self.generator.generate(
            repo, explanation=explanation, no_feat=no_feat, debug=debug
        )

        if prompt is None:
            return None

        response = self.client.generate(
            model=self.model,
            prompt=prompt.user_prompt,
            system=prompt.system_prompt,
            format=CommitMessage.model_json_schema(),
        )

        return CommitMessage.model_validate_json(response["response"])

    @override
    def supports(self, action: LLMAction) -> bool:
        """Check if the LLM supports the action.

        Args:
            action (str): The action to check.

        Returns:
            bool: True if the LLM supports the action, False otherwise.
        """
        return action in [LLMAction.RESUME_CHANGES, LLMAction.COMMIT_MESSAGE]
