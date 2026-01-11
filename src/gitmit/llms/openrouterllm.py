"""OpenRouter LLM service."""

from typing import Optional, List

import requests
import tiktoken
from git import Repo

from . import LLMService, LLMAction
from ..resources.types import CommitMessage
from ..services.database import LLMUsageDatabaseService
from ..resources import llms


class OpenRouterLLMService(LLMService):
    """Service for the OpenRouter LLM."""

    def __init__(
        self,
        api_key: str,
        database: LLMUsageDatabaseService,
        model: str = "anthropic/claude-3.5-sonnet",
        providers: Optional[List[str]] = None,
    ):
        """Initialize the OpenRouter LLM service.

        Args:
            api_key (str): The OpenRouter API key.
            database (LLMUsageDatabaseService): The database service for token tracking.
            model (str, optional): The model to use. Defaults to "anthropic/claude-3.5-sonnet".
            providers (list[str], optional): List of providers to prioritize. Defaults to None.
        """
        self.api_key = api_key
        self.model = model
        self.database = database
        self.providers = [p.strip() for p in providers if p.strip()] if providers else None
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def tokens_used(self) -> int:
        """Get the number of tokens used."""
        self.database.start()
        return self.database.current_month_tokens_used(f"openrouter/{self.model}")

    def count_tokens(
        self,
        repo: Repo,
        explanation: Optional[str] = None,
        resume: Optional["LLMService"] = None,
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
            prompt = llms.prompt_commit_from_resume(
                resume.resume_changes(repo, explanation), explanation
            )
        else:
            prompt = llms.prompt_commit_from_files(repo, explanation)

        if prompt is None:
            return 0

        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(prompt))

    def resume_changes(
        self, repo: Repo, explanation: Optional[str] = None
    ) -> Optional[str]:
        """Resume changes.

        Args:
            repo (git.Repo): The repository to resume the changes for.
            explanation (str, optional): The explanation of the changes. Defaults to None.
        """
        raise NotImplementedError("OpenRouter LLM does not support resume changes")

    def commit_message(
        self,
        repo: Repo,
        explanation: Optional[str] = None,
        resume: Optional[LLMService] = None,
        no_feat: bool = False,
        debug: bool = False,
    ) -> Optional[CommitMessage]:
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
            prompt = llms.prompt_commit_from_resume(
                resume.resume_changes(repo, explanation), explanation
            )
        else:
            prompt = llms.prompt_commit_from_files(repo, explanation, no_feat, debug)

        if prompt is None:
            return None

        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }

        if self.providers:
            body["provider"] = {
                "order": self.providers,
                "allow_fallbacks": True,
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
