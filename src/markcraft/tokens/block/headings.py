from __future__ import annotations

import re

from markcraft.tokens import span as span_token

from .base import BlockToken


class Heading(BlockToken):
    """ATX heading token."""

    repr_attributes = BlockToken.repr_attributes + ("level",)
    pattern = re.compile(r" {0,3}(#{1,6})(?:\n|\s+?(.*?)(\n|\s+?#+\s*?$))")
    level = 0
    content = ""

    def __init__(self, match):
        self.level, content, self.closing_sequence = match
        super().__init__(content, span_token.tokenize_inner)

    @classmethod
    def start(cls, line):
        match_obj = cls.pattern.match(line)
        if match_obj is None:
            return False
        cls.level = len(match_obj.group(1))
        cls.content = (match_obj.group(2) or "").strip()
        if set(cls.content) == {"#"}:
            cls.content = ""
        cls.closing_sequence = (match_obj.group(3) or "").strip()
        return True

    @classmethod
    def check_interrupts_paragraph(cls, lines):
        return cls.start(lines.peek())

    @classmethod
    def read(cls, lines):
        next(lines)
        return cls.level, cls.content, cls.closing_sequence


class SetextHeading(BlockToken):
    """Setext heading token."""

    repr_attributes = BlockToken.repr_attributes + ("level",)

    def __init__(self, lines):
        self.underline = lines.pop().rstrip()
        self.level = 1 if self.underline.endswith("=") else 2
        content = "\n".join([line.strip() for line in lines])
        super().__init__(content, span_token.tokenize_inner)

    @classmethod
    def start(cls, line):
        raise NotImplementedError()

    @classmethod
    def read(cls, lines):
        raise NotImplementedError()
