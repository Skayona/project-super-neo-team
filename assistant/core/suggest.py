import re
from collections.abc import Iterable, Mapping
from difflib import get_close_matches

from assistant.core.command import Command


def similar_cmd(key: str, commands: Iterable[str]) -> list[str]:
    return get_close_matches(key, commands, n=3, cutoff=0.6)


def keyword_match(
    command: str,
    commands: Mapping[str, Command],
) -> list[str]:
    normalized_command = command.lower().replace("’", "'")
    words = re.findall(r"\w+(?:'\w+)*", normalized_command)

    # Unigrams, bigrams and trigrams
    format_command = set(words)

    format_command.update(
        " ".join(words[i : i + 2]) for i in range(len(words) - 1)
    )

    format_command.update(
        " ".join(words[i : i + 3]) for i in range(len(words) - 2)
    )

    matches_dict: dict[str, int] = {}
    for key, value in commands.items():
        if not value.keywords:
            continue
        matches = format_command & set(value.keywords)
        if matches:
            score = len(matches)
            matches_dict[key] = score

    sorted_matches = sorted(
        matches_dict.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [item[0] for item in sorted_matches[:3]]
