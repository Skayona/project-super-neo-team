"""Define application and domain exceptions."""


class AssistantError(Exception):
    """Represent an application-level error."""

    def __init__(self, message: str) -> None:
        """Initialize an application error."""
        self.message = message
        super().__init__(message)


class ValidationError(AssistantError):
    """Represent invalid user input."""

    pass


class NotFoundError(AssistantError):
    """Represent a missing entity."""

    pass


class AlreadyExistsError(AssistantError):
    """Represent an existing entity conflict."""

    pass


class UsageError(AssistantError):
    """Represent invalid command usage."""

    pass


# ===================== Validation Errors =====================


class FieldValidationError(ValidationError):
    """Represent a field validation failure."""

    default_message = "Некоректне значення '{value}'."

    def __init__(
        self,
        value: str = "",
        message: str | None = None,
    ) -> None:
        """Initialize a field validation error."""
        self.value = value
        super().__init__(message or self.default_message.format(value=value))


class NameValidationError(FieldValidationError):
    """Represent an invalid contact name."""

    default_message = "Ім'я не може бути порожнім."


class PhoneValidationError(FieldValidationError):
    """Represent an invalid phone number."""

    default_message = (
        "Номер телефону '{value}' має містити 10 цифр. "
        "Формат: 0501234567, 050-123-45-67 або +380501234567."
    )


class EmailValidationError(FieldValidationError):
    """Represent an invalid email address."""

    default_message = (
        "Email '{value}' має некоректний формат. "
        "Формат: name@example.com (до 254 символів)."
    )


class BirthdayValidationError(FieldValidationError):
    """Represent an invalid birthday."""

    default_message = (
        "Некоректна дата народження '{value}'. "
        "Використовуйте формат ДД.ММ.РРРР."
    )


class AddressValidationError(FieldValidationError):
    """Represent an invalid address."""

    default_message = "Адреса не може бути порожньою."


class NoteValidationError(FieldValidationError):
    """Represent invalid note data."""

    default_message = "Заголовок нотатки не може бути порожнім."


class TagValidationError(FieldValidationError):
    """Represent an invalid note tag."""

    default_message = (
        "Некоректний тег '{value}'. Тег: 1–30 символів, "
        "лише літери, цифри, _ або -."
    )


# ===================== Not Found Errors =====================


class ContactNotFoundError(NotFoundError):
    """Represent a missing contact."""

    def __init__(self, name: str) -> None:
        """Initialize a missing-contact error."""
        super().__init__(f"Контакт '{name}' не знайдено.")


class NoteNotFoundError(NotFoundError):
    """Represent a missing note."""

    def __init__(self, note: str) -> None:
        """Initialize a missing-note error."""
        super().__init__(f"Нотатка '{note}' не знайдена.")


class PhoneNotFoundError(NotFoundError):
    """Represent a missing phone number."""

    def __init__(self, phone: str = "") -> None:
        """Initialize a missing-phone error."""
        super().__init__(f"Телефон '{phone}' не знайдено.")


class BirthdayNotFoundError(NotFoundError):
    """Represent a contact without a birthday."""

    def __init__(self, name: str) -> None:
        """Initialize a missing-birthday error."""
        super().__init__(f"У контакту {name} не вказано дату народження")


# ===================== Already Exists Errors =====================


class PhoneExistsError(AlreadyExistsError):
    """Represent a duplicate phone number."""

    def __init__(self, phone: str, name: str) -> None:
        """Initialize a duplicate-phone error."""
        super().__init__(
            f"Номер телефону '{phone}' вже існує для контакту '{name}'"
        )


class ContactExistsError(AlreadyExistsError):
    """Represent a duplicate contact."""

    def __init__(self, name: str) -> None:
        """Initialize a duplicate-contact error."""
        super().__init__(f"Контакт '{name}' вже існує.")


class NoteExistsError(AlreadyExistsError):
    """Represent a duplicate note."""

    def __init__(self, note: str = "") -> None:
        """Initialize a duplicate-note error."""
        super().__init__(f"Нотатка '{note}' вже існує.")


class BirthdayExistsError(AlreadyExistsError):
    """Represent a contact that already has a birthday."""

    def __init__(self, name: str) -> None:
        """Initialize a duplicate-birthday error."""
        super().__init__(f"У контакту {name} вже вказано дату народження")
