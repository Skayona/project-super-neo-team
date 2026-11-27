"""Define identifiers for contact commands."""

from enum import Enum


class ContactCommandKeys(str, Enum):
    """Identify available contact commands."""

    ADD_CONTACT = "add-contact"
    DELETE_CONTACT = "delete-contact"
    FIND_CONTACT = "find-contact"
    SHOW_ALL_CONTACTS = "show-all-contacts"
    ADD_PHONE = "add-phone"
    SHOW_PHONE = "show-phone"
    CHANGE_PHONE = "change-phone"
    DELETE_PHONE = "delete-phone"
    ADD_BIRTHDAY = "add-birthday"
    SHOW_BIRTHDAY = "show-birthday"
    CHANGE_BIRTHDAY = "change-birthday"
    DELETE_BIRTHDAY = "delete-birthday"
    UPCOMING_BIRTHDAYS = "upcoming-birthdays"
    ADD_EMAIL = "add-email"
    CHANGE_EMAIL = "change-email"
    DELETE_EMAIL = "delete-email"
    ADD_ADDRESS = "add-address"
    CHANGE_ADDRESS = "change-address"
    DELETE_ADDRESS = "delete-address"
