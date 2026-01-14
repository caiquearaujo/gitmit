"""Commit message."""

from datetime import datetime

from git.repo import Repo
from pydantic import BaseModel
from rich.panel import Panel

from ..llms import LLMAction
from ..resources.types import (
    CommitMessage,
    CommitType,
    CommitTypeProps,
    get_commit_types,
)
from ..services.config import Services
from ..services.git import GitService
from ..utils.terminal import (
    ask,
    ask_confirmation,
    choose,
    console,
    display_error,
    display_info,
    display_warning,
)


class CommitSettings(BaseModel):
    push: bool = False
    force: bool = False
    mode: str | None = None
    brief: str | None = None
    no_feat: bool = False
    debug: bool = False
    dry_run: bool = False


class CommitTool:
    """Commit tool."""

    def __init__(
        self, git_service: GitService, services: Services, settings: CommitSettings
    ):
        """Initialize the commit tool."""

        if not git_service.exists():
            raise ValueError("No git repository found.")

        self.git_service: GitService = git_service
        self.services: Services = services
        self.settings: CommitSettings = settings

    def run(self):
        """Run the commit tool."""
        branch = self.git_service.currentBranch()

        if self.git_service.hasChanges() is False:
            display_warning("No changes to commit.")
            return

        if self.settings.mode is None:
            mode = choose(
                "Set your commit mode",
                ["🤖 Generated", "🥵 Manual", "❌ Abort"],
                default=1,
                clean=False,
            )
        else:
            mode = {
                "manual": 1,
                "ai": 0,
            }[self.settings.mode]

        if mode == 2:
            return

        action = {
            0: lambda: self.__llm_commit(),
            1: lambda: self.__manual_commit(),
        }

        message = action[mode]()

        if message is None:
            return

        display_info(
            Panel(
                f"[white]{message}[/white]",
                title="Preview",
            )
        )

        if not self.settings.force:
            keep = ask_confirmation(
                "Ready to commit?",
                default="y",
                clean=False,
            )

            if not keep:
                message = self.__manual_commit()

                if message is None:
                    return

                return

        if self.settings.dry_run:
            display_warning("[DRY-RUN] Commit and push skipped.")
        else:
            self.git_service.commit(message)

            if self.settings.push:
                self.__push_to_remote(branch)

    def __llm_commit(self):
        """Commit using LLM."""
        if self.services.commit.supports(LLMAction.COMMIT_MESSAGE) is False:
            raise ValueError("Selected LLM does not support commit message generation.")

        console.print(Panel("> Generating your commit message", style="bold cyan"))
        current_usage = 0

        # @note first, check local usage to grant it can call LLM later
        if self.services.commit.supports(LLMAction.TOKENS_USED):
            current_usage = self.services.commit.tokens_used()

            display_info(
                Panel(
                    f"Current usage: [bold green]{format(current_usage, ',')} tokens[/bold green] [white]{datetime.now().strftime('%Y-%m')}[/white]",
                    title="Token Usage",
                )
            )

            if not self.settings.force:
                keep = ask_confirmation(
                    "Do you want to continue?",
                    default="y",
                    clean=False,
                )

                if not keep:
                    return self.__manual_commit()

        # @note second, estimate count usage for current prompt
        if self.services.commit.supports(LLMAction.COUNT_TOKENS):
            response = self.services.commit.count_tokens(
                self.__get_repo(), explanation=None, resume=self.services.resume
            )

            display_info(
                Panel(
                    (
                        f"Estimated usage: [bold green]~{format(response, ',')} tokens[/bold green]\n"
                        f"Calculated usage: [bold green]~{format(current_usage + response, ',')} tokens[/bold green]"
                    ),
                    title="Token Usage",
                )
            )

            if not self.settings.force:
                keep = ask_confirmation(
                    "Do you want to continue?",
                    default="y",
                    clean=False,
                )

                if not keep:
                    return self.__manual_commit()

        # @note generate commit message
        if self.settings.brief is None:
            explanation = ask(
                "[bold yellow]?[/bold yellow] May briefly explain your changes",
                required=False,
                default=None,
                clean=False,
            )
        else:
            explanation = self.settings.brief

        commit_message = self.services.commit.commit_message(
            self.__get_repo(),
            explanation=explanation,
            resume=self.services.resume,
            no_feat=self.settings.no_feat,
            debug=self.settings.debug,
        )

        if commit_message is None:
            display_error(
                "Cannot generate a commit message right now, changing to manual mode"
            )

            return self.__manual_commit()

        founded_type = CommitTypeProps(
            commit_title=commit_message.type.value,
            commit_emoji=":bricks:",
            preview_emoji="🧱",
            commit_type=CommitType.OTHER,
            commit_meaning="This commit type is useful when doing other things not related to the other commit types.",
        )

        for _type in get_commit_types():
            if _type.commit_type.name == commit_message.type.name:
                founded_type = _type
                break

        display_info(
            Panel(
                f"[white]{founded_type.preview_emoji} {founded_type.commit_title}: {commit_message.reason}[/white] 👌",
                title="Explanation",
            )
        )

        return self.__formatted_message(
            commit_message,
            founded_type,
        )

    def __manual_commit(self):
        """Commit manually."""
        console.print(Panel("> Build your commit message manually", style="bold cyan"))

        types = get_commit_types()
        display_types = [f"{x.preview_emoji} / {x.commit_title}" for x in types]
        display_types.append("❌ / Abort")

        type = choose(
            "Commit type applyable for your changes",
            display_types,
            clean=False,
        )

        if type == len(display_types) - 1:
            return None

        founded_type = types[type]

        scope = ask("A scope for your commit", required=True, clean=False)
        title = ask("A title for your commit", required=True, clean=False)

        body = ask(
            "[bold yellow]?[/bold yellow] May briefly describe your commit",
            required=False,
            clean=False,
        )

        return self.__formatted_message(
            CommitMessage(
                type=CommitType(founded_type.commit_type),
                scope=scope.lower(),
                short_description=title,
                description=body,
                reason="Manual",
            ),
            founded_type,
        )

    def __formatted_message(
        self, commit_message: CommitMessage, founded_type: CommitTypeProps
    ):
        """Format the commit message.

        Args:
            commit_message (CommitMessage): A commit message.
            founded_type (CommitTypeProps): A founded type.
        """
        message = "{em} {tp}({sc}): {tt}\n\n{b}".format(
            em=founded_type.preview_emoji,
            tp=founded_type.commit_type.value,
            sc=commit_message.scope,
            tt=commit_message.short_description,
            b=commit_message.description,
        )

        return message

    def __push_to_remote(self, branch: str):
        """Push to remote."""
        origin_name = "origin"
        keep_trying = True

        if self.git_service.remoteExists(origin_name) is False:
            while True:
                origin_name = ask(
                    "Set a remote name (origin not found)",
                    required=True,
                    clean=False,
                )

                if self.git_service.remoteExists(origin_name) is False:
                    display_error(
                        "Cannot find any remote with name: " + origin_name,
                    )

                    origin_name = None
                    keep_trying = ask_confirmation(
                        "Do you want to try a new remote name?",
                        default="y",
                        clean=False,
                    )

                    if not keep_trying:
                        return

        self.git_service.pushTo(branch, origin_name)

    def __get_repo(self) -> Repo:
        repo = self.git_service.repo

        if repo is None:
            raise RuntimeError("Cannot get the current git repository...")

        return repo
