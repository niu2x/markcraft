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

        line = cls.convert_leading_tabs(next(lines).lstrip()).split(">", 1)[1]
        if len(line) > 0 and line[0] == " ":
            line = line[1:]
        line_buffer = [line]
        start_line = lines.line_number()

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
                prepend += 1
                if stripped[1] == " ":
                    prepend += 1
                stripped = stripped[prepend:]
                in_code_fence = block.CodeFence.start(stripped)
                in_block_code = block.BlockCode.start(stripped)
                blank_line = stripped.strip() == ""
                line_buffer.append(stripped)
            elif in_code_fence or in_block_code or blank_line:
                break
            else:
                line_buffer.append(next_line)
            next(lines)
            next_line = lines.peek()

        block.Paragraph.parse_setext = False
        parse_buffer = tokenizer.tokenize_block(
            line_buffer, block.get_token_types(), start_line=start_line
        )
        block.Paragraph.parse_setext = True
        return parse_buffer

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
