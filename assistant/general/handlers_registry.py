from functools import partial
from typing import Any

from rich.panel import Panel

from assistant.context.context import AssistantContext
from assistant.core.command import Command
from assistant.general.command_keys import GeneralCommandKeys
from assistant.general.keywords import get_keywords
from assistant.ui.views import format_command_card, format_help, format_info


def hello_handler(*_: Any) -> Panel:
    return format_info("Як я можу допомогти?")


def help_handler(
    commands: dict[str, Command],
    args: list[str],
) -> Any:
    if args:
        return format_command_card(commands, args[0])
    return format_help(commands)


def exit_handler(ctx: AssistantContext, *_: Any) -> Panel:
    ctx.save_all()
    return format_info("Всі записи збережно. До зустрічі!")


def build_commands(
    ctx: AssistantContext,
    commands: dict[str, Command],
) -> dict[str, Command]:
    def get_exit_command(command: GeneralCommandKeys) -> Command:
        return Command(
            handler=partial(exit_handler, ctx),
            usage=(
                f"{GeneralCommandKeys.EXIT.value} |"
                f" {GeneralCommandKeys.CLOSE.value}"
            ),
            description="Зберігає дані та завершує роботу асистента",
            category="General",
            example="exit",
            keywords=get_keywords(command),
        )

    return {
        GeneralCommandKeys.HELLO: Command(
            handler=hello_handler,
            usage=GeneralCommandKeys.HELLO.value,
            description="Привітання з асистентом",
            category="General",
            example="hello",
            keywords=get_keywords(GeneralCommandKeys.HELLO),
        ),
        GeneralCommandKeys.HELP: Command(
            handler=partial(help_handler, commands),
            usage=GeneralCommandKeys.HELP.value,
            description="Показує список усіх доступних команд",
            category="General",
            example="help | help <command>",
            keywords=get_keywords(GeneralCommandKeys.HELP),
        ),
        GeneralCommandKeys.CLOSE: get_exit_command(GeneralCommandKeys.CLOSE),
        GeneralCommandKeys.EXIT: get_exit_command(GeneralCommandKeys.EXIT),
    }
