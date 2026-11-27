"""Define handlers for note commands."""

from collections.abc import Iterable
from difflib import get_close_matches
from functools import partial

from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from assistant.core import (
    Command,
    CommandResult,
    MutationCommand,
    NoteNotFoundError,
    UsageError,
    input_error,
)
from assistant.notes.command_keys import NotesCommandKeys
from assistant.notes.fields import NoteTag
from assistant.notes.keywords import get_keywords
from assistant.notes.note import Note
from assistant.notes.notebook import Notebook
from assistant.ui import (
    format_card,
    format_error,
    format_info,
    format_success,
    format_table,
)

MATCH_ALL_FLAG = "--all"


def get_note(notebook: Notebook, title: str) -> Note:
    """Return a note or raise when it is missing."""
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
    content = ""
    tags: list[str] = []

    remaining = args[1:]

    if remaining:
        if remaining[0] == "-":
            remaining = remaining[1:]
        elif not remaining[0].startswith("#"):
            content = remaining[0]
            remaining = remaining[1:]

    for arg in remaining:
        if arg == "-":
            continue

        tags.extend(arg.split())

    return title, content, tags


def _render_notes_table(title: str, notes: list[Note]) -> Table | Panel:
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


@input_error
def add_note(notebook: Notebook, args: list[str]) -> CommandResult:
    """Create a note with optional content and tags."""
    title, content, tags = _parse_note_args(args)

    note = Note(
        title=title,
        content=content,
        tags=tags,
    )

    notebook.add_note(note)

    return CommandResult(
        format_success(f"Нотатку «{note.title.value}» успішно додано."),
        changed=True,
    )


@input_error
def show_note(notebook: Notebook, args: list[str]) -> CommandResult:
    """Display a note and its metadata."""
    if not args:
        raise UsageError("Вкажіть заголовок нотатки.")

    title = " ".join(args)
    note = get_note(notebook, title)

    tags = (
        ", ".join(f"#{tag}" for tag in sorted(t.value for t in note.tags))
        or "—"
    )

    return CommandResult(
        format_card(
            note.title.value,
            {
                "Текст": note.content.value,
                "Теги": tags,
                "Створено": note.created_at_display,
                "Оновлено": note.updated_at_display,
            },
        ),
        changed=False,
    )


@input_error
def all_notes(notebook: Notebook, args: list[str]) -> CommandResult:
    """Display all notes."""
    if args:
        raise UsageError("Команда не приймає аргументів.")

    if not notebook:
        return CommandResult(
            format_info(
                "Нотаток ще немає. Додайте: "
                f"{NotesCommandKeys.ADD_NOTE.value} ..."
            ),
            changed=False,
        )

    notes = sorted(
        reversed(list(notebook.values())),
        key=lambda note: note.created_at,
        reverse=True,
    )

    return CommandResult(
        _render_notes_table("Усі нотатки", notes),
        changed=False,
    )


@input_error
def find_note(notebook: Notebook, args: list[str]) -> CommandResult:
    """Find notes matching a query."""
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
        return CommandResult(
            format_info(f"За запитом «{query}» нічого не знайдено."),
            changed=False,
        )

    notes.sort(
        key=lambda note: note.created_at,
        reverse=True,
    )

    return CommandResult(
        _render_notes_table("Результати пошуку", notes),
        changed=False,
    )


@input_error
def edit_note(notebook: Notebook, args: list[str]) -> CommandResult:
    """Replace the content of a note."""
    if len(args) < 2:
        raise UsageError("Вкажіть заголовок нотатки та новий текст.")

    title = args[0]
    content = " ".join(args[1:])

    note = notebook.update_note(title, text=content)

    return CommandResult(
        format_success(
            f"Текст нотатки «{note.title.value}» успішно оновлено."
        ),
        changed=True,
    )


@input_error
def rename_note(notebook: Notebook, args: list[str]) -> CommandResult:
    """Rename a note."""
    if len(args) != 2:
        raise UsageError("Вкажіть поточний та новий заголовки нотатки.")

    old_title, new_title = args

    note = notebook.rename_note(old_title, new_title)

    return CommandResult(
        format_success(
            f"Нотатку «{old_title}» перейменовано на «{note.title.value}»."
        ),
        changed=True,
    )


