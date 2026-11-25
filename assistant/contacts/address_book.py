from collections import UserDict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from assistant.contacts.record import Record
from assistant.core.exceptions import AlreadyExistsError, ExtendedValueError


@dataclass(frozen=True)
class UpcomingBirthday:
    name: str
    birthday: date
    days_left: int
    age: int
    congratulation_date: date


class AddressBook(UserDict[str, Record]):
    def add_record(self, record: Record) -> None:
        name = record.name.value
        if self.find(name) is not None:
            raise AlreadyExistsError("Contact already exists.")

        self.data[name] = record

    def find(self, name: str) -> Record | None:
        needle = name.strip().casefold()
        return next(
            (
                record
                for key, record in self.data.items()
                if key.casefold() == needle
            ),
            None,
        )

    def delete(self, name: str) -> None:
        record = self.find(name)
        if record is None:
            raise ExtendedValueError("Contact doesn't exist.")
        del self.data[record.name.value]

    def to_dict(self) -> dict[str, dict[str, str]]:
        return {name: record.to_dict() for name, record in self.data.items()}

    def get_upcoming_birthdays(self, days: int = 7) -> list[UpcomingBirthday]:
        if not 1 <= days <= 365:
            raise ExtendedValueError(
                "Кількість днів — ціле число від 1 до 365"
            )

        today = date.today()
        results = []
        for name, record in self.items():
            if record.birthday is None:
                continue

            birth_date = datetime.strptime(
                record.birthday.value, "%d.%m.%Y"
            ).date()
            birthday = self.__handle_leap_year(birth_date, today.year)
            if birthday < today:
                birthday = self.__handle_leap_year(
                    birth_date, today.year + 1
                )

            days_left = (birthday - today).days
            if days_left > days:
                continue

            congratulation_date = birthday
            if birthday.weekday() >= 5:
                congratulation_date += timedelta(days=7 - birthday.weekday())
            results.append(
                UpcomingBirthday(
                    name, birthday, days_left,
                    birthday.year - birth_date.year, congratulation_date,
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
    def from_dict(data: dict[str, Any]) -> "AddressBook":
        book = AddressBook()
        for record_data in data.values():
            book.add_record(Record.from_dict(record_data))
        return book
