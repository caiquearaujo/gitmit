"""
Change Analyzer Module.

This module provides deterministic analysis of git changes to help
the LLM understand the context and magnitude of modifications.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

from ..resources.files import File


class ChangeMagnitude(Enum):
    """Magnitude of changes - helps LLM calibrate response appropriately."""

    TRIVIAL = "trivial"  # Typos, single variable renames, whitespace
    SMALL = "small"  # Few lines changed, minor tweaks
    MEDIUM = "medium"  # Moderate changes, new functions/methods
    LARGE = "large"  # Significant refactoring, multiple files
    MAJOR = "major"  # Architecture changes, new modules


class ChangeCategory(Enum):
    """Primary category of changes - suggests likely commit type."""

    NEW_FILES = "new_files"  # Primarily adding new files
    MODIFICATIONS = "modifications"  # Primarily modifying existing files
    MIXED = "mixed"  # Both new and modified files
    DELETIONS = "deletions"  # Primarily removing code/files
    RENAME_REFACTOR = "rename_refactor"  # Variable/function renames
    CONFIG = "config"  # Configuration files
    DOCUMENTATION = "documentation"  # Docs, comments, README
    TESTS = "tests"  # Test files
    DEPENDENCIES = "dependencies"  # Package management files


@dataclass
class FileAnalysis:
    """Analysis of a single file's changes."""

    filename: str
    is_new: bool
    lines_added: int = 0
    lines_removed: int = 0
    is_config: bool = False
    is_test: bool = False
    is_doc: bool = False
    is_dependency: bool = False
    has_function_changes: bool = False
    has_class_changes: bool = False
    rename_only: bool = False

    @property
    def total_changes(self) -> int:
        return self.lines_added + self.lines_removed

    @property
    def net_changes(self) -> int:
        return self.lines_added - self.lines_removed


@dataclass
class ChangeAnalysis:
    """Complete analysis of all changes in the repository."""

    magnitude: ChangeMagnitude
    category: ChangeCategory
    total_files: int
    new_files_count: int
    modified_files_count: int
    total_lines_added: int
    total_lines_removed: int
    file_analyses: list[FileAnalysis] = field(default_factory=list)
    suggested_types: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    context_hints: list[str] = field(default_factory=list)

    @property
    def net_changes(self) -> int:
        return self.total_lines_added - self.total_lines_removed

    def to_context_string(self) -> str:
        """Generate a context string for the LLM prompt."""
        lines = [
            f"CHANGE MAGNITUDE: {self.magnitude.value.upper()}",
            f"CHANGE CATEGORY: {self.category.value.upper()}",
            f"FILES: {self.total_files} total ({self.new_files_count} new, {self.modified_files_count} modified)",
            f"LINES: +{self.total_lines_added} -{self.total_lines_removed} (net: {self.net_changes:+d})",
        ]

        if self.suggested_types:
            lines.append(f"SUGGESTED TYPES: {', '.join(self.suggested_types)}")

        if self.warnings:
            lines.append("WARNINGS:")
            for warning in self.warnings:
                lines.append(f"  ⚠️ {warning}")

        if self.context_hints:
            lines.append("CONTEXT HINTS:")
            for hint in self.context_hints:
                lines.append(f"  • {hint}")

        return "\n".join(lines)


