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


class NameValidationError(ValidationError):
    def __init__(self):
        super().__init__("Ім'я не може бути порожнім.")


class PhoneValidationError(ValidationError):
    def __init__(self, phone=""):
        super().__init__(f"Номер телефону '{phone}' має містити 10 цифр.")


class EmailValidationError(ValidationError):
    def __init__(self, email=""):
        super().__init__(
            f"Адреса електронної пошти: {email} " "має некоректний формат."
        )


class BirthdayValidationError(ValidationError):
    def __init__(self, birthday=""):
        super().__init__(
            f"Некоректна дата народження '{birthday}'.\n"
            "Використовуйте формат ДД.ММ.РРРР."
        )


class AddressValidationError(ValidationError):
    def __init__(self):
        super().__init__("Адреса не може бути порожньою.")


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
            f"Номер телефону '{phone}' " f"вже існує для контакту '{name}'"
        )


class ContactExistsError(AlreadyExistsError):
    def __init__(self, name):
        super().__init__(f"Контакт '{name}' вже існує.")


class NoteExistsError(AlreadyExistsError):
    def __init__(self, note=""):
        super().__init__(f"Нотатка '{note}' вже існує.")
