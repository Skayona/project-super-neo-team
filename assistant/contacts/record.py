from contextlib import suppress
from typing import Any

from assistant.contacts.fields import Address, Birthday, Email, Name, Phone
from assistant.core.exceptions import (
    BirthdayExistsError,
    BirthdayNotFoundError,
    NotFoundError,
    PhoneExistsError,
    PhoneNotFoundError,
    ValidationError,
)


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.email: Email | None = None
        self.birthday: Birthday | None = None
        self.address: Address | None = None

    def add_phone(self, phone: str) -> None:
        new_phone = Phone(phone)
        if self.find_phone(new_phone.value):
            raise PhoneExistsError(new_phone.value, self.name.value)
        self.phones.append(new_phone)

    def add_email(self, value: str) -> None:
        self.email = Email(value)

    def edit_email(self, value: str) -> None:
        if self.email is None:
            raise NotFoundError(f"У контакту {self.name.value} немає email.")
        self.email = Email(value)

    def delete_email(self) -> None:
        if self.email is None:
            raise NotFoundError(f"У контакту {self.name.value} немає email.")
        self.email = None

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit is None:
            raise PhoneNotFoundError(old_phone)
        replacement = Phone(new_phone)
        if replacement != phone_to_edit and self.find_phone(replacement.value):
            raise PhoneExistsError(replacement.value, self.name.value)
        index = self.phones.index(phone_to_edit)
        self.phones[index] = replacement

    def find_phone(self, number: str) -> Phone | None:
        target = Phone.normalize(number)
        return next(
            (phone for phone in self.phones if phone.value == target),
            None,
        )

    def delete_phone(self, phone: str) -> None:
        phone_to_delete = self.find_phone(phone)
        if phone_to_delete:
            self.phones.remove(phone_to_delete)
        else:
            raise PhoneNotFoundError(phone)

    def add_birthday(self, date: str) -> None:
        if self.birthday is not None:
            raise BirthdayExistsError(self.name.value)
        self.birthday = Birthday(date)

    def delete_birthday(self) -> None:
        if self.birthday is None:
            raise BirthdayNotFoundError(self.name.value)
        self.birthday = None

    def change_birthday(self, date: str) -> None:
        if self.birthday is None:
            raise BirthdayNotFoundError(self.name.value)

        self.birthday = Birthday(date)

    def add_address(self, value: str) -> None:
        self.address = Address(value)

    def edit_address(self, value: str) -> None:
        if self.address is None:
            raise NotFoundError(f"У контакту {self.name.value} немає адреси.")
        self.address = Address(value)

    def delete_address(self) -> None:
        if self.address is None:
            raise NotFoundError(f"У контакту {self.name.value} немає адреси.")
        self.address = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name.value,
            "phones": [p.value for p in self.phones],
            "birthday": self.birthday.value if self.birthday else None,
            "email": self.email.value if self.email else None,
            "address": self.address.value if self.address else None,
        }

    def show_all_phones(self) -> str:
        return "; ".join(p.value for p in self.phones)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Record":
        record = Record(data["name"])
        for phone in data.get("phones", []):
            if record.find_phone(phone) is None:
                with suppress(ValidationError):
                    record.add_phone(phone)
        setters = (
            (record.add_birthday, data.get("birthday")),
            (record.add_email, data.get("email")),
            (record.add_address, data.get("address")),
        )
        for setter, value in setters:
            if value:
                with suppress(ValidationError):
                    setter(value)
        return record

    def __str__(self) -> str:
        res = (
            f"Contact name: {self.name.value}, phones: "
            f"{'; '.join(p.value for p in self.phones)}"
        )
        if self.birthday:
            res += f", birthday: {self.birthday.value}"
        return res
