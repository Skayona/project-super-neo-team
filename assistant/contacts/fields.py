import re
from datetime import date, datetime

from assistant.core.base_field import BaseField
from assistant.core.exceptions import (
    AddressValidationError,
    BirthdayValidationError,
    EmailValidationError,
    NameValidationError,
    PhoneValidationError,
)


class Name(BaseField):
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


class Phone(BaseField):
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


class Email(BaseField):
    MAX_LENGTH = 254
    _PATTERN = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")

    @classmethod
    def normalize(cls, value: str) -> str:
        return value.strip().lower()

    @classmethod
    def validate(cls, value: str) -> None:
        if len(value) > cls.MAX_LENGTH or not cls._PATTERN.fullmatch(value):
            raise EmailValidationError(value)


class Birthday(BaseField):
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


class Address(BaseField):
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
