from prompt_toolkit import PromptSession
from rich.console import Console
from rich.markup import escape

from assistant.contacts.handlers_registry import build_contacts_commands
from assistant.context.context import AssistantContext
from assistant.core.command import Command
from assistant.core.command_result import CommandResult
from assistant.core.exceptions import AssistantError, UsageError
from assistant.core.suggest import keyword_match, similar_cmd
from assistant.general_commands import (
    build_general_commands,
    exit_handler,
    parse_input,
)
from assistant.notes.handlers_registry import build_notes_commands
from assistant.ui.completer import init_assistant_completer
from assistant.ui.views import format_error, format_info

console = Console()


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
                similar = keyword_match(user_input, commands.keys())

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

            try:
                confirmation = (
                    session.prompt(
                        f"Виконати {suggested_key} "
                        "з тими ж аргументами? (y/n): "
                    )
                    .strip()
                    .lower()
                )
            except (KeyboardInterrupt, EOFError):
                continue

            if confirmation != "y":
                continue

            command_key = suggested_key
            command = commands[command_key]

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
                format_error(
                    f"{err.message} Використання: {escape(command.usage)}"
                )
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

    console.print(format_info("Welcome to the assistant bot!"))

    try:
        run_loop(assistant_ctx, commands, session)
    finally:
        assistant_ctx.save_all()


if __name__ == "__main__":
    main()
