"""Represent command execution results."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CommandResult:
    """Return command output and mutation state."""

    output: Any
    changed: bool = False
