"""Built-in block-level token classes."""

from __future__ import annotations

from contextvars import ContextVar
from typing import Iterable, Sequence

from markcraft.parser import block_tokenizer as tokenizer

from .base import BlockToken
from .code_blocks import BlockCode, CodeFence
from .document import Document
from .extras import Footnote, HTMLBlock, HtmlBlock, ThematicBreak
from .headings import Heading, SetextHeading
from .lists import List, ListItem
from .quote_paragraph import Paragraph, Quote
from .tables import Table, TableCell, TableRow

__all__ = [
    "BlockCode",
    "Heading",
    "Quote",
    "CodeFence",
    "ThematicBreak",
    "List",
    "Table",
    "Footnote",
    "Paragraph",
]


_active_token_types: ContextVar[Sequence[type] | None] = ContextVar(
    "markcraft_block_token_types",
    default=None,
)


def get_token_types() -> Sequence[type]:
    active = _active_token_types.get()
    return active if active is not None else _token_types


def activate_token_types(token_types: Sequence[type]):
    return _active_token_types.set(tuple(token_types))


def deactivate_token_types(token):
    _active_token_types.reset(token)


def tokenize(lines, token_types: Iterable[type] | None = None):
    return tokenizer.tokenize(lines, tuple(token_types) if token_types is not None else get_token_types())


def add_token(token_cls, position=0):
    _token_types.insert(position, token_cls)


def remove_token(token_cls):
    _token_types.remove(token_cls)


def reset_tokens():
    global _token_types
    _token_types = [globals()[cls_name] for cls_name in __all__]


for _cls in (
    BlockToken,
    Document,
    Heading,
    SetextHeading,
    Quote,
    Paragraph,
    BlockCode,
    CodeFence,
    List,
    ListItem,
    Table,
    TableRow,
    TableCell,
    Footnote,
    ThematicBreak,
    HtmlBlock,
):
    _cls.__module__ = __name__

_token_types = []
reset_tokens()
