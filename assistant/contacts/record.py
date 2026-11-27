"""Represent a contact and its details."""

from contextlib import suppress
from typing import Any, TypedDict

from assistant.contacts.fields import Address, Birthday, Email, Name, Phone
from assistant.core.exceptions import (
    BirthdayExistsError,
    BirthdayNotFoundError,
    NotFoundError,
    PhoneExistsError,
    PhoneNotFoundError,
    ValidationError,
)


class RecordData(TypedDict):
    """Represent the JSON-compatible data for a contact record."""

    name: str
    phones: list[str]
    birthday: str | None
    email: str | None
    address: str | None


class Record:
    """Store the details for one contact."""

    def __init__(self, name: str) -> None:
        """Initialize a contact record."""
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.email: Email | None = None
        self.birthday: Birthday | None = None
        self.address: Address | None = None

    def add_phone(self, phone: str) -> None:
        """Add a phone number."""
        new_phone = Phone(phone)
        if self.find_phone(new_phone.value):
            raise PhoneExistsError(new_phone.value, self.name.value)
        self.phones.append(new_phone)

    def add_email(self, value: str) -> None:
        """Set the contact email."""
        self.email = Email(value)

    def edit_email(self, value: str) -> None:
        """Replace the contact email."""
        if self.email is None:
            raise NotFoundError(f"У контакту {self.name.value} немає email.")
        self.email = Email(value)

    def delete_email(self) -> None:
        """Remove the contact email."""
        if self.email is None:
            raise NotFoundError(f"У контакту {self.name.value} немає email.")
        self.email = None

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Replace an existing phone number."""
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit is None:
            raise PhoneNotFoundError(old_phone)
        replacement = Phone(new_phone)
        if replacement != phone_to_edit and self.find_phone(replacement.value):
            raise PhoneExistsError(replacement.value, self.name.value)
        index = self.phones.index(phone_to_edit)
        self.phones[index] = replacement

    def find_phone(self, number: str) -> Phone | None:
        """Find a phone number by its normalized value."""
        target = Phone.normalize(number)
        return next(
            (phone for phone in self.phones if phone.value == target),
            None,
        )

    def delete_phone(self, phone: str) -> None:
        """Remove a phone number."""
        phone_to_delete = self.find_phone(phone)
        if phone_to_delete:
            self.phones.remove(phone_to_delete)
        else:
            raise PhoneNotFoundError(phone)

    def add_birthday(self, date: str) -> None:
        """Set the contact birthday."""
        if self.birthday is not None:
            raise BirthdayExistsError(self.name.value)
        self.birthday = Birthday(date)

    def delete_birthday(self) -> None:
        """Remove the contact birthday."""
        if self.birthday is None:
            raise BirthdayNotFoundError(self.name.value)
        self.birthday = None

    def change_birthday(self, date: str) -> None:
        """Replace the contact birthday."""
        if self.birthday is None:
            raise BirthdayNotFoundError(self.name.value)

        self.birthday = Birthday(date)

    def add_address(self, value: str) -> None:
        """Set the contact address."""
        self.address = Address(value)

    def edit_address(self, value: str) -> None:
        """Replace the contact address."""
        if self.address is None:
            raise NotFoundError(f"У контакту {self.name.value} немає адреси.")
        self.address = Address(value)

    def delete_address(self) -> None:
        """Remove the contact address."""
        if self.address is None:
            raise NotFoundError(f"У контакту {self.name.value} немає адреси.")
        self.address = None

    def to_dict(self) -> RecordData:
        """Serialize the contact details."""
        return {
            "name": self.name.value,
            "phones": [p.value for p in self.phones],
            "birthday": self.birthday.value if self.birthday else None,
            "email": self.email.value if self.email else None,
            "address": self.address.value if self.address else None,
        }

    def show_all_phones(self) -> str:
        """Format all phone numbers as a string."""
        return "; ".join(p.value for p in self.phones)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Record":
        """Build a contact record from serialized data."""
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
        """Format the contact for display."""
        res = (
            f"Contact name: {self.name.value}, phones: "
            f"{'; '.join(p.value for p in self.phones)}"
        )
        if self.birthday:
            res += f", birthday: {self.birthday.value}"
        return res
