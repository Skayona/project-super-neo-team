"""Define command models and argument completers."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Literal

from rich.console import RenderableType

from assistant.core.command_result import CommandResult

Category = Literal["Notes", "Contacts", "General"]
ArgCompleter = Callable[[list[str]], Sequence[str]]


@dataclass(frozen=True)
class Command:
    """Describe a command and its handler."""

    handler: Callable[[list[str]], CommandResult | RenderableType]
    usage: str
    description: str
    category: Category
    arg_completer: ArgCompleter | None = None
    example: str = ""
    mutates: bool = False
    keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class MutationCommand(Command):
    """Describe a command that changes stored data."""

    mutates: bool = True
