from functools import partial

from rich.panel import Panel
from rich.table import Table

from assistant.core.command import Command, MutationCommand
from assistant.core.command_result import CommandResult
from assistant.core.exceptions import NoteNotFoundError, UsageError
from assistant.core.input_error_decorator import input_error
from assistant.notes.fields import NoteTag
from assistant.notes.note import Note
from assistant.notes.notebook import Notebook
from assistant.ui.views import format_info, format_success, format_table

MATCH_ALL_FLAG = "--all"


def get_note(notebook: Notebook, title: str) -> Note:
    note = notebook.find_note(title)
    if note is None:
        raise NoteNotFoundError(title)
    return note


def format_tags(note: Note) -> str:
    return ", ".join(sorted(tag.value for tag in note.tags)) or "—"


@input_error
def add_tag(notebook: Notebook, args: list[str]) -> CommandResult:
    title, *tags = args
    if not tags:
        raise UsageError("Вкажіть хоча б один тег.")

    note = get_note(notebook, title)
    old_tags = set(note.tags)
    note.add_tags(*tags)
    new_tags = note.tags - old_tags
    if not new_tags:
        return CommandResult(
            format_info(f"Нотатка «{note.title}» вже має ці теги."),
            changed=False,
        )

    added = ", ".join(sorted(tag.value for tag in new_tags))
    return CommandResult(
        format_success(f"До нотатки «{note.title}» додано теги: {added}."),
        changed=True,
    )


@input_error
def remove_tag(notebook: Notebook, args: list[str]) -> Panel:
    title, tag = args
    note = get_note(notebook, title)
    note.remove_tag(tag)
    return format_success(
        f"Тег '{NoteTag(tag).value}' видалено з нотатки «{note.title}»."
    )


@input_error
def find_tag(notebook: Notebook, args: list[str]) -> Table | Panel:
    match_all = MATCH_ALL_FLAG in args
    tags = [arg for arg in args if arg != MATCH_ALL_FLAG]
    if not tags:
        raise UsageError("Вкажіть хоча б один тег.")

    notes = notebook.find_by_tags(*tags, match_all=match_all)
    if not notes:
        return format_info("Нотаток з такими тегами не знайдено.")

    rows = [
        [note.title.value, note.content.value, format_tags(note)]
        for note in sorted(notes, key=lambda n: n.title.value.casefold())
    ]
    return format_table(
        "Нотатки за тегами", ["Заголовок", "Текст", "Теги"], rows
    )


@input_error
def all_tags(notebook: Notebook, args: list[str]) -> Table | Panel:
    rows = [
        [tag, str(count)] for tag, count in sorted(notebook.all_tags().items())
    ]
    return format_table("Усі теги", ["Тег", "Кількість нотаток"], rows)


def complete_note_title(notebook: Notebook, args: list[str]) -> list[str]:
    if len(args) == 0:
        return sorted(note.title.value for note in notebook.values())
    return []


def complete_note_tag(notebook: Notebook, args: list[str]) -> list[str]:
    if len(args) == 0:
        return complete_note_title(notebook, args)
    if len(args) == 1:
        note = notebook.find_note(args[0])
        return sorted(tag.value for tag in note.tags) if note else []
    return []


def complete_tags(notebook: Notebook, args: list[str]) -> list[str]:
    used = set(args)
    options = [*sorted(notebook.all_tags()), MATCH_ALL_FLAG]
    return [option for option in options if option not in used]


def build_tag_commands(notebook: Notebook) -> dict[str, Command]:
    return {
        "add-tag": MutationCommand(
            handler=partial(add_tag, notebook),
            arg_completer=partial(complete_note_title, notebook),
            usage="add-tag <назва> <тег1> [тег2 ...]",
            description="Додати нотатці один або кілька тегів",
            category="Notes",
            example="add-tag Покупки дім терміново",
        ),
        "remove-tag": MutationCommand(
            handler=partial(remove_tag, notebook),
            arg_completer=partial(complete_note_tag, notebook),
            usage="remove-tag <назва> <тег>",
            description="Видалити тег із нотатки",
            category="Notes",
            example="remove-tag Покупки терміново",
        ),
        "find-tag": Command(
            handler=partial(find_tag, notebook),
            arg_completer=partial(complete_tags, notebook),
            usage="find-tag <тег1> [тег2 ...] [--all]",
            description=(
                "Знайти нотатки з будь-яким із тегів (--all — з усіма)"
            ),
            category="Notes",
            example="find-tag дім робота --all",
        ),
        "all-tags": Command(
            handler=partial(all_tags, notebook),
            usage="all-tags",
            description="Показати всі теги та кількість нотаток з ними",
            category="Notes",
        ),
    }
