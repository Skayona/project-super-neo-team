from collections.abc import Iterable
from functools import partial

from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from assistant.core.command import Command
from assistant.core.exceptions import UsageError
from assistant.notes.note import Note
from assistant.notes.notebook import Notebook
from assistant.ui.views import format_table


def _render_notes(title: str, notes: Iterable[Note]) -> Table | Panel:
    rows = [
        [
            note.title.value,
            note.content.value,
            ", ".join(sorted(tag.value for tag in note.tags)) or "—",
        ]
        for note in notes
    ]
    return format_table(title, ["Заголовок", "Текст", "Теги"], rows)


def sort_notes(notebook: Notebook, args: list[str]) -> Table | Panel | Group:
    if args and args != ["--group"]:
        raise UsageError("Доступний параметр: --group.")

    if args and notebook:
        return Group(
            *(
                _render_notes(tag, notes)
                for tag, notes in notebook.group_by_tags().items()
            )
        )

    return _render_notes("Нотатки за тегами", notebook.sort_by_tags())


def build_sort_notes_command(notebook: Notebook) -> Command:
    return Command(
        handler=partial(sort_notes, notebook),
        usage="sort-notes [--group]",
        description="Сортувати нотатки за тегами або показати групи",
        category="Notes",
        example="sort-notes --group",
    )
