from __future__ import annotations

from markcraft.tokens import base as token


class BlockToken(token.Token):
    """Base class for block-level tokens."""

    repr_attributes = ("line_number",)

    def __init__(self, lines, tokenize_func):
        self.children = tokenize_func(lines)

    def __contains__(self, text):
        return any(text in child for child in self.children)

    @staticmethod
    def read(lines):
        line_buffer = [next(lines)]
        for line in lines:
            if line == "\n":
                break
            line_buffer.append(line)
        return line_buffer
