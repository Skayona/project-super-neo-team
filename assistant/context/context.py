from dataclasses import dataclass

from rich.console import Console

from assistant.contacts.address_book import AddressBook
from assistant.notes.notebook import Notebook
from assistant.storage.storage import (
    load_address_book,
    load_notebook,
    save_address_book,
    save_notebook,
)

console = Console()


@dataclass
class AssistantContext:
    """Keeps all book entities together"""

    address_book: AddressBook
    notebook: Notebook

    @classmethod
    def load(cls) -> "AssistantContext":
        address_book = load_address_book()
        notebook = load_notebook()
        return cls(address_book=address_book, notebook=notebook)

    def save_all(self) -> None:
        save_address_book(self.address_book)
        save_notebook(self.notebook)
