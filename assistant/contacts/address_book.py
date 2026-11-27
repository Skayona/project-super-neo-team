"""Store and search contact records."""

import re
from collections import UserDict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from rich.console import Console

from assistant.contacts.fields import Birthday
from assistant.contacts.record import Record
from assistant.core.exceptions import (
    ContactExistsError,
    ContactNotFoundError,
    UsageError,
)
from assistant.ui.views import format_warn

console = Console()


@dataclass(frozen=True)
class UpcomingBirthday:
    """Represent an upcoming birthday and its reminder date."""

    name: str
    birthday: date
    days_left: int
    age: int
    congratulation_date: date


class AddressBook(UserDict[str, Record]):
    """Store and search contact records."""

    def add_record(self, record: Record) -> None:
        """Add a contact record."""
        name = record.name.value
        if self.find(name) is not None:
            raise ContactExistsError(name)

        self.data[name] = record

    def find(self, name: str) -> Record | None:
        """Find a contact by name."""
        needle = name.strip().casefold()
        return next(
            (
                record
                for key, record in self.data.items()
                if key.casefold() == needle
            ),
            None,
        )

    def search(self, query: str) -> list[Record]:
        """Search contact details for a query."""
        query = query.strip().casefold()
        if not query:
            return []

        phone_query = ""
        if re.fullmatch(r"[\d\s()+.-]+", query):
            phone_query = re.sub(r"\D", "", query)

        matches = []
        for record in self.values():
            fields = (
                record.name,
                record.email,
                record.address,
                record.birthday,
            )
            matches_field = any(
                field is not None and query in field.value.casefold()
                for field in fields
            )
            matches_phone = phone_query and any(
                phone_query in re.sub(r"\D", "", phone.value)
                for phone in record.phones
            )
            if matches_field or matches_phone:
                matches.append(record)
        return matches

    def delete(self, name: str) -> None:
        """Delete a contact by name."""
        record = self.find(name)
        if record is None:
            raise ContactNotFoundError(name)
        del self.data[record.name.value]

    def to_dict(self) -> dict[str, dict[str, str]]:
        """Serialize all contact records."""
        return {name: record.to_dict() for name, record in self.data.items()}

    def get_upcoming_birthdays(self, days: int = 7) -> list[UpcomingBirthday]:
        """List birthdays due within the given number of days."""
        if not 1 <= days <= 365:
            raise UsageError("Кількість днів — ціле число від 1 до 365")

        today = date.today()
        results = []
        for name, record in self.items():
            if record.birthday is None:
                continue

            birth_date = datetime.strptime(
                record.birthday.value, Birthday.DATE_FORMAT
            ).date()
            birthday = self.__handle_leap_year(birth_date, today.year)
            if birthday < today:
                birthday = self.__handle_leap_year(birth_date, today.year + 1)

            days_left = (birthday - today).days
            if days_left > days:
                continue

            congratulation_date = birthday
            if birthday.weekday() >= 5:
                congratulation_date += timedelta(days=7 - birthday.weekday())
            results.append(
                UpcomingBirthday(
                    name,
                    birthday,
                    days_left,
                    birthday.year - birth_date.year,
                    congratulation_date,
                )
            )
        return sorted(results, key=lambda result: result.birthday)

    @staticmethod
    def __handle_leap_year(d: date, year: int) -> date:
        try:
            return d.replace(year=year)
        except ValueError:
            return d.replace(year=year, month=3, day=1)

    @staticmethod
    def print_unpack_book_error() -> None:
        """Display a warning about invalid address-book data."""
        console.print(
            format_warn(
                "Файл адресної книги пошкоджено або недоступний. "
                "Завантажено порожню книгу."
            )
        )

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "AddressBook":
        """Build an address book from serialized records."""
        book = AddressBook()
        if not isinstance(data, dict):
            AddressBook.print_unpack_book_error()
            return book

        skipped = 0
        for record_data in data.values():
            if not isinstance(record_data, dict):
                skipped += 1
                continue

            try:
                book.add_record(Record.from_dict(record_data))
            except Exception:
                skipped += 1

        if skipped:
            console.print(
                format_warn(
                    "Під час завантаження книги було пропущено некоректних "
                    f"записів: {skipped}.\n"
                    "Некоректні аписи будуть видалені з книги."
                )
            )
        return book