class ChangeAnalyzer:
    """
    Analyzes git changes to provide context for LLM prompt generation.

    This class performs deterministic analysis of changes to help the LLM
    understand the scope, magnitude, and likely category of modifications.
    """

    # File patterns for categorization
    CONFIG_PATTERNS = [
        r"\.json$",
        r"\.ya?ml$",
        r"\.toml$",
        r"\.ini$",
        r"\.cfg$",
        r"\.env",
        r"Makefile$",
        r"Dockerfile$",
        r"\.conf$",
        r"pyproject\.toml$",
        r"setup\.py$",
        r"setup\.cfg$",
        r"tsconfig\.json$",
        r"package\.json$",
        r"\.eslintrc",
        r"\.prettierrc",
        r"\.gitignore$",
        r"\.dockerignore$",
    ]

    TEST_PATTERNS = [
        r"test[_/]",
        r"_test\.py$",
        r"\.test\.[jt]sx?$",
        r"spec[_/]",
        r"\.spec\.[jt]sx?$",
        r"__tests__/",
        r"tests?\.py$",
        r"conftest\.py$",
    ]

    DOC_PATTERNS = [
        r"README",
        r"CHANGELOG",
        r"LICENSE",
        r"CONTRIBUTING",
        r"\.md$",
        r"\.rst$",
        r"\.txt$",
        r"docs?/",
        r"\.adoc$",
    ]

    DEPENDENCY_PATTERNS = [
        r"requirements.*\.txt$",
        r"Pipfile",
        r"poetry\.lock$",
        r"package-lock\.json$",
        r"yarn\.lock$",
        r"pnpm-lock\.yaml$",
        r"go\.mod$",
        r"go\.sum$",
        r"Cargo\.toml$",
        r"Cargo\.lock$",
        r"Gemfile",
        r"composer\.json$",
        r"composer\.lock$",
    ]

    # Patterns that suggest specific changes
    FUNCTION_PATTERNS = [
        r"^[\+\-]\s*(def |async def |function |const \w+ = \(|const \w+ = async)",
        r"^[\+\-]\s*(export (default )?(function|const))",
    ]

    CLASS_PATTERNS = [
        r"^[\+\-]\s*class \w+",
        r"^[\+\-]\s*export (default )?class",
    ]

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        self._config_re = [re.compile(p, re.IGNORECASE) for p in self.CONFIG_PATTERNS]
        self._test_re = [re.compile(p, re.IGNORECASE) for p in self.TEST_PATTERNS]
        self._doc_re = [re.compile(p, re.IGNORECASE) for p in self.DOC_PATTERNS]
        self._dep_re = [re.compile(p, re.IGNORECASE) for p in self.DEPENDENCY_PATTERNS]
        self._func_re = [re.compile(p, re.MULTILINE) for p in self.FUNCTION_PATTERNS]
        self._class_re = [re.compile(p, re.MULTILINE) for p in self.CLASS_PATTERNS]

    def _matches_any(self, text: str, patterns: List[re.Pattern[str]]) -> bool:
        """Check if text matches any of the compiled patterns."""
        return any(p.search(text) for p in patterns)

    def _categorize_file(self, filename: str) -> Dict[str, bool]:
        """Categorize a file based on its name/path."""
        return {
            "is_config": self._matches_any(filename, self._config_re),
            "is_test": self._matches_any(filename, self._test_re),
            "is_doc": self._matches_any(filename, self._doc_re),
            "is_dependency": self._matches_any(filename, self._dep_re),
        }

    def _analyze_diff_content(self, content: str) -> Dict[str, Any]:
        """Analyze diff content for specific patterns."""
        has_function_changes = self._matches_any(content, self._func_re)
        has_class_changes = self._matches_any(content, self._class_re)

        # Count actual changes (lines starting with + or -)
        lines_added = len(re.findall(r"^\+[^+]", content, re.MULTILINE))
        lines_removed = len(re.findall(r"^-[^-]", content, re.MULTILINE))

        # Detect rename-only changes (similar removed/added with small differences)
        rename_only = self._detect_rename_only(content, lines_added, lines_removed)

        return {
            "has_function_changes": has_function_changes,
            "has_class_changes": has_class_changes,
            "lines_added": lines_added,
            "lines_removed": lines_removed,
            "rename_only": rename_only,
        }

    def _detect_rename_only(self, content: str, added: int, removed: int) -> bool:
        """
        Detect if changes are primarily variable/function renames.

        This is a heuristic: if added ≈ removed and changes are small,
        it's likely a rename operation.
        """
        if added == 0 or removed == 0:
            return False

        # Small changes with balanced add/remove
        if added <= 10 and removed <= 10:
            ratio = min(added, removed) / max(added, removed)
            if ratio > 0.7:  # Within 30% of each other
                return True

        return False

    def _analyze_new_file(self, filename: str, content: str) -> FileAnalysis:
        """Analyze a new (untracked) file."""
        categories = self._categorize_file(filename)
        lines = content.count("\n") + (
            1 if content and not content.endswith("\n") else 0
        )

        has_functions = self._matches_any(content, self._func_re)
        has_classes = self._matches_any(content, self._class_re)

        return FileAnalysis(
            filename=filename,
            is_new=True,
            lines_added=lines,
            lines_removed=0,
            has_function_changes=has_functions,
            has_class_changes=has_classes,
            **categories,
        )

    def _analyze_modified_file(self, filename: str, diff_content: str) -> FileAnalysis:
        """Analyze a modified file."""
        categories = self._categorize_file(filename)
        diff_analysis = self._analyze_diff_content(diff_content)

        return FileAnalysis(
            filename=filename, is_new=False, **categories, **diff_analysis
        )

    def _determine_magnitude(self, analyses: list[FileAnalysis]) -> ChangeMagnitude:
        """Determine the magnitude of changes based on file analyses."""
        if not analyses:
            return ChangeMagnitude.TRIVIAL

        total_files = len(analyses)
        total_changes = sum(a.total_changes for a in analyses)
        has_structural = any(
            a.has_function_changes or a.has_class_changes for a in analyses
        )
        all_rename = all(a.rename_only for a in analyses if not a.is_new)

        # Trivial: very small changes, likely typos or renames
        if total_changes <= 5 and total_files == 1:
            if all_rename or not has_structural:
                return ChangeMagnitude.TRIVIAL

        # Small: minor changes
        if total_changes <= 30 and total_files <= 2:
            return ChangeMagnitude.SMALL

        # Medium: moderate changes
        if total_changes <= 150 and total_files <= 5:
            return ChangeMagnitude.MEDIUM

        # Large: significant changes
        if total_changes <= 500 and total_files <= 15:
            return ChangeMagnitude.LARGE

        # Major: very significant changes
        return ChangeMagnitude.MAJOR

    def _determine_category(self, analyses: list[FileAnalysis]) -> ChangeCategory:
        """Determine the primary category of changes."""
        if not analyses:
            return ChangeCategory.MODIFICATIONS

        new_files = [a for a in analyses if a.is_new]
        modified_files = [a for a in analyses if not a.is_new]

        # Check for specialized categories first
        all_tests = all(a.is_test for a in analyses)
        all_docs = all(a.is_doc for a in analyses)
        all_config = all(a.is_config for a in analyses)
        all_deps = all(a.is_dependency for a in analyses)
        all_rename = (
            all(a.rename_only for a in modified_files) if modified_files else False
        )

        if all_tests:
            return ChangeCategory.TESTS
        if all_docs:
            return ChangeCategory.DOCUMENTATION
        if all_config:
            return ChangeCategory.CONFIG
        if all_deps:
            return ChangeCategory.DEPENDENCIES
        if all_rename and not new_files:
            return ChangeCategory.RENAME_REFACTOR

        # Check for deletions (more removed than added)
        total_removed = sum(a.lines_removed for a in analyses)
        total_added = sum(a.lines_added for a in analyses)
        if total_removed > total_added * 2 and not new_files:
            return ChangeCategory.DELETIONS

        # Mixed or primary category
        if new_files and modified_files:
            # Determine which is more significant
            new_lines = sum(a.lines_added for a in new_files)
            mod_lines = sum(a.total_changes for a in modified_files)

            if new_lines > mod_lines * 2:
                return ChangeCategory.NEW_FILES
            elif mod_lines > new_lines * 2:
                return ChangeCategory.MODIFICATIONS
            return ChangeCategory.MIXED

        if new_files:
            return ChangeCategory.NEW_FILES

        return ChangeCategory.MODIFICATIONS

    def _suggest_commit_types(
        self, analyses: list[FileAnalysis], category: ChangeCategory
    ) -> list[str]:
        """Suggest appropriate commit types based on analysis."""
        suggestions = []

        # Category-based suggestions
        category_suggestions = {
            ChangeCategory.TESTS: ["test"],
            ChangeCategory.DOCUMENTATION: ["docs"],
            ChangeCategory.CONFIG: ["chore", "build", "ci"],
            ChangeCategory.DEPENDENCIES: [
                "dependencies",
                "devDependencies",
                "peerDependencies",
            ],
            ChangeCategory.RENAME_REFACTOR: ["refactor", "style"],
            ChangeCategory.DELETIONS: ["refactor", "chore"],
        }

        if category in category_suggestions:
            suggestions.extend(category_suggestions[category])

        # Content-based suggestions
        has_new_functions = any(a.has_function_changes and a.is_new for a in analyses)
        has_new_classes = any(a.has_class_changes and a.is_new for a in analyses)
        has_modified_functions = any(
            a.has_function_changes and not a.is_new for a in analyses
        )

        # Only suggest 'feat' for genuinely new functionality
        if has_new_classes or (
            has_new_functions and category == ChangeCategory.NEW_FILES
        ):
            suggestions.insert(0, "feat")

        # Suggest enhancement for improvements to existing code
        if has_modified_functions and category == ChangeCategory.MODIFICATIONS:
            suggestions.insert(0, "enhancement")
            suggestions.append("refactor")

        # Always include some fallbacks
        if not suggestions:
            if category == ChangeCategory.NEW_FILES:
                suggestions = ["feat", "chore"]
            else:
                suggestions = ["enhancement", "refactor", "chore"]

        return list(dict.fromkeys(suggestions))  # Remove duplicates preserving order

    def _generate_warnings(
        self, analyses: list[FileAnalysis], magnitude: ChangeMagnitude
    ) -> list[str]:
        """Generate warnings to help the LLM avoid common mistakes."""
        warnings = []

        # Warn about trivial changes being classified as features
        if magnitude == ChangeMagnitude.TRIVIAL:
            warnings.append(
                "This is a TRIVIAL change. Do NOT use 'feat' unless explicitly requested. "
                "Consider: style, refactor, chore, or docs."
            )

        # Warn about rename-only changes
        rename_files = [a for a in analyses if a.rename_only]
        if rename_files:
            warnings.append(
                f"Files with rename-like patterns detected: {[a.filename for a in rename_files]}. "
                "Consider 'refactor' or 'style' instead of 'feat'."
            )

        # Warn about test-only changes
        test_files = [a for a in analyses if a.is_test]
        if test_files and all(a.is_test for a in analyses):
            warnings.append("All changes are in test files. Use 'test' commit type.")

        # Warn about config-only changes
        config_files = [a for a in analyses if a.is_config]
        if config_files and all(a.is_config for a in analyses):
            warnings.append(
                "All changes are in configuration files. Consider 'chore', 'build', or 'ci'."
            )

        return warnings

    def _generate_context_hints(self, analyses: list[FileAnalysis]) -> list[str]:
        """Generate context hints to help the LLM understand the changes."""
        hints = []

        # File type breakdown
        new_files = [a for a in analyses if a.is_new]
        modified_files = [a for a in analyses if not a.is_new]

        if new_files:
            hints.append(
                f"New files: {', '.join(a.filename for a in new_files[:5])}"
                + (f" (+{len(new_files) - 5} more)" if len(new_files) > 5 else "")
            )

        if modified_files:
            hints.append(
                f"Modified files: {', '.join(a.filename for a in modified_files[:5])}"
                + (
                    f" (+{len(modified_files) - 5} more)"
                    if len(modified_files) > 5
                    else ""
                )
            )

        # Structural changes
        struct_files = [
            a for a in analyses if a.has_class_changes or a.has_function_changes
        ]
        if struct_files:
            hints.append(
                f"Files with structural changes (classes/functions): {len(struct_files)}"
            )

        return hints

    def analyze(self, files: List[File]) -> ChangeAnalysis:
        """
        Analyze a list of File objects and return a comprehensive analysis.

        Args:
            files: List of File objects with name, content, and type attributes.

        Returns:
            ChangeAnalysis with magnitude, category, and context information.
        """
        file_analyses = []

        for file in files:
            is_new = file.type.value == "untracked"

            if is_new:
                analysis = self._analyze_new_file(file.name, file.content)
            else:
                analysis = self._analyze_modified_file(file.name, file.content)

            file_analyses.append(analysis)

        magnitude = self._determine_magnitude(file_analyses)
        category = self._determine_category(file_analyses)
        suggested_types = self._suggest_commit_types(file_analyses, category)
        warnings = self._generate_warnings(file_analyses, magnitude)
        context_hints = self._generate_context_hints(file_analyses)

        return ChangeAnalysis(
            magnitude=magnitude,
            category=category,
            total_files=len(file_analyses),
            new_files_count=sum(1 for a in file_analyses if a.is_new),
            modified_files_count=sum(1 for a in file_analyses if not a.is_new),
            total_lines_added=sum(a.lines_added for a in file_analyses),
            total_lines_removed=sum(a.lines_removed for a in file_analyses),
            file_analyses=file_analyses,
            suggested_types=suggested_types,
            warnings=warnings,
            context_hints=context_hints,
        )
