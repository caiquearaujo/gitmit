"""Google LLM service."""

from typing import override

from git import Repo
from google import genai
from google.genai import types as genai_types

from ..resources import llms
from ..resources.types import CommitMessage
from ..services.database import LLMUsageDatabaseService
from . import LLMAction, LLMService


class GoogleLLMService(LLMService):
    """Service for the Google LLM."""

    def __init__(
        self,
        api_key: str,
        database: LLMUsageDatabaseService,
        model: str = "gemini-2.0-flash",
    ):
        """Initialize the Google LLM service."""
        self.client: genai.Client = genai.Client(api_key=api_key)
        self.model: str = model
        self.database: LLMUsageDatabaseService = database
        self.generator: llms.CommitPromptGenerator = llms.CommitPromptGenerator()

    @override
    def tokens_used(self) -> int:
        """Get the number of tokens used."""
        self.database.start()
        return self.database.current_month_tokens_used(f"google/{self.model}")

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
        try:
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

            # type: ignore
            tokens = self.client.models.count_tokens(
                model=self.model,
                contents=f"{prompt.system_prompt}\n\n{prompt.user_prompt}",
            )

            return int(getattr(tokens, "total_tokens", 0))
        except Exception:
            return 0

    @override
    def resume_changes(self, repo: Repo, explanation: str | None = None) -> str | None:
        """Resume changes.

        Args:
            repo (git.Repo): The repository to resume the changes for.
            explanation (str, optional): The explanation of the changes. Defaults to None.
        """
        raise NotImplementedError("Google LLM does not support resume changes")

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

        # type: ignore
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt.user_prompt,
            config=genai_types.GenerateContentConfig(
                system_instruction=prompt.system_prompt,
                response_mime_type="application/json",
                response_schema=CommitMessage,
            ),
        )

        text = response.text
        total = int(getattr(response.usage_metadata, "total_token_count", 0))

        self.database.insert_token_usage(total, f"google/{self.model}")

        if text is None:
            return None

        return CommitMessage.model_validate_json(text)

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
