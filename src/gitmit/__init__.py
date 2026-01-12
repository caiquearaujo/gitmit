import signal
import sys

from .services.config import init
from .services.git import GitService
from .tools.analyze import AnalyzeTool
from .tools.commit import CommitSettings, CommitTool
from .tools.config import ConfigTool
from .tools.init import InitSettings, InitTool
from .tools.merge import MergeSettings, MergeTool
from .tools.update import UpdateTool
from .tools.versioning import VersioningSettings, VersioningTool
from .utils.args import parse_args
from .utils.terminal import (
    Panel,
    display_error,
    display_info,
    display_success,
    display_warning,
)

__VERSION__ = "0.6.0"
__REPO__ = "caiquearaujo/gitmit"
config = init()


def close_all():
    if config.database:
        config.database.close()


def signal_handler(signum, frame):
    close_all()
    print("")
    sys.exit(0)


def startup(args):
    if args.command == "config":
        # Always show current configuration
        ConfigTool(services=config).run()
        return

    service = GitService(args.path)

    env = [
        f"Configuration file: [bold yellow]{config.path}[/bold yellow]",
        f"Working directory: [bold yellow]{service.getPath()}[/bold yellow]",
    ]

    if service.exists():
        env.append(f"Branch: [bold yellow]{service.currentBranch()}[/bold yellow]")

    display_info(Panel("\n".join(env), title="Environment"))

    switcher = {
        "commit": lambda: CommitTool(
            service,
            services=config,
            settings=CommitSettings(
                push=args.push,
                force=args.force,
                mode=args.mode,
                brief=args.brief,
                no_feat=args.no_feat,
                debug=args.debug,
                dry_run=args.dry_run,
            ),
        ).run(),
        "analyze": lambda: AnalyzeTool(
            service,
            services=config,
        ).run(),
        "init": lambda: InitTool(
            service,
            services=config,
            settings=InitSettings(dev=args.dev, origin=args.origin),
        ).run(),
        "merge": lambda: MergeTool(
            service,
            services=config,
            settings=MergeSettings(
                origin=args.origin,
                destination=args.destination,
                push=args.push,
            ),
        ).run(),
        "update": lambda: UpdateTool(__VERSION__, __REPO__).run(args.force),
        "versioning": lambda: VersioningTool(
            service,
            services=config,
            settings=VersioningSettings(
                version=args.version,
                origin=args.origin,
                force=args.force,
                push=args.push,
            ),
        ).run(),
    }

    func = switcher.get(args.command, None)

    if not func:
        display_error(
            "The command {command} was not found.".format(command=args.command),
        )

        return

    if isinstance(func, dict):
        func = func.get(args.action, False)

        if not func:
            display_error(
                "The action {action} was not found for {command}.".format(
                    action=args.action, command=args.command
                ),
            )

            return

    if not callable(func):
        display_error(
            "Unexpected error for {command}.".format(command=args.command),
        )

        return

    func()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    args = parse_args(__VERSION__)

    try:
        startup(args)
    except KeyboardInterrupt:
        display_warning("Interruping application...")
    except Exception as e:
        display_error(f"An unexpected error occurred. See: {e}.")
    finally:
        close_all()
        display_success("Bye, bye 🖖")
