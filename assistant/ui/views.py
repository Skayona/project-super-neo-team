from collections.abc import Sequence
from typing import get_args

from rich import box
from rich.console import Group
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from assistant.core.command import Category, Command
from assistant.core.suggest import similar_cmd


def format_welcome(
    contact_count: int,
    note_count: int,
    frequent_commands: Sequence[tuple[str, Command]],
) -> Panel:
    content = [
        Text.assemble(
            ("Контактів: ", "bold"),
            (str(contact_count), "cyan"),
            ("    Нотаток: ", "bold"),
            (str(note_count), "cyan"),
        ),
        Text(""),
        Text("Популярні команди", style="bold magenta"),
        Text(""),
    ]

    for index, (name, command) in enumerate(frequent_commands):
        content.extend(
            [
                Text(name, style="bold cyan"),
                Text(f"  {command.usage}", style="bold"),
                Text(f"  {command.description}", style="italic"),
            ]
        )
        if index < len(frequent_commands) - 1:
            content.append(Text(""))

    content.extend(
        [
            Text(""),
            Text("Введи help, щоб переглянути всі команди.", style="dim"),
        ]
    )

    return Panel(
        Group(*content),
        title=Text("Бот-помічник вітає тебе!", style="bold white"),
        title_align="left",
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 2),
    )


def format_info(text: str) -> Panel:
    return Panel(
        f"\n{escape(text)}\n",
        title_align="left",
        box=box.ROUNDED,
        border_style="white",
        title="[bold white] ● Інфо [/]",
    )


def format_success(text: str) -> Panel:
    return Panel(
        f"\n{escape(text)}\n",
        title_align="left",
        box=box.ROUNDED,
        border_style="green",
        title="[bold green] ✅ Успіх[/]",
    )


def format_error(text: str) -> Panel:
    return Panel(
        f"\n{escape(text)}\n",
        title_align="left",
        box=box.ROUNDED,
        border_style="red",
        title="[bold red] ❌ Упс, щось пішло не так[/]",
    )


def format_warn(text: str) -> Panel:
    return Panel(
        f"\n{escape(text)}\n",
        title_align="left",
        box=box.ROUNDED,
        border_style="yellow",
        title="[bold yellow] ⚠ Увага [/]",
    )


def format_card(title: str, data: dict[str, str]) -> Panel:
    lines = [
        f"[bold magenta]{escape(key)}:[/] {escape(value) or '—'}"
        for key, value in data.items()
    ]
    joined_lines = "\n".join(lines)
    return Panel(
        f"\n{joined_lines}\n",
        title_align="left",
        box=box.ROUNDED,
        border_style="cyan",
        title=f"[bold cyan]{escape(title)}[/]",
    )


def format_table(
    title: str, headers: list[str], rows: list[list[str]]
) -> Table | Panel:
    if not rows:
        return format_info("Список порожній.")

    table = Table(
        title=f"[bold magenta]{escape(title)}[/]",
        box=box.ROUNDED,
        show_lines=True,
    )
    for header in headers:
        table.add_column(escape(header), style="cyan")

    for row in rows:
        table.add_row(*map(lambda col: escape(col), row))

    return table


def format_command_card(commands: dict[str, Command], name: str) -> Panel:
    key = name.lower()
    cmd = commands.get(key)
    if cmd is None:
        message = f"Команду '{name}' не знайдено."
        similar = similar_cmd(key, commands.keys())

        if similar:
            message += f"\nМожливо, ви мали на увазі: {', '.join(similar)}"

        message += "\nВведіть 'help', щоб побачити всі команди."

        return format_error(message)

    return format_card(
        key,
        {
            "Використання": cmd.usage,
            "Опис": cmd.description,
            "Категорія": cmd.category,
            "Приклад": cmd.example or cmd.usage,
        },
    )


def format_help(commands: dict[str, Command]) -> Table:
    table = Table(
        title="[bold magenta]Доступні команди[/]",
        box=box.ROUNDED,
        show_lines=False,
    )
    table.add_column("Використання", style="bold green")
    table.add_column("Опис")

    unique = {id(cmd): cmd for _, cmd in sorted(commands.items())}.values()

    categories = sorted(get_args(Category), key=lambda c: c != "General")
    category_labels = {
        "General": "Загальні",
        "Contacts": "Контакти",
        "Notes": "Нотатки",
    }

    first = True
    for category in categories:
        group = [cmd for cmd in unique if cmd.category == category]
        if not group:
            continue
        if not first:
            table.add_section()
        first = False
        table.add_row(f"[bold magenta]{category_labels[category]}[/]", "")
        for cmd in group:
            table.add_row(f"  {escape(cmd.usage)}", escape(cmd.description))

    return table
