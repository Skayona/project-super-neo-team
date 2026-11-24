import json
import os
from pathlib import Path

from assistant.contacts.address_book import AddressBook

# saved in the same project instead of Path.home() / ".assistant_storage"
# to avoid clutter the users disk
STORAGE_DIR = Path(".assistant_storage")
CONTACTS_FILE = STORAGE_DIR / "address_book.json"


def check_storage_dir() -> Path:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    return STORAGE_DIR


def save_address_book(
    book: AddressBook, file_path: Path = CONTACTS_FILE
) -> None:
    check_storage_dir()
    temp_file = file_path.with_suffix(".tmp")
    data = book.to_dict()

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    os.replace(temp_file, file_path)


def load_address_book(file_path: Path = CONTACTS_FILE) -> AddressBook:
    if not file_path.exists():
        return AddressBook()

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
            return AddressBook.from_dict(data)
    except (json.JSONDecodeError, OSError):
        return AddressBook()
