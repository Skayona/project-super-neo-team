from prompt_toolkit import PromptSession
from rich.console import Console

from assistant.contacts.handlers_registry import build_contacts_commands
from assistant.context.context import AssistantContext
from assistant.core.command import Command, CommandResult
from assistant.general_commands import (
    ExtendedValueError,
    build_general_commands,
    exit_handler,
    parse_input,
)
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
            user_input = session.prompt("Enter a command: ")
            command_key, args = parse_input(user_input)
        except KeyboardInterrupt:
            continue
        except EOFError:
            console.print(exit_handler(ctx))
            break
        except ExtendedValueError as err:
            console.print(format_error(str(err)))
            continue

        if not command_key:
            continue

        command = commands.get(command_key)

        if command:
            try:
                result = command.handler(args)
            except Exception as err:
                console.print(format_error(f"Непередбачена помилка: {err}"))
                continue

            if isinstance(result, CommandResult):
                if command.mutates and result.changed:
                    ctx.save_all()
                console.print(result.output)
            else:
                console.print(result)
            if command_key in ("close", "exit"):
                break
        else:
            console.print(format_error("Invalid command."))


def main() -> None:
    assistant_ctx = AssistantContext.load()

    commands: dict[str, Command] = {}
    commands.update(build_contacts_commands(assistant_ctx.address_book))
    # TODO(notes): register the Notes commands below, e.g.
    # commands.update(build_notes_commands(assistant_ctx.notebook))
    # They must have category="Notes" to appear in `help`.
    commands.update(build_general_commands(assistant_ctx, commands))

    session = init_assistant_completer(commands)

    console.print(format_info("Welcome to the assistant bot!"))

    try:
        run_loop(assistant_ctx, commands, session)
    finally:
        assistant_ctx.save_all()


if __name__ == "__main__":
    main()
