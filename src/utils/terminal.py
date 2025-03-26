"""Module for displaying messages in the terminal."""

from typing import Callable

from rich.console import Console
from rich.prompt import Prompt


console = Console()


def display_success(message: str) -> None:
    """Display a success message.

    Args:
        message (str): The message to display.
    """
    console.print(message, style="bold green")


def display_error(message: str) -> None:
    """Display an error message.

    Args:
        message (str): The message to display.
    """
    console.print(message, style="bold red")


def display_warning(message: str) -> None:
    """Display a warning message.

    Args:
        message (str): The message to display.
    """
    console.print(message, style="bold yellow")


def display_info(message: str) -> None:
    """Display an info message.

    Args:
        message (str): The message to display.
    """
    console.print(message, style="bold blue")


def clear():
    """Clear the terminal."""
    console.clear()


def ask(
    question: str,
    default: str = None,
    required: bool = False,
    formatter: Callable = None,
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

    while True:
        if default is not None:
            question = f"{question} [bold yellow]({default})[/bold yellow]"

        answer = Prompt.ask(
            question, console=console, default=default, show_default=False
        )

        if (answer == "" or answer is None) and default is not None:
            return default

        if required and (answer == "" or answer is None):
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

        if answer == "" or answer is None:
            return values[default]

        if answer[0] in values:
            return values[answer[0]]

        console.print(
            f"Invalid answer: {answer}. Please answer with {', '.join(values.keys())}.",
            style="bold red",
        )


def choose(
    question: str, choices: list[str], default: int = None, clean: bool = True
) -> str:
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

    console.print(question, style="bold cyan")
    console.print("")
    zfill = len(str(len(choices)))

    for index, option in enumerate(choices, start=1):
        console.print(f"[bold yellow]{str(index).zfill(zfill)}.[/bold yellow] {option}")

    while True:
        console.print("")
        choice = Prompt.ask(
            "Enter the number of your choice",
            console=console,
            default=default,
            show_default=False,
        )

        if choice == "" or choice is None:
            if default is not None:
                return choices[default - 1]

            console.print(
                "This field is required. Please provide a value for it.",
                style="bold red",
            )

            continue

        if choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(choices):
                return choices[num - 1]

        console.print(
            f"Invalid choice: {choice}. Please choose a valid option.",
            style="bold red",
        )
