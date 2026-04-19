from __future__ import annotations

import re

from markcraft.tokens import base as token
from markcraft.tokens import span as span_token
from markcraft.tokens.core import (
    follows,
    is_control_char,
    normalize_label,
    shift_whitespace,
    whitespace,
)

from .base import BlockToken


class Footnote(BlockToken):
    def __new__(cls, _):
        return None

    @classmethod
    def start(cls, line):
        return line.lstrip().startswith("[")

    @classmethod
    def read(cls, lines):
        line_buffer = []
        next_line = lines.peek()
        while next_line is not None and next_line.strip() != "":
            line_buffer.append(next(lines))
            next_line = lines.peek()
        string = "".join(line_buffer)
        offset = 0
        matches = []
        while offset < len(string) - 1:
            match_info = cls.match_reference(string, offset)
            if match_info is None:
                lines._index -= string[offset:].count("\n")
                break
            offset, match = match_info
            matches.append(match)
        cls.append_footnotes(matches, token._root_node)
        return matches or None

    @classmethod
    def match_reference(cls, string, offset):
        match_info = cls.match_link_label(string, offset)
        if not match_info:
            return None
        _, label_end, label = match_info
        if not follows(string, label_end - 1, ":"):
            return None
        dest_start = shift_whitespace(string, label_end + 1)
        if dest_start == len(string):
            return None
        match_info = cls.match_link_dest(string, dest_start)
        if not match_info:
            return None
        _, dest_end, dest = match_info
        dest_type = "angle_uri" if string[dest_start] == "<" else "uri"
        title_start = shift_whitespace(string, dest_end)
        if title_start == dest_end and title_start < len(string):
            return None
        match_info = cls.match_link_title(string, title_start)
        if not match_info:
            eol_pos = string[dest_end:title_start].find("\n")
            if eol_pos >= 0:
                return dest_end + eol_pos + 1, (label, dest, "", dest_type, None)
            return None
        _, title_end, title = match_info
        line_end = title_end
        while line_end < len(string):
            if string[line_end] == "\n":
                title_delimiter = string[title_start] if title_start < title_end else None
                return line_end + 1, (label, dest, title, dest_type, title_delimiter)
            if string[line_end] in whitespace:
                line_end += 1
            else:
                break
        eol_pos = string[dest_end:title_start].find("\n")
        if eol_pos >= 0:
            return dest_end + eol_pos + 1, (label, dest, "", dest_type, None)
        return None

    @classmethod
    def match_link_label(cls, string, offset):
        start = -1
        escaped = False
        for i, c in enumerate(string[offset:], start=offset):
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == "[":
                if start == -1:
                    start = i
                else:
                    return None
            elif c == "]":
                label = string[start + 1 : i]
                if label.strip() != "":
                    return start, i + 1, label
                return None
            if start == -1 and not (c == " " and i - offset < 3):
                return None
        return None

    @classmethod
    def match_link_dest(cls, string, offset):
        if string[offset] == "<":
            escaped = False
            for i, c in enumerate(string[offset + 1 :], start=offset + 1):
                if c == "\\" and not escaped:
                    escaped = True
                elif c == "\n" or (c == "<" and not escaped):
                    return None
                elif c == ">" and not escaped:
                    return offset, i + 1, string[offset + 1 : i]
                elif escaped:
                    escaped = False
            return None
        escaped = False
        count = 0
        for i, c in enumerate(string[offset:], start=offset):
            if c == "\\" and not escaped:
                escaped = True
            elif c in whitespace:
                break
            elif not escaped:
                if c == "(":
                    count += 1
                elif c == ")":
                    count -= 1
            elif is_control_char(c):
                return None
            elif escaped:
                escaped = False
        if count != 0:
            return None
        return offset, i, string[offset:i]

    @classmethod
    def match_link_title(cls, string, offset):
        if offset == len(string):
            return None
        if string[offset] == '"':
            closing = '"'
        elif string[offset] == "'":
            closing = "'"
        elif string[offset] == "(":
            closing = ")"
        else:
            return None
        escaped = False
        for i, c in enumerate(string[offset + 1 :], start=offset + 1):
            if c == "\\" and not escaped:
                escaped = True
            elif c == closing and not escaped:
                return offset, i + 1, string[offset + 1 : i]
            elif escaped:
                escaped = False
        return None

    @staticmethod
    def append_footnotes(matches, root):
        for key, dest, title, *_ in matches:
            key = normalize_label(key)
            dest = span_token.EscapeSequence.strip(dest.strip())
            title = span_token.EscapeSequence.strip(title)
            if key not in root.footnotes:
                root.footnotes[key] = dest, title


class ThematicBreak(BlockToken):
    pattern = re.compile(r" {0,3}(?:([-_*])\s*?)(?:\1\s*?){2,}$")

    def __init__(self, lines):
        self.line = lines[0].strip("\n")

    @classmethod
    def start(cls, line):
        return cls.pattern.match(line)

    @classmethod
    def check_interrupts_paragraph(cls, lines):
        return cls.start(lines.peek())

    @staticmethod
    def read(lines):
        return [next(lines)]


class HtmlBlock(BlockToken):
    _end_cond = None
    multiblock = re.compile(r"<(pre|script|style|textarea)[ >\n]")
    predefined = re.compile(r"<\/?(.+?)(?:\/?>|[ \n])")
    custom_tag = re.compile(
        r"(?:" + "|".join((span_token._open_tag, span_token._closing_tag)) + r")\s*$"
    )

    def __init__(self, lines):
        self.children = (span_token.RawText("".join(lines).rstrip("\n")),)

    @property
    def content(self):
        return self.children[0].content

    @classmethod
    def start(cls, line):
        stripped = line.lstrip()
        if len(line) - len(stripped) >= 4:
            return False
        match_obj = cls.multiblock.match(stripped)
        if match_obj is not None:
            cls._end_cond = "</{}>".format(match_obj.group(1).casefold())
            return 1
        if stripped.startswith("<!--"):
            cls._end_cond = "-->"
            return 2
        if stripped.startswith("<?"):
            cls._end_cond = "?>"
            return 3
        if stripped.startswith("<!") and stripped[2].isupper():
            cls._end_cond = ">"
            return 4
        if stripped.startswith("<![CDATA["):
            cls._end_cond = "]]>"
            return 5
        match_obj = cls.predefined.match(stripped)
        if match_obj is not None and match_obj.group(1).casefold() in span_token._tags:
            cls._end_cond = None
            return 6
        match_obj = cls.custom_tag.match(stripped)
        if match_obj is not None:
            cls._end_cond = None
            return 7
        return False

    @classmethod
    def check_interrupts_paragraph(cls, lines):
        html_block = cls.start(lines.peek())
        return html_block and html_block != 7

    @classmethod
    def read(cls, lines):
        line_buffer = []
        for line in lines:
            line_buffer.append(line)
            if cls._end_cond is not None:
                if cls._end_cond in line.casefold():
                    break
            elif line.strip() == "":
                line_buffer.pop()
                lines.backstep()
                break
        return line_buffer


HTMLBlock = HtmlBlock
