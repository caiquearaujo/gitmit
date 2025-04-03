"""Commit message."""

from pydantic import BaseModel
from src.services.git import GitService
from src.services.config import Services
from src.utils.terminal import Panel, display_info


class InitSettings(BaseModel):
    dev: bool = False
    origin: str = ""


class InitTool:
    """Commit tool."""

    def __init__(
        self, git_service: GitService, services: Services, settings: InitSettings
    ):
        """Initialize the commit tool."""
        self.git_service = git_service
        self.services = services
        self.settings = settings

    def run(self):
        """Run the commit tool."""
        if self.git_service.exists():
            raise ValueError("Git repository already exists. Cannot initialize.")

        display_info(
            Panel(
                (
                    f"Origin: [bold yellow]{self.settings.origin if self.settings.origin else '(not set)'}[/bold yellow]\n"
                    f"Dev branch: [bold yellow]{'yes' if self.settings.dev else 'no'}[/bold yellow]"
                ),
                title="Setup",
            )
        )

        self.git_service.init()
        self.git_service.commit(":tada: initial(repo): First commit")
        self.git_service.renameTo("main")

        if self.settings.origin != "":
            # @todo check if origin is valid
            self.git_service.remote(self.settings.origin, "origin")
            self.git_service.pushTo("main")

        if self.settings.dev:
            self.git_service.createBranch("dev", "origin", True)
