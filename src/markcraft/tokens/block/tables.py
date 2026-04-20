from __future__ import annotations

import re
from itertools import zip_longest

from markcraft.tokens import span as span_token

from .base import BlockToken


class Table(BlockToken):
    repr_attributes = BlockToken.repr_attributes + ("column_align",)
    interrupt_paragraph = True

    _column_align = r":?-+:?"
    column_align_pattern = re.compile(_column_align)
    delimiter_row_pattern = re.compile(
        r"\s*\|?\s*" + _column_align + r"\s*(\|\s*" + _column_align + r"\s*)*\|?\s*"
    )

    def __init__(self, match):
        from markcraft.tokens import block

        lines, start_line, start_offset = match
        row_offsets = []
        cursor = start_offset
        for line in lines:
            row_offsets.append(cursor)
            cursor += len(line)
        if "-" in lines[1]:
            self.column_align = [self.parse_align(column) for column in self.split_delimiter(lines[1])]
            self.header = block.TableRow(lines[0], self.column_align, start_line)
            if self.header is not None:
                self.header.span = ((start_line, 1), (start_line, len(lines[0]) + 1))
                self.header.offset_span = (row_offsets[0], row_offsets[0] + len(lines[0]))
                if isinstance(self.header, BlockToken):
                    for cell in self.header.children:
                        if cell is not None:
                            cell.span = self.header.span
                            cell.offset_span = self.header.offset_span
            self.children = [
                block.TableRow(line, self.column_align, start_line + offset)
                for offset, line in enumerate(lines[2:], start=2)
            ]
            for offset, line in enumerate(lines[2:], start=2):
                row = self.children[offset - 2]
                if row is not None:
                    row.span = ((start_line + offset, 1), (start_line + offset, len(line) + 1))
                    row.offset_span = (row_offsets[offset], row_offsets[offset] + len(line))
                    if isinstance(row, BlockToken):
                        for cell in row.children:
                            if cell is not None:
                                cell.span = row.span
                                cell.offset_span = row.offset_span
        else:
            self.column_align = [None]
            self.children = [
                block.TableRow(line, line_number=start_line + offset)
                for offset, line in enumerate(lines)
            ]
            for offset, line in enumerate(lines):
                row = self.children[offset]
                if row is not None:
                    row.span = ((start_line + offset, 1), (start_line + offset, len(line) + 1))
                    row.offset_span = (row_offsets[offset], row_offsets[offset] + len(line))
                    if isinstance(row, BlockToken):
                        for cell in row.children:
                            if cell is not None:
                                cell.span = row.span
                                cell.offset_span = row.offset_span

    @classmethod
    def split_delimiter(cls, delimiter_row):
        return cls.column_align_pattern.findall(delimiter_row)

    @staticmethod
    def parse_align(column):
        return (0 if column[0] == ":" else 1) if column[-1] == ":" else None

    @staticmethod
    def start(line):
        return "|" in line

    @classmethod
    def check_interrupts_paragraph(cls, lines):
        if not cls.interrupt_paragraph or not cls.start(lines.peek()):
            return False
        return cls.read(lines, check_only=True)

    @classmethod
    def read(cls, lines, check_only=False):
        anchor = lines.get_pos()
        header_row = next(lines)
        start_line = lines.line_number()
        start_offset = lines.line_start_offset(lines.get_pos())
        delimiter_row = next(lines, None)
        if delimiter_row is None or not cls.delimiter_row_pattern.fullmatch(delimiter_row):
            lines.set_pos(anchor)
            return None
        if check_only:
            lines.set_pos(anchor)
            return True
        line_buffer = [header_row, delimiter_row]
        while lines.peek() is not None and "|" in lines.peek():
            line_buffer.append(next(lines))
        return line_buffer, start_line, start_offset


class TableRow(BlockToken):
    repr_attributes = BlockToken.repr_attributes + ("row_align",)
    split_pattern = re.compile(r"(?<!\\)\|")
    escaped_pipe_pattern = re.compile(r"(?<!\\)(\\\\)*\\\|")

    def __init__(self, line, row_align=None, line_number=None, span=None, offset_span=None):
        from markcraft.tokens import block

        self.row_align = row_align or [None]
        self.line_number = line_number
        if span is not None:
            self.span = span
        elif line_number is not None:
            self.span = ((line_number, 1), (line_number, len(line) + 1))
        else:
            self.span = None
        self.offset_span = offset_span
        cells = filter(None, self.split_pattern.split(line.strip()))
        self.children = []
        for cell, align in zip_longest(cells, self.row_align):
            table_cell = block.TableCell(
                self.escaped_pipe_pattern.sub("\\1|", cell.strip()) if cell else "",
                align,
                line_number,
            )
            if table_cell is not None:
                table_cell.span = self.span
                table_cell.offset_span = self.offset_span
            self.children.append(table_cell)


class TableCell(BlockToken):
    repr_attributes = BlockToken.repr_attributes + ("align",)

    def __init__(self, content, align=None, line_number=None, span=None, offset_span=None):
        self.align = align
        self.line_number = line_number
        if span is not None:
            self.span = span
        elif line_number is not None:
            self.span = ((line_number, 1), (line_number, 1))
        else:
            self.span = None
        self.offset_span = offset_span
        super().__init__(content, span_token.tokenize_inner)
