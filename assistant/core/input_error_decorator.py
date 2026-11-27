"""Convert command errors into user-facing results."""

from collections.abc import Callable
from functools import wraps
from typing import Any

from assistant.core.command_result import CommandResult
from assistant.core.exceptions import AssistantError, UsageError
from assistant.ui.views import format_error


def failed(message: str) -> CommandResult:
    """Build a failed command result."""
    return CommandResult(format_error(message), changed=False)


def input_error(func: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap a handler with input error conversion."""
    @wraps(func)
    def inner(*args: Any, **kwargs: Any) -> Any:
        try:
            result = func(*args, **kwargs)
        except UsageError:
            raise
        except AssistantError as e:
            return failed(e.message)
        except IndexError:
            raise UsageError("Недостатньо аргументів.") from None
        except ValueError as e:
            if "not enough values to unpack" in str(e):
                raise UsageError("Недостатньо аргументів.") from None
            raise

        if isinstance(result, CommandResult):
            return result

        return CommandResult(result, changed=True)

    return inner
