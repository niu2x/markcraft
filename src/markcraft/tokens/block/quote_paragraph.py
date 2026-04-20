from __future__ import annotations

import re

from markcraft.parser import block_tokenizer as tokenizer
from markcraft.tokens import span as span_token

from .base import BlockToken


class Quote(BlockToken):
    def __init__(self, parse_buffer):
        self.children = tokenizer.make_tokens(parse_buffer)

    @staticmethod
    def start(line):
        stripped = line.lstrip(" ")
        if len(line) - len(stripped) > 3:
            return False
        return stripped.startswith(">")

    @classmethod
    def check_interrupts_paragraph(cls, lines):
        return cls.start(lines.peek())

    @classmethod
    def read(cls, lines):
        from markcraft.tokens import block

        original_line = next(lines)
        start_index = lines.get_pos()
        line, first_prefix = cls.strip_quote_prefix(original_line)
        line_buffer = [line]
        start_line = lines.line_number()
        start_offset = lines.line_start_offset(start_index)
        line_start_offsets = [start_offset + first_prefix]
        line_start_columns = [first_prefix + 1]

        in_code_fence = block.CodeFence.start(line)
        in_block_code = block.BlockCode.start(line)
        blank_line = line.strip() == ""

        next_line = lines.peek()
        breaking_tokens = [
            t
            for t in block.get_token_types()
            if hasattr(t, "check_interrupts_paragraph") and t != block.Quote
        ]
        while (
            next_line is not None
            and next_line.strip() != ""
            and not any(token_type.check_interrupts_paragraph(lines) for token_type in breaking_tokens)
        ):
            stripped = cls.convert_leading_tabs(next_line.lstrip())
            prepend = 0
            if stripped[0] == ">":
                next_index = lines.get_pos() + 1
                stripped, prepend = cls.strip_quote_prefix(next_line)
                in_code_fence = block.CodeFence.start(stripped)
                in_block_code = block.BlockCode.start(stripped)
                blank_line = stripped.strip() == ""
                line_buffer.append(stripped)
                line_start_offsets.append(lines.line_start_offset(next_index) + prepend)
                line_start_columns.append(prepend + 1)
            elif in_code_fence or in_block_code or blank_line:
                break
            else:
                next_index = lines.get_pos() + 1
                line_buffer.append(next_line)
                line_start_offsets.append(lines.line_start_offset(next_index))
                line_start_columns.append(1)
            next(lines)
            next_line = lines.peek()

        block.Paragraph.parse_setext = False
        parse_buffer = tokenizer.tokenize_block(
            line_buffer,
            block.get_token_types(),
            start_line=start_line,
            start_offset=start_offset,
            line_start_offsets=line_start_offsets,
            line_start_columns=line_start_columns,
        )
        block.Paragraph.parse_setext = True
        return parse_buffer

    @classmethod
    def strip_quote_prefix(cls, line):
        leading = len(line) - len(line.lstrip())
        stripped = cls.convert_leading_tabs(line.lstrip())
        if not stripped.startswith(">"):
            return stripped, leading

        prefix = leading + 1
        content = stripped[1:]
        if content.startswith(" "):
            prefix += 1
            content = content[1:]
        return content, prefix

    @staticmethod
    def convert_leading_tabs(string):
        string = string.replace(">\t", "   ", 1)
        count = 0
        for i, c in enumerate(string):
            if c == "\t":
                count += 4
            elif c == " ":
                count += 1
            else:
                break
        if i == 0:
            return string
        return ">" + " " * count + string[i:]


class Paragraph(BlockToken):
    setext_pattern = re.compile(r" {0,3}(=|-)+ *$")
    parse_setext = True

    def __new__(cls, lines):
        if not isinstance(lines, list):
            return lines
        return super().__new__(cls)

    def __init__(self, lines):
        content = "".join([line.lstrip() for line in lines]).strip()
        super().__init__(content, span_token.tokenize_inner)

    @staticmethod
    def start(line):
        return line.strip() != ""

    @classmethod
    def read(cls, lines):
        from markcraft.tokens import block

        line_buffer = [next(lines)]
        next_line = lines.peek()
        breaking_tokens = [
            t
            for t in block.get_token_types()
            if hasattr(t, "check_interrupts_paragraph") and t != block.ThematicBreak
        ]
        while next_line is not None and next_line.strip() != "":
            if any(token_type.check_interrupts_paragraph(lines) for token_type in breaking_tokens):
                break
            if cls.parse_setext and cls.is_setext_heading(next_line):
                line_buffer.append(next(lines))
                return block.SetextHeading(line_buffer)
            if block.ThematicBreak.check_interrupts_paragraph(lines):
                break
            line_buffer.append(next(lines))
            next_line = lines.peek()
        return line_buffer

    @classmethod
    def is_setext_heading(cls, line):
        return cls.setext_pattern.match(line)
