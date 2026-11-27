import shlex
from enum import Enum

from prompt_toolkit import PromptSession
from rich.console import Console

from assistant.contacts import build_commands as build_contacts_commands
from assistant.contacts.command_keys import ContactCommandKeys
from assistant.context import AssistantContext
from assistant.core import (
    AssistantError,
    Command,
    CommandResult,
    UsageError,
    keyword_match,
    similar_cmd,
)
from assistant.general import (
    build_commands as build_general_commands,
)
from assistant.general import (
    exit_handler,
)
from assistant.notes.command_keys import NotesCommandKeys
from assistant.notes.handlers_registry import build_notes_commands
from assistant.ui import (
    format_error,
    format_welcome,
    init_assistant_completer,
)

console = Console()


def parse_input(user_input: str) -> tuple[str, list[str]]:
    if not user_input or not user_input.strip():
        return "", []

    user_input = user_input.strip()
    splitter = shlex.shlex(user_input, posix=True)
    splitter.quotes = '"'  # Зберігаємо апострофи в назвах
    splitter.whitespace_split = True
    splitter.commenters = ""

    try:
        splitted_input = list(splitter)
    except ValueError:
        raise UsageError("Незакрита лапка у команді.") from None

    if not splitted_input:
        return "", []

    cmd, *args = splitted_input
    cmd = cmd.lower()

    return cmd, args


def run_loop(
    ctx: AssistantContext,
    commands: dict[str, Command],
    session: PromptSession,
) -> None:
    while True:
        try:
            user_input = session.prompt("Введіть команду: ")
            command_key, args = parse_input(user_input)
        except KeyboardInterrupt:
            continue
        except EOFError:
            console.print(exit_handler(ctx))
            break
        except AssistantError as err:
            console.print(format_error(err.message))
            continue

        if not command_key:
            continue

        command = commands.get(command_key)

        if command is None:
            message = f"Не вдалося розпізнати команду: '{user_input}'."
            similar = similar_cmd(command_key, commands.keys())
            typo_matches = bool(similar)

            if not similar:
                similar = keyword_match(user_input, commands)

            if similar:
                usages = "\n".join(
                    [
                        commands[item].usage
                        for item in similar
                        if item in commands
                    ]
                )
                message += f"\nМожливо, ви мали на увазі:\n{usages}\n"

            message += "\nВведіть 'help', щоб побачити всі команди."
            console.print(format_error(message))

            # Optional — Execute suggested command
            if not typo_matches:
                continue

            suggested_key = similar[0]
            suggested_command = (
                str(suggested_key.value)
                if isinstance(suggested_key, Enum)
                else suggested_key
            )

            try:
                confirmation = (
                    session.prompt(
                        f"Виконати {suggested_command} "
                        "з тими ж аргументами? (y/n): "
                    )
                    .strip()
                    .lower()
                )
            except (KeyboardInterrupt, EOFError):
                continue

            if confirmation != "y":
                continue

            command = commands[suggested_command]

        try:
            result = command.handler(args)

            if isinstance(result, CommandResult):
                if command.mutates and result.changed:
                    ctx.save_all()
                console.print(result.output)
            else:
                console.print(result)

        except UsageError as err:
            console.print(
                format_error(f"{err.message} Використання: {command.usage}")
            )
        except AssistantError as err:
            console.print(format_error(err.message))
        except Exception as err:
            console.print(format_error(f"Непередбачена помилка: {err}"))

        if command_key in ("close", "exit"):
            break


def main() -> None:
    assistant_ctx = AssistantContext.load()

    commands: dict[str, Command] = {}
    commands.update(build_contacts_commands(assistant_ctx.address_book))
    commands.update(build_notes_commands(assistant_ctx.notebook))
    commands.update(build_general_commands(assistant_ctx, commands))

    session = init_assistant_completer(commands)

    frequent_commands = (
        ("Додати контакт", commands[ContactCommandKeys.ADD_CONTACT]),
        ("Знайти контакт", commands[ContactCommandKeys.FIND_CONTACT]),
        ("Усі контакти", commands[ContactCommandKeys.SHOW_ALL_CONTACTS]),
        ("Додати нотатку", commands[NotesCommandKeys.ADD_NOTE]),
        ("Усі нотатки", commands[NotesCommandKeys.ALL_NOTES]),
        ("Знайти нотатку", commands[NotesCommandKeys.FIND_NOTE]),
    )

    console.print(
        format_welcome(
            len(assistant_ctx.address_book),
            len(assistant_ctx.notebook),
            frequent_commands,
        )
    )

    try:
        run_loop(assistant_ctx, commands, session)
    finally:
        assistant_ctx.save_all()


if __name__ == "__main__":
    main()
