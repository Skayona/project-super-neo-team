"""Adds UX for the users."""

from assistant.ui.completer import init_assistant_completer
from assistant.ui.views import (
    format_card,
    format_error,
    format_help,
    format_info,
    format_success,
    format_table,
    format_warn,
)

__all__ = [
    "init_assistant_completer",
    "format_info",
    "format_success",
    "format_error",
    "format_card",
    "format_table",
    "format_help",
    "format_warn",
]
