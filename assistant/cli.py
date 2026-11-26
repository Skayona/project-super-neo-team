from prompt_toolkit import PromptSession
from rich.console import Console

from assistant.contacts.address_book import AddressBook
from assistant.contacts.handlers_registry import build_contacts_commands
from assistant.core.command import Command, CommandResult
from assistant.general_commands import (
    ExtendedValueError,
    build_general_commands,
    exit_handler,
    parse_input,
)
from assistant.storage.storage import (
    load_address_book,
    save_address_book,
)
from assistant.ui.completer import init_assistant_completer
from assistant.ui.views import format_error, format_info

console = Console()


def main():
    book = load_address_book()
    commands: dict[str, Command] = {}
    commands.update(build_contacts_commands(book))

    # TODO(notes): register the Notes commands below, e.g.
    # commands.update(build_notes_commands(book))
    # They must have category="Notes" to appear in `help`.
    commands.update(build_general_commands(lambda: commands))

    session = init_assistant_completer(commands)

    console.print(format_info("Welcome to the assistant bot!"))

    try:
        run_loop(book, commands, session)
    finally:
        save_address_book(book)


def run_loop(
    book: AddressBook,
    commands: dict[str, Command],
    session: PromptSession,
) -> None:
    while True:
        try:
            user_input = session.prompt("Enter a command: ")
            command_key, args = parse_input(user_input)
        except KeyboardInterrupt:
            continue
        except EOFError:
            console.print(exit_handler(book))
            break
        except ExtendedValueError as err:
            console.print(format_error(str(err)))
            continue

        if not command_key:
            continue

        command = commands.get(command_key)

        if command:
            result = command.handler(book, args)
            if isinstance(result, CommandResult):
                if command.mutates and result.changed:
                    save_address_book(book)
                console.print(result.output)
            else:
                console.print(result)
            if command_key in ("close", "exit"):
                break
        else:
            console.print(format_error("Invalid command."))


if __name__ == "__main__":
    main()
