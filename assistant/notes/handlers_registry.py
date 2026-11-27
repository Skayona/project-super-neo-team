from collections.abc import Iterable
from functools import partial

from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from assistant.core.command import Command, MutationCommand
from assistant.core.command_result import CommandResult
from assistant.core.exceptions import (
    NoteNotFoundError,
    UsageError,
)
from assistant.core.input_error_decorator import input_error
from assistant.notes.fields import NoteTag
from assistant.notes.note import Note
from assistant.notes.notebook import Notebook
from assistant.ui.views import (
    format_card,
    format_error,
    format_info,
    format_success,
    format_table,
)

MATCH_ALL_FLAG = "--all"


def get_note(notebook: Notebook, title: str) -> Note:
    note = notebook.find_note(title)
    if note is None:
        raise NoteNotFoundError(title)
    return note


def _parse_note_args(
    args: list[str],
) -> tuple[str, str, list[str]]:
    if not args:
        raise UsageError("Вкажіть заголовок нотатки.")

    title = args[0]
    content_parts: list[str] = []
    tags: list[str] = []

    for arg in args[1:]:
        if arg.startswith("#"):
            tags.append(arg)
        else:
            content_parts.append(arg)

    return title, " ".join(content_parts), tags


def _render_notes_table(title: str, notes: list[Note]):
    rows = [
        [
            note.title.value,
            note.content.value,
            ", ".join(
                f"#{tag.value}"
                for tag in sorted(note.tags, key=lambda tag: tag.value)
            )
            or "—",
            note.created_at_display,
            note.updated_at_display,
        ]
        for note in notes
    ]

    return format_table(
        title,
        ["Заголовок", "Текст", "Теги", "Створено", "Оновлено"],
        rows,
    )


def add_note(notebook: Notebook, args: list[str]):

    title, content, tags = _parse_note_args(args)

    note = Note(
        title=title,
        content=content,
        tags=tags,
    )

    notebook.add_note(note)

    return format_success(f"Нотатку «{note.title.value}» успішно додано.")


def show_note(notebook: Notebook, args: list[str]):
    if not args:
        raise UsageError("Вкажіть заголовок нотатки")

    title = " ".join(args)
    note = notebook.find_note(title)

    if note is None:
        raise NoteNotFoundError(title)

    tags = (
        ", ".join(f"#{tag}" for tag in sorted(t.value for t in note.tags))
        or "—"
    )

    return format_card(
        note.title.value,
        {
            "Текст": note.content.value,
            "Теги": tags,
            "Створено": note.created_at_display,
            "Оновлено": note.updated_at_display,
        },
    )


def all_notes(notebook: Notebook, args: list[str]):
    if args:
        raise UsageError("Команда не приймає аргументів.")

    if not notebook:
        return format_error("Нотаток ще немає. Додайте: add-note ...")
    notes = sorted(
        reversed(list(notebook.values())),
        key=lambda note: note.created_at,
        reverse=True,
    )

    return _render_notes_table("Усі нотатки", notes)


def find_note(notebook: Notebook, args: list[str]):
    query = " ".join(args).strip()

    if not query:
        raise UsageError("Вкажіть пошуковий запит.")

    notes = notebook.search(query)

    if query.startswith("#"):
        tagged_notes = notebook.search(query[1:])

        for note in tagged_notes:
            if note not in notes:
                notes.append(note)

    if not notes:
        return format_error(f"За запитом «{query}» нічого не знайдено.")

    notes.sort(
        key=lambda note: note.created_at,
        reverse=True,
    )

    return _render_notes_table("Результати пошуку", notes)


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


def build_notes_commands(notebook: Notebook) -> dict[str, Command]:
    return {
        "add-note": MutationCommand(
            handler=partial(add_note, notebook),
            usage=("add-note <назва нотатки> [вміст нотатки] [теги]"),
            description=(
                "Додати нотатку "
                "('-' для пропуску поля, напр.: add-note Заголовок - супер-тег"
                '. Вміст з пробілом писати у лапках: "Anna Petrenko", '
                "теги через пробіл - декілька тегів)."
            ),
            category="Notes",
            example='add-note "Список покупок" "Довгий список покупок" '
            '"покупки витрати магазин"',
        ),
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
        "show-note": Command(
            handler=partial(show_note, notebook),
            arg_completer=partial(complete_note_title, notebook),
            usage="show-note <назва>",
            description="Показати нотатку",
            category="Notes",
            example='show-note "Список покупок"',
        ),
        "all-notes": Command(
            handler=partial(all_notes, notebook),
            usage="all-notes",
            description="Показати всі нотатки",
            category="Notes",
            example="all-notes",
        ),
        "find-note": Command(
            handler=partial(find_note, notebook),
            usage="find-note <запит>",
            description="Знайти нотатки за назвою, текстом або тегами",
            category="Notes",
            example="find-note молоко",
        ),
        "sort-notes": Command(
            handler=partial(sort_notes, notebook),
            usage="sort-notes [--group]",
            description="Сортувати нотатки за тегами або показати групи",
            category="Notes",
            example="sort-notes --group",
        ),
    }
