import re
from dataclasses import dataclass
from datetime import datetime

from assistant.core.exceptions import BirthdayError, ExtendedValueError


@dataclass
class Field:
    value: str

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class Name(Field):
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ExtendedValueError(
                "Name cannot be empty. Please provide a valid name"
            )


class Phone(Field):
    def __init__(self, value: str):
        self.__validate_phone(value)
        super().__init__(value)

    def __validate_phone(self, value: str):
        if not self.__is_phone_valid(value):
            raise ExtendedValueError(
                f"Phone number {value} is incorrect. "
                "It should contain 10 numbers"
            )

    @staticmethod
    def __is_phone_valid(value: str) -> bool:
        pattern = r"^\d{10}$"
        match = re.match(pattern, value)
        return match is not None


class Email(Field):
    def __init__(self, value: str):
        self.__validate_email(value)
        super().__init__(value)

    def __validate_email(self, value: str):
        if not self.__is_email_valid(value):
            raise ExtendedValueError(f"Email {value} is incorrect.")

    @staticmethod
    def __is_email_valid(value: str) -> bool:
        pattern = r"^[\w.+-]+@[\w-]+\.[\w.-]+$"
        match = re.match(pattern, value)
        return match is not None


class Birthday(Field):
    __date_str_format = "%d.%m.%Y"

    def __init__(self, value: str):
        self.__validate_date(value)
        super().__init__(value)

    def __validate_date(self, value: str):
        try:
            datetime.strptime(value, self.__date_str_format)
        except ValueError:
            raise BirthdayError
        except TypeError:
            raise BirthdayError(
                "Provided value is not a date. "
                "Please provide a date in DD.MM.YYYY format."
            )


class Address(Field):
    def __init__(self, value: str):
        self.__validate_address(value)
        super().__init__(value)

    def __validate_address(self, value: str):
        if not value:
            raise ExtendedValueError("Address is missing.")
