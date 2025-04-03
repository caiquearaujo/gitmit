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

    subparsers.add_parser("commit", help="Commit all changes.")
    subparsers.add_parser("init", help="Initialize the project.")

    return parser.parse_args()
