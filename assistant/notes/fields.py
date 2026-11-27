"""Normalize and validate note fields."""

import re

from assistant.core.base_field import BaseField
from assistant.core.exceptions import NoteValidationError, TagValidationError


class NoteTitle(BaseField):
    """Normalize and validate a note title."""

    MAX_LENGTH = 80

    @classmethod
    def normalize(cls, value: str) -> str:
        """Strip surrounding whitespace."""
        return value.strip()

    @classmethod
    def validate(cls, value: str) -> None:
        """Validate the note title."""
        if not value:
            raise NoteValidationError(value)
        if len(value) > cls.MAX_LENGTH:
            raise NoteValidationError(
                value,
                f"Заголовок нотатки задовгий: "
                f"максимум {cls.MAX_LENGTH} символів.",
            )


class NoteContent(BaseField):
    """Normalize and validate note content."""

    MAX_LENGTH = 5000

    @classmethod
    def normalize(cls, value: str) -> str:
        """Strip surrounding whitespace."""
        return value.strip()

    @classmethod
    def validate(cls, value: str) -> None:
        """Validate the note content length."""
        if len(value) > cls.MAX_LENGTH:
            raise NoteValidationError(
                value,
                f"Текст нотатки задовгий: максимум {cls.MAX_LENGTH} символів.",
            )


class NoteTag(BaseField):
    """Normalize and validate a note tag."""

    _PATTERN = re.compile(r"[\w-]{1,30}")

    @classmethod
    def normalize(cls, value: str) -> str:
        """Remove a leading hash and lowercase the tag."""
        return value.strip().lstrip("#").lower()

    @classmethod
    def validate(cls, value: str) -> None:
        """Validate the tag format."""
        if not cls._PATTERN.fullmatch(value):
            raise TagValidationError(value)
