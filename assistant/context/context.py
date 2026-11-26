from dataclasses import dataclass
from typing import Any

from assistant.contacts.address_book import AddressBook
from assistant.storage.storage import save_address_book


@dataclass
class AssistantContext:
    """Keeps all book entities together"""

    address_book: AddressBook
    notebook: Any | None = None  # Replace Any with NoteBook when ready

    def save_all(self) -> None:
        save_address_book(self.address_book)
        if self.notebook is not None:
            # save_notebook(self.notebook) - update when NoteBook is ready
            pass
