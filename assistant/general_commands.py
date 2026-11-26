import shlex
from functools import partial
from typing import Any

from rich.panel import Panel

from assistant.context.context import AssistantContext
from assistant.core.command import Command
from assistant.core.exceptions import UsageError
from assistant.ui.views import format_command_card, format_help, format_info


def parse_input(user_input: str) -> tuple[str, list[str]]:
    if not user_input or not user_input.strip():
        return "", []

    user_input = user_input.strip()
    splitter = shlex.shlex(user_input, posix=True)
    splitter.quotes = '"'  # Зберігаємо апострофи в назвах
    splitter.whitespace_split = True

    try:
        splitted_input = list(splitter)
    except ValueError:
        raise UsageError("Незакрита лапка у команді.") from None

    if not splitted_input:
        return "", []

    cmd, *args = splitted_input
    cmd = cmd.lower()

    return cmd, args


def hello_handler(*_: Any) -> Panel:
    return format_info("How can I help you?")


def help_handler(
    commands: dict[str, Command],
    args: list[str],
) -> Any:
    if args:
        return format_command_card(commands, args[0])
    return format_help(commands)


def exit_handler(ctx: AssistantContext, *_: Any) -> Panel:
    ctx.save_all()
    return format_info("Good bye!")


def build_general_commands(
    ctx: AssistantContext,
    commands: dict[str, Command],
) -> dict[str, Command]:
    exit_command = Command(
        handler=partial(exit_handler, ctx),
        usage="exit | close",
        description="Зберігає дані та завершує роботу асистента",
        category="General",
        example="exit",
    )

    return {
        "hello": Command(
            handler=hello_handler,
            usage="hello",
            description="Привітання з асистентом",
            category="General",
            example="hello",
        ),
        "help": Command(
            handler=partial(help_handler, commands),
            usage="help",
            description="Показує список усіх доступних команд",
            category="General",
            example="help | help <command>",
        ),
        "close": exit_command,
        "exit": exit_command,
    }