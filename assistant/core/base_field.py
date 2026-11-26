from abc import ABC, abstractmethod


class BaseField(ABC):
    def __init__(self, value: str):
        normalized = self.normalize(value)
        self.validate(normalized)
        self.value = normalized

    @classmethod
    def normalize(cls, value: str) -> str:
        return value

    @classmethod
    @abstractmethod
    def validate(cls, value: str) -> None:
        raise NotImplementedError

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseField):
            return NotImplemented
        return type(self) is type(other) and self.value == other.value

    def __hash__(self) -> int:
        return hash((type(self), self.value))
