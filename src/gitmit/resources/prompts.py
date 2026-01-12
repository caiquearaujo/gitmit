"""
Prompt Builder Module.

This module handles loading, caching, and rendering prompt templates
for commit message generation.
"""

import pkgutil
import re
from dataclasses import dataclass
from pathlib import Path

from .analyzer import ChangeAnalysis, ChangeMagnitude


@dataclass
class PromptPair:
    """A pair of system and user prompts ready for LLM consumption."""

    system_prompt: str
    user_prompt: str


class PromptBuilder:
    """
    Builds prompts from templates with placeholder substitution.

    This class handles:
    - Loading templates from files
    - Caching loaded templates
    - Selecting appropriate templates based on change analysis
    - Substituting placeholders with actual values
    """

    # Placeholder pattern: {{PLACEHOLDER_NAME}}
    PLACEHOLDER_PATTERN = re.compile(r"\{\{(\w+)\}\}")

    def __init__(self, prompts_dir: Path | None = None):
        """
        Initialize the PromptBuilder.

        Args:
            prompts_dir: Directory containing prompt templates.
                        If None, uses pkgutil to load from package resources.
        """
        self.prompts_dir = Path(prompts_dir) if prompts_dir else None
        self._cache: dict[str, str] = {}

    def _load_template(self, name: str) -> str:
        """
        Load a template file, using cache if available.

        Args:
            name: Template name (without .txt extension)

        Returns:
            Template content as string

        Raises:
            FileNotFoundError: If template doesn't exist
        """
        if name in self._cache:
            return self._cache[name]

        if self.prompts_dir:
            template_path = self.prompts_dir / f"{name}.txt"

            if not template_path.exists():
                raise FileNotFoundError(
                    f"Template '{name}' not found at {template_path}"
                )

            content = template_path.read_text(encoding="utf-8")
        else:
            try:
                data = pkgutil.get_data("gitmit.resources", f".prompts/{name}.txt")

                if data is None:
                    raise FileNotFoundError()

                content = data.decode("utf-8")
            except (FileNotFoundError, ModuleNotFoundError):
                template_path = Path(__file__).parent / ".prompts" / f"{name}.txt"

                if not template_path.exists():
                    raise FileNotFoundError(
                        f"Template '{name}' not found in package or at {template_path}"
                    )

                content = template_path.read_text(encoding="utf-8")

        self._cache[name] = content
        return content

    def _substitute(self, template: str, values: dict[str, str]) -> str:
        """
        Substitute placeholders in template with values.

        Args:
            template: Template string with {{PLACEHOLDER}} markers
            values: Dictionary mapping placeholder names to values

        Returns:
            Template with placeholders replaced
        """

        def replacer(match: re.Match[str]) -> str:
            key = match.group(1)
            return values.get(key, match.group(0))

        return self.PLACEHOLDER_PATTERN.sub(replacer, template)

    def _select_user_template(self, magnitude: ChangeMagnitude) -> str:
        """
        Select the appropriate user template based on change magnitude.

        Args:
            magnitude: The analyzed change magnitude

        Returns:
            Template name to use
        """
        if magnitude in (ChangeMagnitude.TRIVIAL, ChangeMagnitude.SMALL):
            return "small_changes"
        elif magnitude == ChangeMagnitude.MEDIUM:
            return "medium_changes"
        else:  # LARGE, MAJOR
            return "major_changes"

    def _format_user_explanation_section(self, explanation: str | None) -> str:
        """
        Format the user explanation section for inclusion in prompts.

        Args:
            explanation: User's explanation or None

        Returns:
            Formatted section string
        """
        if not explanation:
            return ""

        return f"""
## USER EXPLANATION (HIGH PRIORITY)
⚠️ **The user has provided context. Use this as your PRIMARY guide for categorization.**

> {explanation}

This explanation should:
1. Guide your choice of commit type
2. Influence your description wording
3. Be reflected in the final message
"""

    def build_commit_prompt(
        self,
        changes_content: str,
        commit_types_csv: str,
        analysis: ChangeAnalysis,
        user_explanation: str | None = None,
        no_feat: bool = False,
    ) -> PromptPair:
        """
        Build a complete prompt pair for commit message generation.

        Args:
            changes_content: Raw string of file changes
            commit_types_csv: CSV string of commit types
            analysis: Pre-computed change analysis
            user_explanation: Optional user explanation
            no_feat: If True, add extra warning against using 'feat'

        Returns:
            PromptPair with system and user prompts
        """
        # Load templates
        system_template = self._load_template("commit_system")
        user_template_name = self._select_user_template(analysis.magnitude)
        user_template = self._load_template(user_template_name)

        # Build user explanation section
        explanation_section = self._format_user_explanation_section(user_explanation)

        # Add no_feat warning if needed
        no_feat_warning = ""

        if no_feat:
            no_feat_warning = """
## ⚠️ EXPLICIT INSTRUCTION: NO FEAT TYPE
The user has indicated this is NOT a feature. Do NOT use the `feat` commit type.
Choose from: enhancement, refactor, chore, bugfix, style, or other appropriate types.
"""

        # Substitute in system prompt
        system_prompt = self._substitute(
            system_template,
            {
                "COMMIT_TYPES_CSV": commit_types_csv,
            },
        )

        # Substitute in user prompt
        user_prompt = self._substitute(
            user_template,
            {
                "CHANGE_ANALYSIS": analysis.to_context_string(),
                "CHANGES": changes_content,
                "USER_EXPLANATION_SECTION": explanation_section + no_feat_warning,
            },
        )

        return PromptPair(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def build_resume_prompt(
        self,
        changes_content: str,
        user_explanation: str | None = None,
    ) -> str:
        """
        Build a prompt for summarizing changes.

        Args:
            changes_content: Raw string of file changes
            user_explanation: Optional user explanation

        Returns:
            Complete prompt string
        """
        template = self._load_template("resume_changes")

        explanation_section = self._format_user_explanation_section(user_explanation)

        return self._substitute(
            template,
            {
                "CHANGES": changes_content,
                "USER_EXPLANATION_SECTION": explanation_section,
            },
        )

    def clear_cache(self):
        """Clear the template cache."""
        self._cache.clear()

    def reload_template(self, name: str) -> str:
        """
        Force reload a specific template.

        Args:
            name: Template name to reload

        Returns:
            Reloaded template content
        """
        if name in self._cache:
            del self._cache[name]
        return self._load_template(name)