@input_error
def delete_note(notebook: Notebook, args: list[str]) -> CommandResult:
    """Delete a note by title."""
    if not args:
        raise UsageError("Вкажіть заголовок нотатки.")

    title = " ".join(args).strip()
    note = notebook.find_note(title)

    if note is None:
        titles = {
            item.title.value.casefold(): item.title.value
            for item in notebook.values()
        }

        matches = get_close_matches(
            title.casefold(),
            list(titles),
            n=1,
            cutoff=0.6,
        )

        message = f"Нотатка «{title}» не знайдена."

        if matches:
            message += f"\nМожливо, ви мали на увазі: «{titles[matches[0]]}»?"

        return CommandResult(
            format_error(message),
            changed=False,
        )

    notebook.delete_note(title)

    return CommandResult(
        format_success(f"Нотатку «{note.title.value}» успішно видалено."),
        changed=True,
    )


def format_tags(note: Note) -> str:
    """Format a note's tags for display."""
    return ", ".join(sorted(tag.value for tag in note.tags)) or "—"


@input_error
def add_tag(notebook: Notebook, args: list[str]) -> CommandResult:
    """Add tags to a note."""
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
    """Remove a tag from a note."""
    title, tag = args
    note = get_note(notebook, title)
    note.remove_tag(tag)
    return format_success(
        f"Тег '{NoteTag(tag).value}' видалено з нотатки «{note.title}»."
    )


@input_error
def find_tag(notebook: Notebook, args: list[str]) -> Table | Panel:
    """Find notes by one or more tags."""
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
    """Display all tags and their usage counts."""
    rows = [
        [tag, str(count)] for tag, count in sorted(notebook.all_tags().items())
    ]
    return format_table("Усі теги", ["Тег", "Кількість нотаток"], rows)


def complete_note_title(notebook: Notebook, args: list[str]) -> list[str]:
    """Suggest note titles for command input."""
    if len(args) == 0:
        return sorted(note.title.value for note in notebook.values())
    return []


def complete_note_tag(notebook: Notebook, args: list[str]) -> list[str]:
    """Suggest tags for a selected note."""
    if len(args) == 0:
        return complete_note_title(notebook, args)
    if len(args) == 1:
        note = notebook.find_note(args[0])
        return sorted(tag.value for tag in note.tags) if note else []
    return []


