"""Represent command execution results."""

from dataclasses import dataclass

from rich.console import RenderableType


@dataclass(frozen=True)
class CommandResult:
    """Return command output and mutation state."""

    output: RenderableType
    changed: bool = False
