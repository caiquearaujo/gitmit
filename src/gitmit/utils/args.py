import argparse
import os
import pathlib
import re

from urllib.parse import urlparse


class CheckPathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # Convert the provided path to an absolute path
        path = pathlib.Path(values).resolve()

        # Check if the path exists
        if not path.exists():
            parser.error(f"The specified path '{path}' does not exist.")

        setattr(namespace, self.dest, path)


class CheckOriginAction(argparse.Action):
    def __is_git_ssh(self, url: str) -> bool:
        return re.match(r"^[\w\.-]+@[\w\.-]+:[\w\./-]+\.git$", url) is not None

    def __is_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def __call__(self, parser, namespace, values, option_string=None):
        if self.__is_git_ssh(values) or self.__is_url(values):
            setattr(namespace, self.dest, values)
            return

        parser.error("The origin URL is not valid.")


class CheckRepoAction(argparse.Action):
    def __is_valid_repo(self, repo: str) -> bool:
        return re.match(r"^[\w\.-]+/[\w\.-]+$", repo) is not None

    def __call__(self, parser, namespace, values, option_string=None):
        if self.__is_valid_repo(values):
            setattr(namespace, self.dest, values)
            return

        parser.error("The repository is not valid.")


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


def __init_parser(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser("init", help="Initialize the project.")

    parser.add_argument(
        "--dev",
        help="Create a dev branch.",
        action="store_true",
    )

    parser.add_argument(
        "--origin",
        help="Set the origin URL.",
        type=str,
        action=CheckOriginAction,
    )

    return parser


def __update_parser(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser("update", help="Update the tool.")

    parser.add_argument(
        "--force",
        help="Force the update of the tool.",
        action="store_true",
    )

    return parser


def parse_args(version: str):
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

    parser.add_argument(
        "-v",
        "--version",
        help="Show the current version of the tool.",
        action="version",
        version=f"GitMit v{version}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to be executed.")

    subparsers.add_parser("config", help="Creates the configuration file.")
    __commit_parser(subparsers)
    __init_parser(subparsers)
    __update_parser(subparsers)
    return parser.parse_args()
