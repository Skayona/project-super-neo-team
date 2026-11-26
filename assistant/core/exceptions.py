class AssistantError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ValidationError(AssistantError):
    pass


class NotFoundError(AssistantError):
    pass


class AlreadyExistsError(AssistantError):
    pass


class UsageError(AssistantError):
    pass


# ===================== Validation Errors =====================


class FieldValidationError(ValidationError):
    default_message = "Некоректне значення '{value}'."

    def __init__(self, value: str = "", message: str | None = None):
        self.value = value
        super().__init__(message or self.default_message.format(value=value))


class NameValidationError(FieldValidationError):
    default_message = "Ім'я не може бути порожнім."


class PhoneValidationError(FieldValidationError):
    default_message = (
        "Номер телефону '{value}' має містити 10 цифр. "
        "Формат: 0501234567, 050-123-45-67 або +380501234567."
    )


class EmailValidationError(FieldValidationError):
    default_message = (
        "Email '{value}' має некоректний формат. "
        "Формат: name@example.com (до 254 символів)."
    )


class BirthdayValidationError(FieldValidationError):
    default_message = (
        "Некоректна дата народження '{value}'. "
        "Використовуйте формат ДД.ММ.РРРР."
    )


class AddressValidationError(FieldValidationError):
    default_message = "Адреса не може бути порожньою."


class NoteValidationError(ValidationError):
    def __init__(self):
        super().__init__("Текст нотатки не може бути порожнім.")


class TagValidationError(ValidationError):
    def __init__(self):
        super().__init__("Назва тегу не може бути порожньою.")


# ===================== Not Found Errors =====================


class ContactNotFoundError(NotFoundError):
    def __init__(self, name):
        super().__init__(f"Контакт '{name}' не знайдено.")


class NoteNotFoundError(NotFoundError):
    def __init__(self, note):
        super().__init__(f"Нотатка '{note}' не знайдена.")


class PhoneNotFoundError(NotFoundError):
    def __init__(self, phone=""):
        super().__init__(f"Телефон '{phone}' не знайдено.")


# ===================== Already Exists Errors =====================


class PhoneExistsError(AlreadyExistsError):
    def __init__(self, phone, name):
        super().__init__(
            f"Номер телефону '{phone}' вже існує для контакту '{name}'"
        )


class ContactExistsError(AlreadyExistsError):
    def __init__(self, name):
        super().__init__(f"Контакт '{name}' вже існує.")


class NoteExistsError(AlreadyExistsError):
    def __init__(self, note=""):
        super().__init__(f"Нотатка '{note}' вже існує.")
