import re

from assistant.core.exceptions import NoteValidationError, TagValidationError
from assistant.core.fields import Field


class NoteTitle(Field):
    MAX_LENGTH = 80

    @classmethod
    def normalize(cls, value: str) -> str:
        return value.strip()

    @classmethod
    def validate(cls, value: str) -> None:
        if not value:
            raise NoteValidationError(value)
        if len(value) > cls.MAX_LENGTH:
            raise NoteValidationError(
                value,
                f"Заголовок нотатки задовгий: "
                f"максимум {cls.MAX_LENGTH} символів.",
            )


class NoteContent(Field):
    MAX_LENGTH = 5000

    @classmethod
    def normalize(cls, value: str) -> str:
        return value.strip()

    @classmethod
    def validate(cls, value: str) -> None:
        if len(value) > cls.MAX_LENGTH:
            raise NoteValidationError(
                value,
                f"Текст нотатки задовгий: максимум {cls.MAX_LENGTH} символів.",
            )


class Tag(Field):
    _PATTERN = re.compile(r"[\w-]{1,30}")

    @classmethod
    def normalize(cls, value: str) -> str:
        return value.strip().lstrip("#").lower()

    @classmethod
    def validate(cls, value: str) -> None:
        if not cls._PATTERN.fullmatch(value):
            raise TagValidationError(value)
