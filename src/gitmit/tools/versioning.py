"""Versioning tool for managing version tags."""

import re
from pydantic import BaseModel

from ..services.git import GitService
from ..services.config import Services
from ..utils.terminal import (
    display_error,
    display_warning,
    display_info,
    display_success,
    Panel,
)


class VersioningSettings(BaseModel):
    version: str
    origin: str = "main"
    force: bool = False
    push: bool = False


class VersioningTool:
    """Versioning tool for creating and managing version tags."""

    def __init__(
        self, git_service: GitService, services: Services, settings: VersioningSettings
    ):
        """Initialize the versioning tool."""

        if not git_service.exists():
            raise ValueError("No git repository found.")

        self.git_service = git_service
        self.services = services
        self.settings = settings

    def is_valid_semver(self, version: str) -> bool:
        """Check if version string is valid SemVer format.

        Args:
            version (str): Version string to validate.

        Returns:
            bool: True if valid SemVer format, False otherwise.
        """
        # SemVer regex pattern (simplified, covers most cases)
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
        return re.match(pattern, version) is not None

    def run(self):
        """Run the versioning tool."""

        version = self.settings.version
        origin = self.settings.origin
        tag_name = f"{version}"

        display_info(
            Panel(
                f"Version: [bold yellow]{version}[/bold yellow]\n"
                f"Tag: [bold yellow]{tag_name}[/bold yellow]\n"
                f"Origin Branch: [bold yellow]{origin}[/bold yellow]\n"
                f"Force: [bold yellow]{'Yes' if self.settings.force else 'No'}[/bold yellow]\n"
                f"Push: [bold yellow]{'Yes' if self.settings.push else 'No'}[/bold yellow]",
                title="Versioning Configuration",
            )
        )

        # Step 0: Validate SemVer format
        if not self.is_valid_semver(version):
            display_error(
                f"Invalid version format: [bold red]{version}[/bold red]. "
                "Version must be in SemVer format (e.g., 1.0.0, 2.1.3-beta, 3.0.0-rc.1)."
            )
            return

        # Step 1: Check if current branch is the origin branch
        current_branch = self.git_service.currentBranch()
        if current_branch != origin:
            display_error(
                f"Current branch is [bold red]{current_branch}[/bold red], "
                f"but expected [bold yellow]{origin}[/bold yellow]. "
                f"Please checkout to {origin} branch first."
            )
            return

        # Step 2: Check if there are uncommitted changes
        if self.git_service.hasChanges():
            display_error(
                "There are uncommitted changes in the repository. "
                "Please commit or stash them before creating a version tag."
            )
            return

        try:
            # Step 3: Check if tag already exists
            tag_exists = self.git_service.tagExists(tag_name)

            if tag_exists and not self.settings.force:
                display_error(
                    f"Tag [bold red]{tag_name}[/bold red] already exists. "
                    "Use --force to delete and recreate it."
                )
                return

            # Handle force deletion if tag exists
            if tag_exists and self.settings.force:
                display_warning(f"Tag {tag_name} exists. Deleting it...")

                # Delete local tag
                self.git_service.deleteTag(tag_name)
                display_info(f"Deleted local tag {tag_name}.")

                # Delete remote tag if push is enabled
                if self.settings.push:
                    try:
                        self.git_service.deleteRemoteTag(tag_name)
                        display_info(f"Deleted remote tag {tag_name}.")
                    except Exception as e:
                        # Remote tag might not exist, that's okay
                        display_info(
                            f"Remote tag {tag_name} not found or already deleted."
                        )

            # Step 4: Create new tag
            display_info(f"Creating tag {tag_name}...")
            self.git_service.createTag(tag_name, f"Release version {version}")
            display_success(f"Successfully created tag {tag_name}.")

            # Step 5: Push tag if push is enabled
            if self.settings.push:
                display_info(f"Pushing tag {tag_name} to remote...")
                self.git_service.pushTag(tag_name)
                display_success(f"Successfully pushed tag {tag_name} to remote.")
            else:
                display_info(
                    f"Tag created locally. Use 'git push origin {tag_name}' to push it to remote."
                )

            display_success(
                Panel(
                    f"✅ Successfully created version tag [bold green]{tag_name}[/bold green]",
                    title="Versioning Complete",
                )
            )

        except Exception as e:
            display_error(f"Versioning failed: {e}")
