"""Contacts package."""

from assistant.contacts.address_book import AddressBook
from assistant.contacts.handlers_registry import build_contacts_commands
from assistant.contacts.record import Record

__all__ = [
    "AddressBook",
    "Record",
    "build_contacts_commands",
]
