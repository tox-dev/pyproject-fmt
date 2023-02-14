from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

from tomlkit.container import OutOfOrderTableProxy
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


def sort_inline_table(item: tuple[str, Any | Table]) -> str:
    key, value = item
    return f"{key}{'-'.join(value) if isinstance(value, Table) else ''}"


def order_keys(
    table: AbstractTable | OutOfOrderTableProxy,
    to_pin: Sequence[str] | None = None,
    sort_key: None | Callable[[tuple[str, tuple[Key, Item]]], SupportsDunderLT | SupportsDunderGT] = None,
) -> None:
    if isinstance(table, OutOfOrderTableProxy):
        return  # pragma: no cover
    body = table.value.body
    entries: dict[str, list[Any]] = defaultdict(list)
    for key, value in body:
        if isinstance(key, Key):
            entries[key.key].append((key, value))
    body.clear()

    for pin in to_pin or []:  # push pinned to start
        if pin in entries:
            body.extend(sorted(entries[pin], key=sort_inline_table))  # type: ignore
            del entries[pin]
    # append the rest
    if sort_key is None:
        for elements in entries.values():
            body.extend(elements)  # pragma: no cover
    else:
        for _, elements in sorted(entries.items(), key=sort_inline_table):
            body.extend(elements)


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


def ensure_newline_at_end(body: Table) -> None:
    content = body
    while content.value.body and isinstance(content.value.body[-1][1], Table):
        content = content.value.body[-1][1]
    whitespace = Whitespace("\n")
    insert_body = content.value.body
    if insert_body and isinstance(insert_body[-1][1], Whitespace):
        insert_body[-1] = insert_body[-1][0], whitespace
    else:
        insert_body.append((None, whitespace))


__all__ = [
    "ArrayEntries",
    "sorted_array",
    "order_keys",
    "ensure_newline_at_end",
]
