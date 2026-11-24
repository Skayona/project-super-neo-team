class MissingContactError(Exception):
    def __init__(self, name: str):
        self.message = f"Contact {name} is missing"
        super().__init__(self.message)


class BirthdayError(Exception):
    def __init__(
        self, message="Invalid date format. Please use DD.MM.YYYY format."
    ):
        self.message = message
        super().__init__(self.message)


class ExtendedValueError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
