from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

from tomlkit.items import (
    AbstractTable,
    Array,
    Comment,
    Item,
    Key,
    String,
    Table,
    Trivia,
    Whitespace,
    _ArrayItemGroup,
)

if sys.version_info >= (3, 8):  # pragma: no cover (py38+)
    from typing import Protocol
else:  # pragma: no cover (<py38)
    from typing_extensions import Protocol


class SupportsDunderLT(Protocol):
    def __lt__(self, __other: Any) -> bool:  # noqa: U101
        ...


class SupportsDunderGT(Protocol):
    def __gt__(self, __other: Any) -> bool:  # noqa: U101
        ...


def order_keys(
    table: AbstractTable,
    to_pin: Sequence[str] | None = None,
    sort_key: None | Callable[[tuple[str, tuple[Key, Item]]], SupportsDunderLT | SupportsDunderGT] = None,
) -> None:
    body = table.value.body
    entries = {i.key: (i, v) for (i, v) in body if isinstance(i, Key)}
    body.clear()

    for pin in to_pin or []:  # push pinned to start
        if pin in entries:
            body.append(entries[pin])
            del entries[pin]
    # append the rest
    if sort_key is None:
        body.extend(entries.values())
    else:
        body.extend(v for k, v in sorted(entries.items(), key=sort_key))

    if isinstance(table, Table):
        body.append((None, Whitespace("\n")))  # add trailing newline to separate


@dataclass
class ArrayEntries:
    text: String
    comments: list[Comment] = field(default_factory=list)


def sorted_array(
    array: Array | None, indent: int, key: Callable[[ArrayEntries], str] = lambda e: str(e.text).lower()
) -> None:
    if array is None:
        return
    body = array._value

    entries: list[ArrayEntries] = []
    start: list[Comment] = []
    for group in body:
        for entry in group:
            if isinstance(entry, String):
                entries.append(ArrayEntries(entry))
            elif isinstance(entry, Comment):
                (entries[-1].comments if len(entries) else start).append(entry)

    body.clear()
    indent_text = " " * indent
    for start_entry in start:
        body.append(_ArrayItemGroup(indent=Whitespace(f"\n{indent_text}"), comment=start_entry))
    for element in sorted(entries, key=key):
        if element.comments:
            com = " ".join(i.trivia.comment[1:].strip() for i in element.comments)
            comment = Comment(Trivia(comment=f" # {com}", trail=""))
        else:
            comment = None
        group = _ArrayItemGroup(
            indent=Whitespace(f"\n{indent_text}"), value=element.text, comma=Whitespace(","), comment=comment
        )
        body.append(group)
    body.append(_ArrayItemGroup(indent=Whitespace("\n")))


__all__ = [
    "ArrayEntries",
    "sorted_array",
    "order_keys",
]
