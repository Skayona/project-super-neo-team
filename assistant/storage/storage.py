import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from assistant.contacts.address_book import AddressBook
from assistant.core.exceptions import ExtendedValueError
from assistant.notes.notebook import Notebook

STORAGE_DIR = Path.home() / "assistant_storage"
CONTACTS_FILE = STORAGE_DIR / "address_book.json"
NOTES_FILE = Path.home() / ".personal_assistant" / "notebook.json"
LEGACY_CONTACTS_FILE = Path(".assistant_storage") / "address_book.json"


def save_address_book(
    book: AddressBook, file_path: Path = CONTACTS_FILE
) -> None:
    save_json(book.to_dict(), file_path)


def load_address_book(file_path: Path = CONTACTS_FILE) -> AddressBook:
    try:
        if file_path == CONTACTS_FILE and not file_path.exists():
            file_path = LEGACY_CONTACTS_FILE
        return AddressBook.from_dict(load_json(file_path))
    except (OSError, ValueError, ExtendedValueError):
        return AddressBook()


def save_notebook(
    notebook: Notebook, file_path: Path = NOTES_FILE
) -> None:
    save_json(notebook.to_dict(), file_path)


def load_notebook(file_path: Path = NOTES_FILE) -> Notebook:
    try:
        return Notebook.from_dict(load_json(file_path))
    except FileNotFoundError:
        return Notebook()
    except (ValueError, OSError) as error:
        raise ExtendedValueError(
            "Не вдалося прочитати файл нотаток."
        ) from error


def save_json(data: object, file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    handle = NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=file_path.parent, delete=False
    )
    temp_path = Path(handle.name)
    try:
        with handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        os.replace(temp_path, file_path)
    finally:
        temp_path.unlink(missing_ok=True)


def load_json(file_path: Path) -> dict[str, Any]:
    with file_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Очікувався JSON-обʼєкт.")
    return data
