"""Storage layer for the Personal Assistant application."""

from assistant.storage.storage import (
    load_address_book,
    save_address_book,
)

__all__ = ["load_address_book", "save_address_book"]
