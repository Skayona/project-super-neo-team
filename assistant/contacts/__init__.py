"""Contacts package."""

from assistant.contacts.address_book import AddressBook
from assistant.contacts.fields import (
    Address,
    Birthday,
    Email,
    Name,
    Phone,
)
from assistant.contacts.handlers_registry import build_contacts_commands
from assistant.contacts.record import Record

__all__ = [
    "AddressBook",
    "Record",
    "build_contacts_commands",
    "Name",
    "Phone",
    "Email",
    "Birthday",
    "Address",
]
