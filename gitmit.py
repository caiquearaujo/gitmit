import signal
import sys
from src.services.config import init
from src.services.git import GitService
from src.tools.commit import CommitTool, CommitSettings
from src.tools.init import InitTool, InitSettings
from src.utils.args import parse_args
from src.utils.terminal import display_success, display_error, display_info, Panel

config = init()


def close_all():
    if config.database:
        config.database.close()


def signal_handler(signum, frame):
    close_all()
    print("")
    sys.exit(0)


def main(args):
    if args.command == "config":
        display_info(
            "Config file created successfully. See at: [bold yellow]~/.config/gitmit/config.ini[/bold yellow]"
        )
        return

    service = GitService(args.path)

    env = [
        f"Working directory: [bold yellow]{service.getPath()}[/bold yellow]",
    ]

    if service.exists():
        env.append(f"Branch: [bold yellow]{service.currentBranch()}[/bold yellow]")

    display_info(Panel("\n".join(env), title="Environment"))

    switcher = {
        "commit": lambda: CommitTool(
            service,
            services=config,
            settings=CommitSettings(push=args.push, force=args.force),
        ).run(),
        "init": lambda: InitTool(
            service,
            services=config,
            settings=InitSettings(dev=args.dev, origin=args.origin),
        ).run(),
    }

    func = switcher.get(args.command, False)

    if func == False:
        display_error(
            "The command {command} was not found.".format(command=args.command),
        )

        return

    if type(func) == dict:
        func = func.get(args.action, False)

        if func == False:
            display_error(
                "The action {action} was not found for {command}.".format(
                    action=args.action, command=args.command
                ),
            )

    func()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        main(parse_args())
    except Exception as e:
        display_error(f"An unexpected error occurred. See: {e}.")
    finally:
        close_all()
        display_success("Bye, bye 🖖")
