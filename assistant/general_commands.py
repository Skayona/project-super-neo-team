from typing import Any, Callable

from rich.panel import Panel

from functools import partial

from assistant.contacts.address_book import AddressBook
from assistant.core.command import Command
from assistant.core.input_error_decorator import input_error
from assistant.storage.storage import save_address_book
from assistant.ui.views import format_info, format_help, format_command_card

@input_error
def parse_input(user_input: str) -> tuple[str, ...]:
    if not user_input:
        return ("",)

    user_input = user_input.strip()
    cmd, *args = user_input.split()
    cmd = cmd.lower()

    return cmd, *args


def hello_handler(*_: Any) -> Panel:
    return format_info("How can I help you?")


def help_handler(
    get_commands: Callable[[], dict[str, Command]],
    book: AddressBook,
    args: list[str],
) -> Any:
    commands = get_commands()
    if args:
        return format_command_card(commands, args[0])
    return format_help(commands)


def exit_handler(book: AddressBook, *_: Any) -> Panel:
    save_address_book(book)
    return format_info("Good bye!")


exit_command = Command(
    handler=exit_handler,
    usage="exit | close",
    description="Зберігає дані та завершує роботу асистента",
    category="General",
    example = "exit",
)


def build_general_commands(
    get_commands: Callable[[], dict[str, Command]],
) -> dict[str, Command]:
    return {
        "hello": Command(
            handler=hello_handler,
            usage="hello",
            description="Привітання з асистентом",
            category="General",
            example="hello",
        ),
        "help": Command(
            handler=partial(help_handler, get_commands),
            usage="help",
            description="Показує список усіх доступних команд",
            category="General",
            example="help | help <command>",
        ),
        "close": exit_command,
        "exit": exit_command,
    }