def complete_tags(notebook: Notebook, args: list[str]) -> list[str]:
    """Suggest unused tags and the all-tags option."""
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
    """Display notes sorted or grouped by tag."""
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
    """Build the note command definitions."""
    return {
        NotesCommandKeys.ADD_NOTE: MutationCommand(
            handler=partial(add_note, notebook),
            usage=(
                f"{NotesCommandKeys.ADD_NOTE.value} "
                "<назва> [текст] [тег1 тег2 ...]"
            ),
            description=(
                "Додати нотатку. "
                "Назву та текст із пробілами пишіть у лапках. "
                "Теги можна вводити з символом # або без нього. "
                "Використовуйте '-' для пропуску поля."
            ),
            category="Notes",
            example=(
                f"{NotesCommandKeys.ADD_NOTE.value} "
                '"Список покупок" "Молоко та хліб" #дім магазин'
            ),
            keywords=get_keywords(NotesCommandKeys.ADD_NOTE),
        ),
        NotesCommandKeys.ADD_TAG: MutationCommand(
            handler=partial(add_tag, notebook),
            arg_completer=partial(complete_note_title, notebook),
            usage=(
                f"{NotesCommandKeys.ADD_TAG.value} <назва> <тег1> [тег2 ...]"
            ),
            description="Додати нотатці один або кілька тегів",
            category="Notes",
            example=(
                f"{NotesCommandKeys.ADD_TAG.value} Покупки дім терміново"
            ),
            keywords=get_keywords(NotesCommandKeys.ADD_TAG),
        ),
        NotesCommandKeys.REMOVE_TAG: MutationCommand(
            handler=partial(remove_tag, notebook),
            arg_completer=partial(complete_note_tag, notebook),
            usage=f"{NotesCommandKeys.REMOVE_TAG.value} <назва> <тег>",
            description="Видалити тег із нотатки",
            category="Notes",
            example=(f"{NotesCommandKeys.REMOVE_TAG.value} Покупки терміново"),
            keywords=get_keywords(NotesCommandKeys.REMOVE_TAG),
        ),
        NotesCommandKeys.FIND_TAG: Command(
            handler=partial(find_tag, notebook),
            arg_completer=partial(complete_tags, notebook),
            usage=(
                f"{NotesCommandKeys.FIND_TAG.value} <тег1> [тег2 ...] [--all]"
            ),
            description=(
                "Знайти нотатки з будь-яким із тегів (--all — з усіма)"
            ),
            category="Notes",
            example=f"{NotesCommandKeys.FIND_TAG.value} дім робота --all",
            keywords=get_keywords(NotesCommandKeys.FIND_TAG),
        ),
        NotesCommandKeys.ALL_TAGS: Command(
            handler=partial(all_tags, notebook),
            usage=NotesCommandKeys.ALL_TAGS.value,
            description="Показати всі теги та кількість нотаток з ними",
            category="Notes",
            keywords=get_keywords(NotesCommandKeys.ALL_TAGS),
        ),
        NotesCommandKeys.SHOW_NOTE: Command(
            handler=partial(show_note, notebook),
            arg_completer=partial(complete_note_title, notebook),
            usage=f"{NotesCommandKeys.SHOW_NOTE.value} <назва>",
            description="Показати нотатку",
            category="Notes",
            example=f'{NotesCommandKeys.SHOW_NOTE.value} "Список покупок"',
            keywords=get_keywords(NotesCommandKeys.SHOW_NOTE),
        ),
        NotesCommandKeys.ALL_NOTES: Command(
            handler=partial(all_notes, notebook),
            usage=NotesCommandKeys.ALL_NOTES.value,
            description="Показати всі нотатки",
            category="Notes",
            example=NotesCommandKeys.ALL_NOTES.value,
            keywords=get_keywords(NotesCommandKeys.ALL_NOTES),
        ),
        NotesCommandKeys.FIND_NOTE: Command(
            handler=partial(find_note, notebook),
            usage=f"{NotesCommandKeys.FIND_NOTE.value} <запит>",
            description="Знайти нотатки за назвою, текстом або тегами",
            category="Notes",
            example=f"{NotesCommandKeys.FIND_NOTE.value} молоко",
            keywords=get_keywords(NotesCommandKeys.FIND_NOTE),
        ),
        NotesCommandKeys.SORT_NOTES: Command(
            handler=partial(sort_notes, notebook),
            usage=f"{NotesCommandKeys.SORT_NOTES.value} [--group]",
            description="Сортувати нотатки за тегами або показати групи",
            category="Notes",
            example=f"{NotesCommandKeys.SORT_NOTES.value} --group",
            keywords=get_keywords(NotesCommandKeys.SORT_NOTES),
        ),
        NotesCommandKeys.EDIT_NOTE: MutationCommand(
            handler=partial(edit_note, notebook),
            arg_completer=partial(complete_note_title, notebook),
            usage=(
                f"{NotesCommandKeys.EDIT_NOTE.value} <назва> <новий текст...>"
            ),
            description="Редагувати текст нотатки зі збереженням тегів",
            category="Notes",
            example=(
                f"{NotesCommandKeys.EDIT_NOTE.value} "
                '"Список покупок" Молоко та хліб'
            ),
            keywords=get_keywords(NotesCommandKeys.EDIT_NOTE),
        ),
        NotesCommandKeys.RENAME_NOTE: MutationCommand(
            handler=partial(rename_note, notebook),
            arg_completer=partial(complete_note_title, notebook),
            usage=(
                f"{NotesCommandKeys.RENAME_NOTE.value} "
                "<стара назва> <нова назва>"
            ),
            description="Змінити заголовок нотатки",
            category="Notes",
            example=(
                f"{NotesCommandKeys.RENAME_NOTE.value} "
                '"Список покупок" "Покупки"'
            ),
            keywords=get_keywords(NotesCommandKeys.RENAME_NOTE),
        ),
        NotesCommandKeys.DELETE_NOTE: MutationCommand(
            handler=partial(delete_note, notebook),
            arg_completer=partial(complete_note_title, notebook),
            usage=f"{NotesCommandKeys.DELETE_NOTE.value} <назва>",
            description="Видалити нотатку за заголовком",
            category="Notes",
            example=f'{NotesCommandKeys.DELETE_NOTE.value} "Список покупок"',
            keywords=get_keywords(NotesCommandKeys.DELETE_NOTE),
        ),
    }
