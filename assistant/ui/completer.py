"""Provide command and argument completion."""

import html
import shlex
from collections.abc import Iterable

from prompt_toolkit import HTML, PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.filters import has_completions
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.styles import Style

from assistant.core.command import Command


def _quote_suggestion(value: str) -> str:
    if not any(char.isspace() or char in {'"', "\\"} for char in value):
        return value

    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


class AssistantCompleter(Completer):
    """Complete command names and their arguments."""

    def __init__(self, commands: dict[str, Command]) -> None:
        """Initialize the completer with available commands."""
        self.commands = commands

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """Yield completions for the current input."""
        text = document.text.lstrip()
        splitter = shlex.shlex(text, posix=True)
        splitter.quotes = '"'
        splitter.whitespace_split = True
        splitter.commenters = ""
        try:
            words = list(splitter)
        except ValueError:
            return

        ends_with_space = text.endswith(" ")

        if len(words) == 0 or (len(words) == 1 and not ends_with_space):
            prefix = words[0].lower() if words else ""
            for name, cmd in sorted(self.commands.items()):
                if name.startswith(prefix):
                    yield Completion(
                        text=name,
                        start_position=-len(prefix),
                        display=name,
                        display_meta=cmd.description,
                    )
            return

        # Check if autocomplete is possible for arguments like name/phone ect.
        cmd_name = words[0].lower()
        target_cmd = self.commands.get(cmd_name)
        if not target_cmd or not target_cmd.arg_completer:
            return

        # Check all additional entered arguments and the current one
        # that is still typing
        if ends_with_space:
            completed_args = words[1:]
            current_prefix = ""
        else:
            completed_args = words[1:-1]
            current_prefix = words[-1]

        # Check the command if it has arguments list
        # for the current entered argument
        suggestions = target_cmd.arg_completer(completed_args)
        for item in suggestions:
            if item.lower().startswith(current_prefix.lower()):
                yield Completion(
                    text=_quote_suggestion(item),
                    start_position=-len(current_prefix),
                    display=item,
                )


def get_bottom_toolbar(
    session: PromptSession[str],
    commands: dict[str, Command],
    help_command: str,
) -> HTML:
    """Build the prompt's bottom toolbar."""
    text = session.default_buffer.text.strip()
    if not text:
        return HTML(
            f"Введіть <b>{html.escape(help_command)}</b> "
            "або натисніть <b>Tab</b> для підказки"
        )

    cmd_name = text.split()[0].lower()
    cmd = commands.get(cmd_name)
    if cmd:
        # Escape usage text so names are not interpreted as HTML tags.
        escaped_usage = html.escape(cmd.usage)
        escaped_desc = html.escape(cmd.description)
        return HTML(
            f"<b>Синтаксис:</b> {escaped_usage} — <i>{escaped_desc}</i>\n"
            "Натисни <b>Enter</b> - для вибору"
        )
    return HTML("Натисніть <b>Tab</b> для автодоповнення")


PROMPT_STYLE = Style.from_dict(
    {
        "prompt": "bold ansibrightcyan",
        "bottom-toolbar": "noreverse bg:ansiblack ansibrightblack",
    }
)


def init_assistant_completer(
    commands: dict[str, Command],
    help_command: str,
) -> PromptSession[str]:
    """Create a prompt session with command completion."""
    kb = KeyBindings()

    @kb.add("enter", filter=has_completions)
    def _(event: KeyPressEvent) -> None:
        buf = event.current_buffer
        if buf.complete_state:
            completion = (
                buf.complete_state.current_completion
                or buf.complete_state.completions[0]
            )
            buf.apply_completion(completion)
            buf.insert_text(" ")

    @kb.add("backspace")
    def _(event: KeyPressEvent) -> None:
        buf = event.current_buffer
        buf.delete_before_cursor()
        if buf.text.strip():
            buf.start_completion(select_first=False)

    session: PromptSession[str] = PromptSession(
        completer=AssistantCompleter(commands),
        auto_suggest=AutoSuggestFromHistory(),
        key_bindings=kb,
        complete_while_typing=True,
        style=PROMPT_STYLE,
    )

    session.bottom_toolbar = lambda: get_bottom_toolbar(
        session,
        commands,
        help_command,
    )
    return session
