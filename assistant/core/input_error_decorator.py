from collections.abc import Callable
from functools import wraps
from typing import Any

from assistant.core.command import CommandResult
from assistant.core.exceptions import (
    BirthdayError,
    ExtendedValueError,
    MissingContactError,
)
from assistant.ui.views import format_error


def failed(message: str) -> CommandResult:
    return CommandResult(format_error(message), changed=False)


def input_error(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def inner(*args: Any, **kwargs: Any) -> Any:
        try:
            result = func(*args, **kwargs)
        except ValueError:
            return failed("Not all data is provided.")
        except IndexError:
            return failed("Enter user name.")
        except KeyError:
            return failed("Contact not found.")
        except NotImplementedError:
            return failed("Under construction.")
        except (ExtendedValueError, MissingContactError, BirthdayError) as e:
            return failed(e.message)

        if isinstance(result, CommandResult):
            return result
        return CommandResult(result, changed=True)

    return inner
