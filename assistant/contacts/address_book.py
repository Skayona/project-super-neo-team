from collections import UserDict
from datetime import date, datetime, timedelta
from typing import Any

from assistant.contacts.record import Record
from assistant.core.exceptions import AlreadyExistsError, ExtendedValueError


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

    def get_upcoming_birthdays(self) -> list[dict[str, str]]:
        today = datetime.today().date()
        date_str_format = "%d.%m.%Y"
        congratulation_list: list[dict[str, str]] = []

        for name, user in self.data.items():
            if user.birthday is None:
                continue

            users_bd = datetime.strptime(
                user.birthday.value, date_str_format
            ).date()
            birthday_this_year = self.__handle_leap_year(users_bd, today.year)

            should_notify_next_year = (
                today.weekday() == 0
                and (today - birthday_this_year).days > 2
                or today.weekday() > 0
                and birthday_this_year < today
            )

            if should_notify_next_year:
                birthday_this_year = self.__handle_leap_year(
                    users_bd, today.year + 1
                )

            diff = (birthday_this_year - today).days

            if diff < 7:
                birthday_weekday = birthday_this_year.weekday()

                if birthday_weekday >= 5:
                    first_weekday = 7 - birthday_weekday
                    birthday_this_year += timedelta(days=first_weekday)

                congratulation_list.append(
                    {
                        "name": name,
                        "congratulation_date": birthday_this_year.strftime(
                            date_str_format
                        ),
                    }
                )

        return congratulation_list

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
