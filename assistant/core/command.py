from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Literal

Category = Literal["Notes", "Contacts", "General"]
ArgCompleter = Callable[[list[str]], Sequence[str]]


@dataclass(frozen=True)
class Command:
    handler: Callable[..., Any]
    usage: str
    description: str
    category: Category
    arg_completer: ArgCompleter | None = None
