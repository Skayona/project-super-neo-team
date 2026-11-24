from rich import box
from rich.panel import Panel
from rich.table import Table

from assistant.core.command import Command


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


def format_help(commands: dict[str, Command]) -> Table:
    table = Table(
        title="[bold magenta]Доступні команди[/]", box=box.SIMPLE_HEAVY
    )
    table.add_column("Команда", style="bold green")
    table.add_column("Використання", style="cyan")
    table.add_column("Опис")

    for name, cmd in sorted(commands.items()):
        table.add_row(name, cmd.usage, cmd.description)

    return table
