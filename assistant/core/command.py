from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from assistant.core.command_result import CommandResult

Category = Literal["Notes", "Contacts", "General"]
ArgCompleter = Callable[[list[str]], Sequence[str]]


@dataclass(frozen=True)
class Command:
    handler: Callable[[list[str]], CommandResult | Any]
    usage: str
    description: str
    category: Category
    arg_completer: ArgCompleter | None = None
    example: str = ""
    mutates: bool = False
    keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class MutationCommand(Command):
    mutates: bool = True
