from dataclasses import dataclass, field

from rich.console import Console

from assistant.contacts.address_book import AddressBook
from assistant.core.exceptions import AssistantError
from assistant.notes.notebook import Notebook
from assistant.storage.storage import (
    load_address_book,
    load_notebook,
    save_address_book,
    save_notebook,
)
from assistant.ui.views import format_warn

console = Console()


@dataclass
class AssistantContext:
    """Keeps all book entities together"""

    address_book: AddressBook
    notebook: Notebook = field(default_factory=Notebook)

    @classmethod
    def load(cls) -> "AssistantContext":
        address_book = load_address_book()
        try:
            notebook = load_notebook()
        except AssistantError as error:
            console.print(
                format_warn(f"{error.message} Нотатки почнуться з нуля.")
            )
            notebook = Notebook()
        return cls(address_book=address_book, notebook=notebook)

    def save_all(self) -> None:
        save_address_book(self.address_book)
        save_notebook(self.notebook)
