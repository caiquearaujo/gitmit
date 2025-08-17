"""Merge tool for merging branches."""

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


class MergeSettings(BaseModel):
    origin: str = "dev"
    destination: str = "main"
    push: bool = False


class MergeTool:
    """Merge tool for merging branches following GitFlow."""

    def __init__(
        self, git_service: GitService, services: Services, settings: MergeSettings
    ):
        """Initialize the merge tool."""

        if not git_service.exists():
            raise ValueError("No git repository found.")

        self.git_service = git_service
        self.services = services
        self.settings = settings

    def run(self):
        """Run the merge tool."""

        origin = self.settings.origin
        destination = self.settings.destination

        display_info(
            Panel(
                f"Origin: [bold yellow]{origin}[/bold yellow]\n"
                f"Destination: [bold yellow]{destination}[/bold yellow]\n"
                f"Push: [bold yellow]{'Yes' if self.settings.push else 'No'}[/bold yellow]",
                title="Merge Configuration",
            )
        )

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
                "Please commit or stash them before merging."
            )
            return

        try:
            # Step 3: Push origin to remote if push is enabled
            if self.settings.push:
                display_info(f"Pushing {origin} to remote...")
                self.git_service.pushTo(origin)
                display_success(f"Successfully pushed {origin} to remote.")

            # Step 4: Checkout to destination branch
            display_info(f"Switching to {destination} branch...")
            self.git_service.checkout(destination)

            # Step 5: Pull destination and check for changes
            display_info(f"Pulling latest changes from {destination}...")
            pull_result = self.git_service.pull()

            # Check if there were updates
            if pull_result and "Already up to date" not in str(pull_result):
                display_warning(
                    f"The {destination} branch was updated from remote. "
                    "Please review the changes before proceeding with the merge."
                )
                # Switch back to origin branch
                self.git_service.checkout(origin)
                return

            # Step 6: Merge origin into destination with --no-ff
            display_info(f"Merging {origin} into {destination}...")
            self.git_service.merge(origin)
            display_success(f"Successfully merged {origin} into {destination}.")

            # Step 7: Push destination to remote if push is enabled
            if self.settings.push:
                display_info(f"Pushing {destination} to remote...")
                self.git_service.pushTo(destination)
                display_success(f"Successfully pushed {destination} to remote.")
            else:
                display_info(
                    f"Merge completed locally. Use 'git push' to push {destination} to remote."
                )

            display_success(
                Panel(
                    f"✅ Successfully merged [bold green]{origin}[/bold green] "
                    f"into [bold green]{destination}[/bold green]",
                    title="Merge Complete",
                )
            )

        except Exception as e:
            display_error(f"Merge failed: {e}")
            # Try to return to origin branch if something went wrong
            try:
                current = self.git_service.currentBranch()
                if current != origin:
                    display_info(f"Returning to {origin} branch...")
                    self.git_service.checkout(origin)
            except:
                pass
