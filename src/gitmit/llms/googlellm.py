"""Google LLM service."""

from typing import Optional

from git import Repo
from google import genai
from google.genai import types as genai_types

from . import LLMService, LLMAction
from ..resources.types import CommitMessage
from ..services.database import LLMUsageDatabaseService
from ..resources import llms


class GoogleLLMService(LLMService):
    """Service for the Google LLM."""

    def __init__(
        self,
        api_key: str,
        database: LLMUsageDatabaseService,
        model: str = "gemini-2.0-flash",
    ):
        """Initialize the Google LLM service."""
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.database = database

    def tokens_used(self) -> int:
        """Get the number of tokens used."""
        return self.database.current_month_tokens_used(f"google/{self.model}")

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
        prompt = None

        if resume is not None:
            prompt = llms.prompt_commit_from_resume(
                resume.resume_changes(repo, explanation), explanation
            )
        else:
            prompt = llms.prompt_commit_from_files(repo, explanation)

        if prompt is None:
            return None

        tokens = self.client.models.count_tokens(
            model=self.model,
            contents=prompt,
        )

        if tokens is None:
            return 0

        return tokens.total_tokens

    def resume_changes(
        self, repo: Repo, explanation: Optional[str] = None
    ) -> Optional[str]:
        """Resume changes.

        Args:
            repo (git.Repo): The repository to resume the changes for.
            explanation (str, optional): The explanation of the changes. Defaults to None.
        """
        raise NotImplementedError("Google LLM does not support resume changes")

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

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CommitMessage,
            ),
        )

        if response is None:
            return None

        self.database.insert_token_usage(
            response.usage_metadata.total_token_count, f"google/{self.model}"
        )
        return CommitMessage.model_validate_json(response.text)

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
