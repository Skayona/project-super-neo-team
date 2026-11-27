from enum import Enum


class NotesCommandKeys(str, Enum):
    ADD_NOTE = "add-note"
    ADD_TAG = "add-tag"
    REMOVE_TAG = "remove-tag"
    FIND_TAG = "find-tag"
    ALL_TAGS = "all-tags"
    SHOW_NOTE = "show-note"
    ALL_NOTES = "all-notes"
    FIND_NOTE = "find-note"
    SORT_NOTES = "sort-notes"
    EDIT_NOTE = "edit-note"
    RENAME_NOTE = "rename-note"
    DELETE_NOTE = "delete-note"
