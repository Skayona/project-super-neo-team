"""Define the base class for validated fields."""

from abc import ABC, abstractmethod


class BaseField(ABC):
    """Normalize and validate a field value."""

    def __init__(self, value: str):
        """Initialize a field with a validated value."""
        normalized = self.normalize(value)
        self.validate(normalized)
        self.value = normalized

    @classmethod
    def normalize(cls, value: str) -> str:
        """Return the normalized value."""
        return value

    @classmethod
    @abstractmethod
    def validate(cls, value: str) -> None:
        """Validate a normalized value."""
        raise NotImplementedError

    def __str__(self) -> str:
        """Return the field value as text."""
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        """Compare fields by type and value."""
        if not isinstance(other, BaseField):
            return NotImplemented
        return type(self) is type(other) and self.value == other.value

    def __hash__(self) -> int:
        """Hash the field type and value."""
        return hash((type(self), self.value))
