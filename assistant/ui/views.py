from rich import box
from rich.panel import Panel
from rich.table import Table

from typing import get_args

from difflib import get_close_matches

from assistant.core.command import Command, Category


def format_info(text: str) -> Panel:
    return Panel(
        f"\n{text}\n",
        title_align="left",
        box=box.ROUNDED,
        border_style="white",
        title="[bold white] ● Інфо [/]",
    )


def format_success(text: str) -> Panel:
    return Panel(
        f"\n{text}\n",
        title_align="left",
        box=box.ROUNDED,
        border_style="green",
        title="[bold green] ✅ Успіх[/]",
    )


def format_error(text: str) -> Panel:
    return Panel(
        f"\n{text}\n",
        title_align="left",
        box=box.ROUNDED,
        border_style="red",
        title="[bold red] ❌ Упс, щось пішло не так[/]",
    )


def format_card(title: str, data: dict[str, str]) -> Panel:
    lines = [
        f"[bold magenta]{key}:[/] {value or '—'}"
        for key, value in data.items()
    ]
    joined_lines = "\n".join(lines)
    return Panel(
        f"\n{joined_lines}\n",
        title_align="left",
        box=box.ROUNDED,
        border_style="cyan",
        title=f"[bold cyan]{title}[/]",
    )


def format_table(
    title: str, headers: list[str], rows: list[list[str]]
) -> Table | Panel:
    if not rows:
        return format_info("Список порожній.")

    table = Table(
        title=f"[bold magenta]{title}[/]", box=box.ROUNDED, show_lines=True
    )
    for header in headers:
        table.add_column(header, style="cyan")

    for row in rows:
        table.add_row(*row)

    return table


def format_command_card(commands: dict[str, Command], name: str) -> Panel:
    key = name.lower()
    cmd = commands.get(key)
    if cmd is None:
        message = f"Команду '{name}' не знайдено."
        similar = get_close_matches(key, commands.keys(), n=3, cutoff=0.5)
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

    first = True
    for category in categories:
        group = [cmd for cmd in unique if cmd.category == category]
        if not group:
            continue
        if not first:
            table.add_section()
        first = False
        table.add_row(f"[bold magenta]{category}[/]", "")
        for cmd in group:
            table.add_row(f"  {cmd.usage}", cmd.description)

    return table
