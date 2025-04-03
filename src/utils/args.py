import argparse
import os
import pathlib


class CheckPathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # Convert the provided path to an absolute path
        path = pathlib.Path(values).resolve()

        # Check if the path exists
        if not path.exists():
            parser.error(f"The specified path '{path}' does not exist.")

        setattr(namespace, self.dest, path)


def __commit_parser(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser("commit", help="Commit all changes.")

    parser.add_argument(
        "--push",
        help="Automatically push the changes to the remote repository.",
        action="store_true",
    )

    parser.add_argument(
        "--force",
        help="Once you use this option, you will not be asked for confirmation before committing.",
        action="store_true",
    )

    return parser


def parse_args():
    parser = argparse.ArgumentParser(
        prog="GitMit",
        description="GitMit: A simple Git repository manager based on GitFlow requirements.",
        epilog="See below all commands ready to be used.",
    )

    parser.add_argument(
        "-p",
        "--path",
        help="Working directory for git.",
        type=pathlib.Path,
        default=os.getcwd(),
        action=CheckPathAction,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to be executed.")

    __commit_parser(subparsers)
    subparsers.add_parser("init", help="Initialize the project.")

    return parser.parse_args()
