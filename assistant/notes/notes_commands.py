from functools import partial

from assistant.core.command import Command, MutationCommand
from assistant.core.exceptions import NoteNotFoundError, UsageError
from assistant.notes.note import Note
from assistant.notes.notebook import Notebook
from assistant.ui.views import (
    format_card,
    format_error,
    format_success,
    format_table,
)


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
        raise UsageError('Вкажіть заголовок нотатки')

    title = " ".join(args)
    note = notebook.find_note(title)

    if note is None:
        raise NoteNotFoundError(title)

    tags = ", ".join(f"#{tag}" 
                     for tag in sorted(t.value for t in note.tags)) or "—"

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

def build_add_note_command(notebook: Notebook) -> MutationCommand:
    return MutationCommand(
        handler=partial(add_note, notebook),
        usage='add-note "Назва" текст #тег',
        description="Додати нову нотатку",
        category="Notes",
        example='add-note "Список покупок" молоко #дім',
    )


def build_show_note_command(notebook: Notebook) -> Command:
    return Command(
        handler=partial(show_note, notebook),
        usage='show-note "Назва"',
        description="Показати нотатку",
        category="Notes",
        example='show-note "Список покупок"',
    )


def build_all_notes_command(notebook: Notebook) -> Command:
    return Command(
        handler=partial(all_notes, notebook),
        usage="all-notes",
        description="Показати всі нотатки",
        category="Notes",
        example="all-notes",
    )


def build_find_note_command(notebook: Notebook) -> Command:
    return Command(
        handler=partial(find_note, notebook),
        usage="find-note <запит>",
        description="Знайти нотатки за назвою, текстом або тегами",
        category="Notes",
        example="find-note молоко",
    )
