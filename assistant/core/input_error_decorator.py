from collections.abc import Callable
from functools import wraps
from typing import Any

from assistant.core.exceptions import (
    BirthdayError,
    ExtendedValueError,
    MissingContactError,
)
from assistant.ui.views import format_error


def input_error(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def inner(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ValueError:
            return format_error("Not all data is provided.")
        except IndexError:
            return format_error("Enter user name.")
        except KeyError:
            return format_error("Contact not found.")
        except NotImplementedError:
            return format_error("Under construction.")
        except (ExtendedValueError, MissingContactError, BirthdayError) as e:
            return format_error(e.message)

    return inner
