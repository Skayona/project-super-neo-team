from rich.console import Console

from assistant.contacts.handlers_registry import build_contacts_commands
from assistant.core.command import Command
from assistant.general_commands import (
    build_general_commands,
    exit_handler,
    parse_input,
)
from assistant.storage.storage import (
    load_address_book,
)
from assistant.ui.completer import init_assistant_completer
from assistant.ui.views import format_error, format_info

console = Console()


def main():
    book = load_address_book()
    commands: dict[str, Command] = {
        **build_contacts_commands(book),
        **build_general_commands(),
    }
    session = init_assistant_completer(commands)

    console.print(format_info("Welcome to the assistant bot!"))

    while True:
        try:
            user_input = session.prompt("Enter a command: ")
        except KeyboardInterrupt:
            continue
        except EOFError:
            console.print(exit_handler(book))
            break

        command_key, *args = parse_input(user_input)
        command = commands.get(command_key)

        if command:
            console.print(command.handler(book, args))
            if command_key in ("close", "exit"):
                break
        else:
            console.print(format_error("Invalid command."))


if __name__ == "__main__":
    main()
