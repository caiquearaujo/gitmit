"""Analyze current repository changes."""

from git.repo import Repo

from ..resources.analyzer import ChangeMagnitude
from ..resources.llms import CommitPromptGenerator
from ..services.config import Services
from ..services.git import GitService
from ..utils.terminal import (
    display_warning,
)


class AnalyzeTool:
    """Analyze tool."""

    def __init__(self, git_service: GitService, services: Services):
        """Initialize the analyze tool."""

        if not git_service.exists():
            raise ValueError("No git repository found.")

        self.git_service: GitService = git_service
        self.services: Services = services

    def run(self):
        """Run the analyze tool."""
        if self.git_service.hasChanges() is False:
            display_warning("No changes to analyze.")
            return

        result = CommitPromptGenerator().generate(self.__get_repo())

        if result:
            analysis = result.analysis

            print(f"Change Magnitude: {analysis.magnitude.value}")
            print(f"Change Category: {analysis.category.value}")
            print(f"Suggested Types: {analysis.suggested_types}")
            print(f"Total Files: {analysis.total_files}")
            print(
                f"Lines Changed: +{analysis.total_lines_added} -{analysis.total_lines_removed}"
            )

            # Custom logic based on analysis
            if analysis.magnitude == ChangeMagnitude.TRIVIAL:
                print("This is a tiny change - consider if a commit is even needed")

            # Warnings from analysis
            for warning in analysis.warnings:
                print(f"Warning: {warning}")

    def __get_repo(self) -> Repo:
        repo = self.git_service.repo

        if repo is False:
            raise RuntimeError("Cannot get the current git repository...")

        return repo
