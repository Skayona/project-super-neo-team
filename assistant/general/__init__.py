"""Expose general command builders and handlers."""

from assistant.general.handlers_registry import (
    build_commands,
    exit_handler,
)

__all__ = [
    "build_commands",
    "exit_handler",
]
