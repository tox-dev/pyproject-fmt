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


@dataclass
class TableComments:
    key_comments: dict[str, list[Comment]]
    top_comments: list[Comment]
    bottom_comments: list[Comment]


def store_comments(table: AbstractTable) -> TableComments:
    """
    Takes in a table, and returns a `TableComments` object.
    All comment lines in the table are attached to the key below it.
    Bottom comments are stored separately.

    The only exception to this rule is: If there's comments at the top of
    the table, separated from the rest of the body with newlines, then
    they are stored separately as top comments.
    """
    key_comments: dict[str, list[Comment]] = {}
    top_comments: list[Comment] = []
    bottom_comments: list[Comment] = []

    body = table.value.body
    first_key_index = -1
    for index, (key, item) in enumerate(body):
        if isinstance(key, Key):
            first_key_index = index
            break

    if first_key_index > 0 and isinstance(body[first_key_index - 1], Whitespace):
        # We may have comments at the top of the file.
        for _, item in body[:first_key_index]:
            if isinstance(item, Comment):
                top_comments.append(item)

        # delete the top comments
        del body[:first_key_index]

    # Start picking comments and attaching them to each key
    current_comments: list[Comment] = []
    for key, item in body:
        if isinstance(item, Comment):
            current_comments.append(item)
        elif isinstance(key, Key):
            key_comments[key.key] = current_comments
            current_comments = []

    # If we're left with comments at the bottom
    if current_comments:
        bottom_comments = current_comments

    return TableComments(key_comments, top_comments, bottom_comments)


def insert_key_with_comments(table: AbstractTable, key: Key, item: Item, comments: TableComments) -> None:
    body = table.value.body
    entry_comments = comments.key_comments.get(key.key, [])
    body.extend((None, comment) for comment in entry_comments)
    body.append((key, item))


def order_keys(
    table: AbstractTable,
    to_pin: Sequence[str] | None = None,
    sort_key: None | Callable[[tuple[str, tuple[Key, Item]]], SupportsDunderLT | SupportsDunderGT] = None,
) -> None:
    comments = store_comments(table)

    body = table.value.body
    entries = {i.key: (i, v) for (i, v) in body if isinstance(i, Key)}
    body.clear()

    for comment in comments.top_comments:
        body.append((None, comment))

    for pin in to_pin or []:  # push pinned to start
        if pin in entries:
            key, value = entries[pin]
            insert_key_with_comments(table, key, value, comments)
            del entries[pin]
    # append the rest
    if sort_key is None:
        for _, (key, item) in entries.items():
            insert_key_with_comments(table, key, item, comments)
    else:
        for _, (key, item) in sorted(entries.items(), key=sort_key):
            insert_key_with_comments(table, key, item, comments)

    for comment in comments.bottom_comments:
        body.append((None, comment))

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
    for entry in body:
        if isinstance(entry, String):
            entries.append(ArrayEntries(entry))
        elif isinstance(entry, Comment):
            (entries[-1].comments if len(entries) else start).append(entry)

    body.clear()
    indent_text = " " * indent
    for entry in start:
        body.append(Whitespace(f"\n{indent_text}"))
        entry.indent(0)
        body.append(entry)
    for entry in sorted(entries, key=key):
        body.append(Whitespace(f"\n{indent_text}"))
        body.append(entry.text)
        body.append(Whitespace(","))
        if entry.comments:
            com = " ".join(i.trivia.comment[1:].strip() for i in entry.comments)
            body.append(Comment(Trivia(comment=f" # {com}", trail="")))
    body.append(Whitespace("\n"))


__all__ = [
    "ArrayEntries",
    "sorted_array",
    "order_keys",
]
