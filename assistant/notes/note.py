from collections.abc import Iterable
from datetime import datetime
from typing import Any

from assistant.core.exceptions import NotFoundError
from assistant.notes.fields import NoteContent, NoteTag, NoteTitle

DISPLAY_FORMAT = "%d.%m.%Y %H:%M"


def _now() -> datetime:
    return datetime.now().replace(microsecond=0)


class Note:
    def __init__(
        self,
        title: str,
        content: str = "",
        tags: Iterable[str] = (),
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.title = NoteTitle(title)
        self.content = NoteContent(content)
        self.tags: set[NoteTag] = {NoteTag(tag) for tag in tags}
        self.created_at = created_at or _now()
        self.updated_at = updated_at or self.created_at

    def add_tags(self, *tags: str) -> None:
        new_tags = {NoteTag(tag) for tag in tags}
        if not new_tags <= self.tags:
            self.tags |= new_tags
            self._touch()

    def remove_tag(self, tag: str) -> None:
        target = NoteTag(tag)
        if target not in self.tags:
            raise NotFoundError(
                f"У нотатки «{self.title.value}» немає тегу '{target.value}'."
            )
        self.tags.remove(target)
        self._touch()

    def edit_content(self, text: str) -> None:
        self.content = NoteContent(text)
        self._touch()

    def _touch(self) -> None:
        self.updated_at = _now()

    @property
    def created_at_display(self) -> str:
        return self.created_at.strftime(DISPLAY_FORMAT)

    @property
    def updated_at_display(self) -> str:
        return self.updated_at.strftime(DISPLAY_FORMAT)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title.value,
            "content": self.content.value,
            "tags": sorted(tag.value for tag in self.tags),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Note":
        return cls(
            title=data["title"],
            content=data.get("content", ""),
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Note):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def __str__(self) -> str:
        tags = ", ".join(
            f"#{tag}" for tag in sorted(t.value for t in self.tags)
        )
        return (
            f"{self.title.value} ({self.updated_at_display})"
            f"{f' [{tags}]' if tags else ''}: {self.content.value}"
        )
