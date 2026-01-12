"""Module for displaying messages in the terminal."""

from typing import Callable

from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


def display_success(message: str | RenderableType) -> None:
    """Display a success message.

    Args:
        message (str): The message to display.
    """
    if isinstance(message, str):
        console.print(message, style="bold green")
    else:
        console.print(message)


def display_error(message: str | RenderableType) -> None:
    """Display an error message.

    Args:
        message (str): The message to display.
    """
    if isinstance(message, str):
        console.print(message, style="bold red")
    else:
        console.print(message)


def display_warning(message: str | RenderableType) -> None:
    """Display a warning message.

    Args:
        message (str): The message to display.
    """
    if isinstance(message, str):
        console.print(message, style="bold yellow")
    else:
        console.print(message)


def display_info(message: str | RenderableType) -> None:
    """Display an info message.

    Args:
        message: The message to display (can be str, Panel, Table, etc).
    """
    if isinstance(message, str):
        console.print(message, style="bold blue")
    else:
        console.print(message)


def clear():
    """Clear the terminal."""
    console.clear()


def ask(
    question: str,
    default: str | None = None,
    required: bool = False,
    formatter: Callable[[str], str] | None = None,
    clean: bool = True,
) -> str:
    """Ask a question.

    Args:
        question (str): The question to ask.
        default (str, optional): The default answer. Defaults to None.
        required (bool, optional): Whether the question is required. Defaults to False.
        formatter (Callable, optional): A formatter for the answer. Defaults to None.
        clean (bool, optional): Whether to clean the input. Defaults to True.

    Returns:
        str: The answer to the question.
    """
    if clean:
        console.clear()

    display_question = question

    while True:
        if default is not None:
            display_question = f"{question} [bold yellow]({default})[/bold yellow]"

        answer: str = Prompt.ask(
            display_question, console=console, default=default or "", show_default=False
        )

        if answer == "" and default is not None:
            return default

        if required and answer == "":
            console.print(
                "This field is required. Please provide a value for it.",
                style="bold red",
            )
            continue

        return formatter(answer) if formatter else answer


def ask_confirmation(question: str, default: str = "y", clean: bool = True) -> bool:
    """Ask for confirmation.

    Args:
        question (str): The question to ask.
        default (str, optional): The default answer. Defaults to "yes".
        clean (bool, optional): Whether to clean the input. Defaults to True.

    Returns:
        bool: True if the user confirmed, False otherwise.
    """
    if clean:
        console.clear()

    values = {
        "y": True,
        "n": False,
    }

    default = default.lower()[0]

    if default not in values:
        raise ValueError(f"Invalid default answer: {default}")

    marker = "[y/n]"

    if default == "y":
        marker = "(Y/n)"

    if default == "n":
        marker = "(y/N)"

    while True:
        answer = Prompt.ask(
            f"{question} [bold yellow]{marker}[/bold yellow]",
            console=console,
            default=default,
            show_default=False,
        )

        if answer == "":
            return values[default]

        if answer[0] in values:
            return values[answer[0]]

        console.print(
            f"Invalid answer: {answer}. Please answer with {', '.join(values.keys())}.",
            style="bold red",
        )


def choose(
    question: str,
    choices: list[str],
    default: int | None = None,
    clean: bool = True,
) -> int:
    """Choose an option from a list of choices.

    Args:
        question (str): The question to ask.
        choices (list[str]): The list of choices.
        default (str, optional): The default choice. Defaults to None.
        clean (bool, optional): Whether to clean the input. Defaults to True.

    Returns:
        str: The chosen option.
    """
    if clean:
        console.clear()

    console.print(Panel(question, style="bold cyan"))

    zfill = len(str(len(choices)))

    for index, option in enumerate(choices, start=1):
        console.print(f"[bold yellow]{str(index).zfill(zfill)}.[/bold yellow] {option}")

    choose_message = "Enter the number of your choice"

    if default is not None:
        choose_message = (
            f"{choose_message} [bold yellow]({choices[default - 1]})[/bold yellow]"
        )

    while True:
        choice = Prompt.ask(
            choose_message,
            console=console,
            default=default,
            show_default=False,
        )

        try:
            if choice is None:
                raise ValueError("Should choose a valid option.")

            choice = int(choice)
        except Exception:
            console.print(
                f"Invalid choice: {str(choice)}. Please choose a valid option.",
                style="bold red",
            )

            continue

        if choice == 0:
            if default is not None and choices[default - 1]:
                return default - 1

            console.print(
                "This field is required. Please provide a value for it.",
                style="bold red",
            )

            continue

        if 0 <= choice - 1 < len(choices):
            return choice - 1

        console.print(
            f"Invalid choice: {str(choice)}. Please choose a valid option.",
            style="bold red",
        )
