from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from tomlkit.items import Array, Comment, Item, Key, String, Trivia, Whitespace


def order_keys(body: list[tuple[Key | None, Item]], order: Sequence[str]) -> None:
    entries = {i.key: (i, v) for (i, v) in body if isinstance(i, Key)}
    body.clear()
    for key in order:
        if key in entries:
            body.append(entries[key])
            # body.append((None, Whitespace("\n")))
            del entries[key]
    body.extend(entries.values())  # append the rest
    body.append((None, Whitespace("\n")))  # add trailing newline to separate


@dataclass
class _ArrayEntries:
    text: String
    comments: list[Comment] = field(default_factory=list)


def multiline_sorted_array(array: Array, indent: int) -> None:
    body = array._value

    entries: list[_ArrayEntries] = []
    start: list[Comment] = []
    for entry in body:
        if isinstance(entry, String):
            entries.append(_ArrayEntries(entry))
        elif isinstance(entry, Comment):
            (entries[-1].comments if len(entries) else start).append(entry)

    body.clear()
    indent_text = " " * indent
    for entry in start:
        body.append(Whitespace(f"\n{indent_text}"))
        entry.indent(0)
        body.append(entry)
    for entry in sorted(entries, key=lambda e: str(e.text)):
        body.append(Whitespace(f"\n{indent_text}"))
        body.append(entry.text)
        body.append(Whitespace(","))
        if entry.comments:
            com = " ".join(i.trivia.comment[1:].strip() for i in entry.comments)
            body.append(Comment(Trivia(comment=f" # {com}", trail="")))
    body.append(Whitespace("\n"))
