"""OpenRouter LLM service."""

from typing import Any, override

import requests
import tiktoken
from git import Repo

from ..resources import llms
from ..resources.types import CommitMessage
from ..services.database import LLMUsageDatabaseService
from . import LLMAction, LLMService


class OpenRouterLLMService(LLMService):
    """Service for the OpenRouter LLM."""

    def __init__(
        self,
        api_key: str,
        database: LLMUsageDatabaseService,
        model: str = "anthropic/claude-3.5-sonnet",
        providers: list[str] | None = None,
    ):
        """Initialize the OpenRouter LLM service.

        Args:
            api_key (str): The OpenRouter API key.
            database (LLMUsageDatabaseService): The database service for token tracking.
            model (str, optional): The model to use. Defaults to "anthropic/claude-3.5-sonnet".
            providers (list[str], optional): List of providers to prioritize. Defaults to None.
        """
        self.api_key: str = api_key
        self.model: str = model
        self.database: LLMUsageDatabaseService = database
        self.providers: list[str] | None = (
            [p.strip() for p in providers if p.strip()] if providers else None
        )
        self.base_url: str = "https://openrouter.ai/api/v1/chat/completions"
        self.generator: llms.CommitPromptGenerator = llms.CommitPromptGenerator()

    @override
    def tokens_used(self) -> int:
        """Get the number of tokens used."""
        self.database.start()
        return self.database.current_month_tokens_used(f"openrouter/{self.model}")

    @override
    def count_tokens(
        self,
        repo: Repo,
        explanation: str | None = None,
        resume: LLMService | None = None,
        no_feat: bool = False,
        debug: bool = False,
    ) -> int:
        """Count the tokens in the prompt using tiktoken estimation.

        Args:
            repo (git.Repo): The repository to count the tokens for.
            explanation (str, optional): The explanation of the changes. Defaults to None.
            resume (LLMService, optional): The resume of the changes. Defaults to None.

        Returns:
            int: The estimated number of tokens in the prompt.
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
    def resume_changes(self, repo: Repo, explanation: str | None = None) -> str | None:
        """Resume changes.

        Args:
            repo (git.Repo): The repository to resume the changes for.
            explanation (str, optional): The explanation of the changes. Defaults to None.
        """
        raise NotImplementedError("OpenRouter LLM does not support resume changes")

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
        self.database.start()
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
            return None

        body: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt.system_prompt},
                {"role": "user", "content": prompt.user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        if self.providers:
            body["provider"] = {
                "only": self.providers,
            }

        response = requests.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=120,
        )

        response.raise_for_status()
        data = response.json()

        if data is None:
            return None

        if "usage" in data:
            self.database.insert_token_usage(
                data["usage"]["total_tokens"], f"openrouter/{self.model}"
            )

        content = data["choices"][0]["message"]["content"]
        return CommitMessage.model_validate_json(content)

    @override
    def supports(self, action: LLMAction) -> bool:
        """Check if the LLM supports the action.

        Args:
            action (str): The action to check.

        Returns:
            bool: True if the LLM supports the action, False otherwise.
        """
        return action in [
            LLMAction.COUNT_TOKENS,
            LLMAction.TOKENS_USED,
            LLMAction.COMMIT_MESSAGE,
        ]
