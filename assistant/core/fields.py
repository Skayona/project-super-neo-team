import re
from abc import ABC, abstractmethod
from datetime import date, datetime

from assistant.core.exceptions import (
    AddressValidationError,
    BirthdayValidationError,
    EmailValidationError,
    NameValidationError,
    PhoneValidationError,
)


class Field(ABC):
    def __init__(self, value: str):
        normalized = self.normalize(value)
        self.validate(normalized)
        self.value = normalized

    @classmethod
    def normalize(cls, value: str) -> str:
        return value

    @classmethod
    @abstractmethod
    def validate(cls, value: str) -> None:
        raise NotImplementedError

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Field):
            return NotImplemented
        return type(self) is type(other) and self.value == other.value

    __hash__ = None  # type: ignore[assignment]


class Name(Field):
    MAX_LENGTH = 50

    @classmethod
    def normalize(cls, value: str) -> str:
        return value.strip()

    @classmethod
    def validate(cls, value: str) -> None:
        if not value:
            raise NameValidationError(value)
        if len(value) > cls.MAX_LENGTH:
            raise NameValidationError(
                value, f"Ім'я задовге: максимум {cls.MAX_LENGTH} символів."
            )


class Phone(Field):
    _SEPARATORS = re.compile(r"[\s\-()]")

    @classmethod
    def normalize(cls, value: str) -> str:
        digits = cls._SEPARATORS.sub("", value)
        if digits.startswith("+380"):
            digits = digits[3:]
        return digits

    @classmethod
    def validate(cls, value: str) -> None:
        if not re.fullmatch(r"\d{10}", value):
            raise PhoneValidationError(value)


class Email(Field):
    MAX_LENGTH = 254
    _PATTERN = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")

    @classmethod
    def normalize(cls, value: str) -> str:
        return value.strip().lower()

    @classmethod
    def validate(cls, value: str) -> None:
        if len(value) > cls.MAX_LENGTH or not cls._PATTERN.fullmatch(value):
            raise EmailValidationError(value)


class Birthday(Field):
    DATE_FORMAT = "%d.%m.%Y"
    MIN_YEAR = 1900
    _PATTERN = re.compile(r"\d{2}\.\d{2}\.\d{4}")

    @classmethod
    def validate(cls, value: str) -> None:
        if not cls._PATTERN.fullmatch(value):
            raise BirthdayValidationError(value)
        try:
            birthday = datetime.strptime(value, cls.DATE_FORMAT).date()
        except ValueError:
            raise BirthdayValidationError(value) from None
        if birthday.year < cls.MIN_YEAR:
            raise BirthdayValidationError(
                value,
                f"Некоректна дата народження '{value}'. "
                f"Рік має бути не раніше {cls.MIN_YEAR}.",
            )
        if birthday > date.today():
            raise BirthdayValidationError(
                value,
                f"Некоректна дата народження '{value}'. "
                "Дата не може бути в майбутньому.",
            )


class Address(Field):
    MAX_LENGTH = 200

    @classmethod
    def normalize(cls, value: str) -> str:
        return " ".join(value.split())

    @classmethod
    def validate(cls, value: str) -> None:
        if not value:
            raise AddressValidationError(value)
        if len(value) > cls.MAX_LENGTH:
            raise AddressValidationError(
                value, f"Адреса задовга: максимум {cls.MAX_LENGTH} символів."
            )
