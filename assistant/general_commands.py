import shlex
from typing import Any

from rich.panel import Panel

from assistant.contacts.address_book import AddressBook, ExtendedValueError
from assistant.core.command import Command
from assistant.storage.storage import save_address_book
from assistant.ui.views import format_info


def parse_input(user_input: str) -> tuple[str, list[str]]:
    if not user_input or not user_input.strip():
        return "", []

    user_input = user_input.strip()
    splitter = shlex.shlex(user_input, posix=True)
    splitter.quotes = '"'  # апострофи в назвах не мають бути викинуиті
    splitter.whitespace_split = True

    try:
        splitted_input = list(splitter)
    except ValueError:
        raise ExtendedValueError("Незакрита лапка у команді.")

    if not splitted_input:
        return "", []

    cmd, *args = splitted_input
    cmd = cmd.lower()

    return cmd, args


def hello_handler(*_: Any) -> Panel:
    return format_info("How can I help you?")


def help_handler(*_: Any) -> str:
    raise NotImplementedError


def exit_handler(book: AddressBook, *_: Any) -> Panel:
    save_address_book(book)
    return format_info("Good bye!")


exit_command = Command(
    handler=exit_handler,
    usage="exit | close",
    description="Зберігає дані та завершує роботу асистента",
    category="General",
)


def build_general_commands() -> dict[str, Command]:
    return {
        "hello": Command(
            handler=hello_handler,
            usage="hello",
            description="Привітання з асистентом",
            category="General",
        ),
        "help": Command(
            handler=help_handler,
            usage="help",
            description="Показує список усіх доступних команд",
            category="General",
        ),
        "close": exit_command,
        "exit": exit_command,
    }
