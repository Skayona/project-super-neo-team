from collections import Counter, UserDict
from dataclasses import dataclass, replace
from typing import Any

from assistant.core.exceptions import ExtendedValueError, NoteExistsError


@dataclass(frozen=True)
class Note:
    title: str
    text: str
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        title = self.title.strip()
        if not title:
            raise ExtendedValueError(
                "Заголовок нотатки не може бути порожнім."
            )
        if not self.text.strip():
            raise ExtendedValueError("Текст нотатки не може бути порожнім.")

        tags = dict.fromkeys(
            tag.strip().casefold() for tag in self.tags if tag.strip()
        )
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "tags", tuple(tags))


class Notebook(UserDict[str, Note]):
    def add_note(self, note: Note) -> None:
        key = note.title.casefold()
        if key in self:
            raise NoteExistsError(f"Нотатка «{note.title}» вже існує.")
        self[key] = note

    def find_note(self, title: str) -> Note | None:
        return self.get(title.strip().casefold())

    def delete_note(self, title: str) -> None:
        note = self._require_note(title)
        del self[note.title.casefold()]

    def rename_note(self, title: str, new_title: str) -> Note:
        current = self._require_note(title)
        updated = replace(current, title=new_title)
        old_key = current.title.casefold()
        new_key = updated.title.casefold()
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
        current = self._require_note(title)
        updated = replace(
            current,
            text=current.text if text is None else text,
            tags=current.tags if tags is None else tags,
        )
        self[current.title.casefold()] = updated
        return updated

    def _require_note(self, title: str) -> Note:
        note = self.find_note(title)
        if note is None:
            raise ExtendedValueError(f"Нотатку «{title}» не знайдено.")
        return note

    def search(self, query: str) -> list[Note]:
        query = query.strip().casefold()
        return [
            note for note in self.values()
            if any(
                query in field.casefold()
                for field in (note.title, note.text, *note.tags)
            )
        ]

    def find_by_tags(self, *tags: str, match_all: bool = False) -> list[Note]:
        wanted = {tag.strip().casefold() for tag in tags if tag.strip()}
        if not wanted:
            return []
        if match_all:
            return [note for note in self.values() if wanted <= set(note.tags)]
        return [
            note for note in self.values() if wanted.intersection(note.tags)
        ]

    def all_tags(self) -> dict[str, int]:
        tags = (tag for note in self.values() for tag in note.tags)
        return dict(Counter(tags))

    def group_by_tags(self) -> dict[str, list[Note]]:
        groups: dict[str, list[Note]] = {
            tag: [] for tag in sorted(self.all_tags())
        }
        untagged = []
        for note in self.values():
            for tag in note.tags:
                groups[tag].append(note)
            if not note.tags:
                untagged.append(note)
        if untagged:
            groups["без тегів"] = groups.pop("без тегів", []) + untagged
        return groups

    def sort_by_tags(self) -> list[Note]:
        return sorted(
            self.values(),
            key=lambda note: (
                not note.tags,
                min(note.tags, default=""),
                len(note.tags),
                note.title.casefold(),
            ),
        )

    def to_dict(self) -> dict[str, dict[str, str | list[str]]]:
        return {
            key: {
                "title": note.title,
                "text": note.text,
                "tags": list(note.tags),
            }
            for key, note in self.items()
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Notebook":
        notebook = cls()
        for item in data.values():
            if not isinstance(item, dict):
                raise ExtendedValueError("Некоректний формат нотатки.")
            title, text = item.get("title"), item.get("text")
            tags = item.get("tags", [])
            if (
                not isinstance(title, str)
                or not isinstance(text, str)
                or not isinstance(tags, list)
                or not all(isinstance(tag, str) for tag in tags)
            ):
                raise ExtendedValueError("Некоректний формат нотатки.")
            notebook.add_note(Note(title, text, tuple(tags)))
        return notebook
