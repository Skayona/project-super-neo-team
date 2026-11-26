from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CommandResult:
    output: Any
    changed: bool = False
