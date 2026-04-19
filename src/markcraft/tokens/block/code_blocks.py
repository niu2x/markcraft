from __future__ import annotations

import re

from markcraft.tokens import span as span_token

from .base import BlockToken


class BlockCode(BlockToken):
    repr_attributes = BlockToken.repr_attributes + ("language",)

    def __init__(self, lines):
        self.language = ""
        self.children = (span_token.RawText("".join(lines).strip("\n") + "\n"),)

    @property
    def content(self):
        return self.children[0].content

    @staticmethod
    def start(line):
        return line.replace("\t", "    ", 1).startswith("    ")

    @classmethod
    def read(cls, lines):
        line_buffer = []
        trailing_blanks = 0
        for line in lines:
            if line.strip() == "":
                line_buffer.append(line.lstrip(" ") if len(line) < 5 else line[4:])
                trailing_blanks = trailing_blanks + 1 if line == "\n" else 0
                continue
            if not line.replace("\t", "    ", 1).startswith("    "):
                lines.backstep()
                break
            line_buffer.append(cls.strip(line))
            trailing_blanks = 0
        for _ in range(trailing_blanks):
            line_buffer.pop()
            lines.backstep()
        return line_buffer

    @staticmethod
    def strip(string):
        count = 0
        for i, c in enumerate(string):
            if c == "\t":
                return string[i + 1 :]
            if c == " ":
                count += 1
            else:
                break
            if count == 4:
                return string[i + 1 :]
        return string


class CodeFence(BlockToken):
    repr_attributes = BlockToken.repr_attributes + ("language",)
    pattern = re.compile(r"( {0,3})(`{3,}|~{3,})( *(\S*)[^\n]*)")
    _open_info = None

    def __init__(self, match):
        lines, open_info = match
        self.indentation = open_info[0]
        self.delimiter = open_info[1]
        self.info_string = open_info[2]
        self.language = span_token.EscapeSequence.strip(open_info[3])
        self.children = (span_token.RawText("".join(lines)),)

    @property
    def content(self):
        return self.children[0].content

    @classmethod
    def start(cls, line):
        match_obj = cls.pattern.match(line)
        if not match_obj:
            return False
        prepend, leader, info_string, lang = match_obj.groups()
        if leader[0] == "`" and "`" in info_string:
            return False
        cls._open_info = len(prepend), leader, info_string, lang
        return True

    @classmethod
    def check_interrupts_paragraph(cls, lines):
        return cls.start(lines.peek())

    @classmethod
    def read(cls, lines):
        next(lines)
        line_buffer = []
        for line in lines:
            stripped_line = line.lstrip(" ")
            diff = len(line) - len(stripped_line)
            if (
                stripped_line.startswith(cls._open_info[1])
                and len(stripped_line.split(maxsplit=1)) == 1
                and diff < 4
            ):
                break
            if diff > cls._open_info[0]:
                stripped_line = " " * (diff - cls._open_info[0]) + stripped_line
            line_buffer.append(stripped_line)
        return line_buffer, cls._open_info
