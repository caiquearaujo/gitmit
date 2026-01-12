"""Utilities for the LLM."""

from dataclasses import dataclass
from pathlib import Path
from typing import List

import git

from .analyzer import ChangeAnalysis, ChangeAnalyzer
from .files import (
    File,
    _get_gitignore_parser,
    load_all,
    load_modified_files,
    load_untracked_files,
)
from .prompts import PromptBuilder, PromptPair
from .types import get_commit_types_resume


@dataclass
class CommitPromptResult:
    """Result of building a commit prompt."""

    prompt_pair: PromptPair
    analysis: ChangeAnalysis
    raw_changes: str

    @property
    def system_prompt(self) -> str:
        return self.prompt_pair.system_prompt

    @property
    def user_prompt(self) -> str:
        return self.prompt_pair.user_prompt

    def to_single_prompt(self) -> str:
        """
        Combine system and user prompts into a single string.
        Use this for models/APIs that don't support separate system prompts.
        """
        return f"{self.system_prompt}\n\n---\n\n{self.user_prompt}"


class CommitPromptGenerator:
    """
    Generates prompts for commit message creation.

    This class orchestrates:
    - Loading files from the repository
    - Analyzing changes for context
    - Building appropriate prompts based on analysis
    """

    def __init__(self, prompts_dir: Path | None = None):
        """
        Initialize the generator.

        Args:
            prompts_dir: Optional custom directory for prompt templates.
        """
        self.analyzer = ChangeAnalyzer()
        self.builder = PromptBuilder(prompts_dir)

    def generate(
        self,
        repo: git.Repo,
        explanation: str | None = None,
        no_feat: bool = False,
        debug: bool = False,
    ) -> CommitPromptResult | None:
        """
        Generate prompts for commit message creation.

        Args:
            repo: Git repository to analyze
            explanation: Optional user explanation of changes
            no_feat: If True, explicitly discourage 'feat' type
            debug: If True, print debug information

        Returns:
            CommitPromptResult or None if no changes found
        """
        # Load files
        parser = _get_gitignore_parser(repo)
        untracked = load_untracked_files(repo, parser)
        modified = load_modified_files(repo, parser)
        files = untracked + modified

        if not files:
            return None

        # Analyze changes
        analysis = self.analyzer.analyze(files)

        if debug:
            self._print_debug(analysis, files)

        # Build raw changes string
        raw_changes = self._build_changes_string(files)

        # Build prompts
        prompt_pair = self.builder.build_commit_prompt(
            changes_content=raw_changes,
            commit_types_csv=get_commit_types_resume(),
            analysis=analysis,
            user_explanation=explanation,
            no_feat=no_feat,
        )

        return CommitPromptResult(
            prompt_pair=prompt_pair,
            analysis=analysis,
            raw_changes=raw_changes,
        )

    def generate_from_resume(
        self,
        resume: str,
        explanation: str | None = None,
        no_feat: bool = False,
    ) -> PromptPair:
        """
        Generate prompts from a pre-computed resume.

        This is useful when you want to generate a commit message
        from a summary rather than raw changes.

        Args:
            resume: Pre-computed summary of changes
            explanation: Optional user explanation
            no_feat: If True, explicitly discourage 'feat' type

        Returns:
            PromptPair for commit message generation
        """
        # For resume-based generation, we use MEDIUM magnitude as default
        # since we don't have the raw files to analyze
        from .analyzer import ChangeAnalysis, ChangeCategory, ChangeMagnitude

        # Create a synthetic analysis for template selection
        synthetic_analysis = ChangeAnalysis(
            magnitude=ChangeMagnitude.MEDIUM,
            category=ChangeCategory.MIXED,
            total_files=0,
            new_files_count=0,
            modified_files_count=0,
            total_lines_added=0,
            total_lines_removed=0,
            context_hints=["Generated from resume - detailed analysis not available"],
        )

        return self.builder.build_commit_prompt(
            changes_content=resume,
            commit_types_csv=get_commit_types_resume(),
            analysis=synthetic_analysis,
            user_explanation=explanation,
            no_feat=no_feat,
        )

    def _build_changes_string(self, files: List[File]) -> str:
        """Build the raw changes string from file list."""
        txt = []
        for file in files:
            txt.append(f">>>> {file.name} ({file.type.value})")
            txt.append(file.content)
            txt.append("<<<< end of file")
        return "\n".join(txt)

    def _print_debug(self, analysis: ChangeAnalysis, files: List[File]):
        """Print debug information about the analysis."""
        # Import here to avoid circular dependency
        try:
            from ..utils.terminal import Panel, display_info

            files_info = "\n".join(
                [f"{file.name} ({file.type.value})" for file in files]
            )

            display_info(
                Panel(
                    files_info,
                    style="bold yellow",
                    title="(Debug) Files related to commit",
                )
            )

            display_info(
                Panel(
                    analysis.to_context_string(),
                    style="bold cyan",
                    title="(Debug) Change Analysis",
                )
            )
        except ImportError:
            # Fallback if terminal utils not available
            print("=== Debug: Files ===")
            for file in files:
                print(f"  {file.name} ({file.type.value})")
            print("\n=== Debug: Analysis ===")
            print(analysis.to_context_string())


def generate_resume_prompt(
    repo: git.Repo,
    explanation: str | None = None,
    prompts_dir: Path | None = None,
) -> str | None:
    """
    Generate a prompt for summarizing repository changes.

    Args:
        repo: Git repository to analyze
        explanation: Optional user explanation
        prompts_dir: Optional custom prompts directory

    Returns:
        Prompt string or None if no changes
    """
    changes = load_all(repo)

    if changes is None:
        return None

    builder = PromptBuilder(prompts_dir)
    return builder.build_resume_prompt(changes, explanation)
