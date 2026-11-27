"""Define handlers for general commands."""

from functools import partial

from rich.panel import Panel
from rich.table import Table

from assistant.context.context import AssistantContext
from assistant.core.command import Command
from assistant.general.command_keys import GeneralCommandKeys
from assistant.general.keywords import get_keywords
from assistant.ui.views import format_command_card, format_help, format_info


def hello_handler(_: list[str]) -> Panel:
    """Display a greeting."""
    return format_info("Як я можу допомогти?")


def help_handler(
    commands: dict[str, Command],
    args: list[str],
) -> Panel | Table:
    """Display command help."""
    if args:
        return format_command_card(
            commands,
            args[0],
            GeneralCommandKeys.HELP.value,
        )
    return format_help(commands)


def exit_handler(
    ctx: AssistantContext,
    _args: list[str] | None = None,
) -> Panel:
    """Save assistant data and display a farewell."""
    ctx.save_all()
    return format_info("Всі записи збережно. До зустрічі!")


def build_commands(
    ctx: AssistantContext,
    commands: dict[str, Command],
) -> dict[str, Command]:
    """Build the general command definitions."""
    def get_exit_command(command: GeneralCommandKeys) -> Command:
        return Command(
            handler=partial(exit_handler, ctx),
            usage=(
                f"{GeneralCommandKeys.EXIT.value} |"
                f" {GeneralCommandKeys.CLOSE.value}"
            ),
            description="Зберігає дані та завершує роботу асистента",
            category="General",
            example=command.value,
            keywords=get_keywords(command),
        )

    return {
        GeneralCommandKeys.HELLO: Command(
            handler=hello_handler,
            usage=GeneralCommandKeys.HELLO.value,
            description="Привітання з асистентом",
            category="General",
            example=GeneralCommandKeys.HELLO.value,
            keywords=get_keywords(GeneralCommandKeys.HELLO),
        ),
        GeneralCommandKeys.HELP: Command(
            handler=partial(help_handler, commands),
            usage=GeneralCommandKeys.HELP.value,
            description="Показує список усіх доступних команд",
            category="General",
            example=(
                f"{GeneralCommandKeys.HELP.value} | "
                f"{GeneralCommandKeys.HELP.value} <command>"
            ),
            keywords=get_keywords(GeneralCommandKeys.HELP),
        ),
        GeneralCommandKeys.CLOSE: get_exit_command(GeneralCommandKeys.CLOSE),
        GeneralCommandKeys.EXIT: get_exit_command(GeneralCommandKeys.EXIT),
    }
