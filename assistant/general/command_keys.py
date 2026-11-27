"""Define identifiers for general commands."""

from enum import Enum


class GeneralCommandKeys(str, Enum):
    """Identify available general commands."""

    HELLO = "hello"
    HELP = "help"
    CLOSE = "close"
    EXIT = "exit"
