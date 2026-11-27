"""Store and search notes."""

from collections import Counter, UserDict
from datetime import datetime
from typing import Any

from rich.console import Console

from assistant.core.exceptions import NoteExistsError, NoteNotFoundError
from assistant.notes.fields import NoteTag
from assistant.notes.note import Note

_console = Console()


class Notebook(UserDict[str, Note]):
    """Store and organize notes."""

    def add_note(self, note: Note) -> None:
        """Add a note to the notebook."""
        key = note.title.value.casefold()
        if key in self:
            raise NoteExistsError(note.title.value)
        self[key] = note

    def find_note(self, title: str) -> Note | None:
        """Find a note by title."""
        return self.get(title.strip().casefold())

    def delete_note(self, title: str) -> None:
        """Delete a note by title."""
        note = self._require_note(title)
        del self[note.title.value.casefold()]

    def rename_note(self, title: str, new_title: str) -> Note:
        """Rename a note and return the updated note."""
        current = self._require_note(title)
        updated = Note(
            new_title,
            current.content.value,
            (tag.value for tag in current.tags),
            created_at=current.created_at,
            updated_at=datetime.now().replace(microsecond=0),
        )
        old_key = current.title.value.casefold()
        new_key = updated.title.value.casefold()
        if new_key != old_key:
            self.add_note(updated)
            del self[old_key]
        else:
            self[old_key] = updated
        return updated

    def update_note(
        self,
        title: str,
        text: str | None = None,
        tags: tuple[str, ...] | None = None,
    ) -> Note:
        """Update note content or tags and return the updated note."""
        current = self._require_note(title)
        updated = Note(
            current.title.value,
            current.content.value if text is None else text,
            (tag.value for tag in current.tags) if tags is None else tags,
            created_at=current.created_at,
            updated_at=datetime.now().replace(microsecond=0),
        )
        self[current.title.value.casefold()] = updated
        return updated

    def _require_note(self, title: str) -> Note:
        note = self.find_note(title)
        if note is None:
            raise NoteNotFoundError(title)
        return note

    def search(self, query: str) -> list[Note]:
        """Search note titles, content, and tags."""
        query = query.strip().casefold()
        return [
            note
            for note in self.values()
            if any(
                query in field.casefold()
                for field in (
                    note.title.value,
                    note.content.value,
                    *self._tags(note),
                )
            )
        ]

    def find_by_tags(self, *tags: str, match_all: bool = False) -> list[Note]:
        """Find notes matching any or all supplied tags."""
        wanted = {NoteTag(tag).value for tag in tags}
        if not wanted:
            return []
        if match_all:
            return [
                note for note in self.values() if wanted <= self._tags(note)
            ]
        return [
            note
            for note in self.values()
            if wanted.intersection(self._tags(note))
        ]

    def all_tags(self) -> dict[str, int]:
        """Count each tag used in the notebook."""
        tags = (tag for note in self.values() for tag in self._tags(note))
        return dict(Counter(tags))

    def group_by_tags(self) -> dict[str, list[Note]]:
        """Group notes by tag, including untagged notes."""
        groups: dict[str, list[Note]] = {
            tag: [] for tag in sorted(self.all_tags())
        }
        untagged = []
        for note in self.values():
            for tag in self._tags(note):
                groups[tag].append(note)
            if not note.tags:
                untagged.append(note)
        if untagged:
            groups["без тегів"] = groups.pop("без тегів", []) + untagged
        return groups

    def sort_by_tags(self) -> list[Note]:
        """Sort notes by tags and title."""
        return sorted(
            self.values(),
            key=lambda note: (
                not note.tags,
                min(self._tags(note), default=""),
                len(note.tags),
                note.title.value.casefold(),
            ),
        )

    @staticmethod
    def _tags(note: Note) -> set[str]:
        return {tag.value for tag in note.tags}

    def to_dict(self) -> dict[str, dict[str, str | list[str]]]:
        """Serialize all notes."""
        return {key: note.to_dict() for key, note in self.items()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Notebook":
        """Build a notebook from serialized notes."""
        from assistant.ui.views import format_warn

        notebook = cls()
        skipped = 0
        for item in data.values():
            if not isinstance(item, dict):
                skipped += 1
                continue
            try:
                notebook.add_note(Note.from_dict(item))
            except Exception:
                skipped += 1

        if skipped:
            _console.print(
                format_warn(
                    "Під час завантаження нотатника було пропущено "
                    f"некоректних записів: {skipped}.\n"
                    "Некоректні записи будуть видалені з нотатника."
                )
            )
        return notebook
