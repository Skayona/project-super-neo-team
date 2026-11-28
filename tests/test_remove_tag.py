"""Regression tests for the remove-tag command."""

import unittest

from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document

from assistant.cli import parse_input
from assistant.core.exceptions import UsageError
from assistant.notes.handlers_registry import build_notes_commands
from assistant.notes.note import Note
from assistant.notes.notebook import Notebook
from assistant.ui.completer import AssistantCompleter


class RemoveTagTests(unittest.TestCase):
    """Check suggestions, validation and successful removal."""

    def setUp(self) -> None:
        """Register commands against two notes with distinct tags."""
        self.notebook = Notebook()
        self.note = Note("Список покупок", tags=["дім", "магазин"])
        self.notebook.add_note(self.note)
        self.notebook.add_note(Note("Робота", tags=["офіс"]))
        self.commands = build_notes_commands(self.notebook)
        self.completer = AssistantCompleter(self.commands)

    def _suggestions(self, text: str) -> list[str]:
        return [
            item.text
            for item in self.completer.get_completions(
                Document(text), CompleteEvent(completion_requested=True)
            )
        ]

    def test_completes_note_titles(self) -> None:
        """Suggest titles and quote titles that contain spaces."""
        self.assertCountEqual(
            self._suggestions("remove-tag "), ['"Список покупок"', "Робота"]
        )

    def test_completes_only_selected_note_tags(self) -> None:
        """Suggest only the selected note's tags and filter by prefix."""
        command = 'remove-tag "Список покупок" '
        self.assertEqual(self._suggestions(command), ["дім", "магазин"])
        self.assertEqual(self._suggestions(command + "ма"), ["магазин"])

    def test_rejects_invalid_argument_count_without_changes(self) -> None:
        """Raise a usage error before changing the notebook."""
        saved = self.notebook.to_dict()
        for line in (
            "remove-tag",
            'remove-tag "Список покупок"',
            'remove-tag "Список покупок" дім зайвий',
        ):
            with self.subTest(line=line):
                command, args = parse_input(line)
                with self.assertRaises(UsageError):
                    self.commands[command].handler(args)
                self.assertEqual(self.notebook.to_dict(), saved)

    def test_removes_selected_tag(self) -> None:
        """Remove one tag and preserve the other tags."""
        command, args = parse_input('remove-tag "Список покупок" дім')
        result = self.commands[command].handler(args)
        self.assertTrue(result.changed)
        self.assertEqual({tag.value for tag in self.note.tags}, {"магазин"})
