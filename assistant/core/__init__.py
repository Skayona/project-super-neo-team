"""Core package containing exceptions and base field types."""

from assistant.core.base_field import BaseField
from assistant.core.command import Command
from assistant.core.command_result import CommandResult
from assistant.core.exceptions import (
    AddressValidationError,
    AlreadyExistsError,
    AssistantError,
    BirthdayValidationError,
    ContactExistsError,
    ContactNotFoundError,
    EmailValidationError,
    FieldValidationError,
    NameValidationError,
    NoteExistsError,
    NoteNotFoundError,
    NoteValidationError,
    NotFoundError,
    PhoneExistsError,
    PhoneNotFoundError,
    PhoneValidationError,
    TagValidationError,
    UsageError,
    ValidationError,
)
from assistant.core.input_error_decorator import input_error

__all__ = [
    "Command",
    "CommandResult",
    "AssistantError",
    "ValidationError",
    "FieldValidationError",
    "NameValidationError",
    "PhoneValidationError",
    "EmailValidationError",
    "BirthdayValidationError",
    "AddressValidationError",
    "NoteValidationError",
    "TagValidationError",
    "NotFoundError",
    "ContactNotFoundError",
    "NoteNotFoundError",
    "PhoneNotFoundError",
    "AlreadyExistsError",
    "PhoneExistsError",
    "ContactExistsError",
    "NoteExistsError",
    "UsageError",
    "input_error",
    "BaseField",
]
