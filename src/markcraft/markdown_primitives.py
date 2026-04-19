from __future__ import annotations

import re

from markcraft.tokens import block, span


class BlankLine(block.BlockToken):
    """Blank line token. Represents a single blank line."""

    pattern = re.compile(r"\s*\n$")

    def __init__(self, _):
        self.children = []

    @classmethod
    def start(cls, line):
        return cls.pattern.match(line)

    @classmethod
    def read(cls, lines):
        return [next(lines)]


class LinkReferenceDefinition(span.SpanToken):
    """Link reference definition. ([label]: dest "title")."""

    repr_attributes = ("label", "dest", "title")

    def __init__(self, match):
        self.label, self.dest, self.title, self.dest_type, self.title_delimiter = match


class LinkReferenceDefinitionBlock(block.Footnote):
    """A sequence of link reference definitions kept in the AST."""

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj.__init__(*args, **kwargs)
        return obj

    def __init__(self, matches):
        self.children = [LinkReferenceDefinition(match) for match in matches]


class Fragment:
    """Markdown fragment used by ``MarkdownRenderer`` span rendering."""

    def __init__(self, text: str, **extras):
        self.text = text
        self.__dict__.update(extras)


__all__ = [
    "BlankLine",
    "Fragment",
    "LinkReferenceDefinition",
    "LinkReferenceDefinitionBlock",
]
