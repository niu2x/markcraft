from __future__ import annotations

import re

from markcraft.parser import block_tokenizer as tokenizer

from .base import BlockToken


class List(BlockToken):
    repr_attributes = BlockToken.repr_attributes + ("loose", "start")
    pattern = re.compile(r" {0,3}(?:\d{0,9}[.)]|[+\-*])(?:[ \t]*$|[ \t]+)")

    def __init__(self, matches):
        from markcraft.tokens import block

        self.children = [block.ListItem(*match) for match in matches]
        self.loose = any(item.loose for item in self.children)
        leader = self.children[0].leader
        self.start = None
        if len(leader) != 1:
            self.start = int(leader[:-1])

    @classmethod
    def start(cls, line):
        return cls.pattern.match(line)

    @classmethod
    def check_interrupts_paragraph(cls, lines):
        from markcraft.tokens import block

        marker_tuple = block.ListItem.parse_marker(lines.peek())
        if marker_tuple is not None:
            _, _, leader, content = marker_tuple
            if content.strip() != "":
                return not leader[0].isdigit() or leader in ["1.", "1)"]
        return False

    @classmethod
    def read(cls, lines):
        from markcraft.tokens import block

        leader = None
        next_marker = None
        matches = []
        while True:
            anchor = lines.get_pos()
            output, next_marker = block.ListItem.read(lines, next_marker)
            item_leader = output[3]
            if leader is None:
                leader = item_leader
            elif not cls.same_marker_type(leader, item_leader):
                lines.set_pos(anchor)
                break
            matches.append(output)
            if next_marker is None:
                break

        if matches:
            last_parse_buffer = matches[-1][0]
            last_parse_buffer.loose = len(last_parse_buffer) > 1 and last_parse_buffer.loose

        return matches

    @staticmethod
    def same_marker_type(leader, other):
        if len(leader) == 1:
            return leader == other
        return leader[:-1].isdigit() and other[:-1].isdigit() and leader[-1] == other[-1]


class ListItem(BlockToken):
    repr_attributes = BlockToken.repr_attributes + ("leader", "indentation", "prepend", "loose")
    pattern = re.compile(r"( {0,3})(\d{0,9}[.)]|[+\-*])($|\s+)")
    continuation_pattern = re.compile(r"([ \t]*)(\S.*\n|\n)")

    def __init__(
        self,
        parse_buffer,
        indentation,
        prepend,
        leader,
        line_number=None,
        span=None,
        offset_span=None,
    ):
        self.line_number = line_number
        self.span = span
        self.offset_span = offset_span
        self.leader = leader
        self.indentation = indentation
        self.prepend = prepend
        self.children = tokenizer.make_tokens(parse_buffer)
        self.loose = parse_buffer.loose

    @classmethod
    def parse_continuation(cls, line, prepend):
        match_obj = cls.continuation_pattern.match(line)
        if match_obj is None:
            return None
        if match_obj.group(2) == "\n":
            return "\n"
        expanded_spaces = match_obj.group(1).expandtabs(4)
        if len(expanded_spaces) >= prepend:
            return expanded_spaces[prepend:] + match_obj.group(2)
        return None

    @classmethod
    def parse_marker(cls, line):
        match_obj = cls.pattern.match(line)
        if match_obj is None:
            return None
        indentation = len(match_obj.group(1))
        prepend = len(match_obj.group(0).expandtabs(4))
        leader = match_obj.group(2)
        content = line[match_obj.end(0) :]
        n_spaces = prepend - match_obj.end(2)
        if n_spaces > 4:
            prepend -= n_spaces - 1
            content = " " * (n_spaces - 1) + content
        return indentation, prepend, leader, content

    @classmethod
    def marker_prefix_len(cls, line):
        match_obj = cls.pattern.match(line)
        if match_obj is None:
            return 0
        prepend = len(match_obj.group(0).expandtabs(4))
        n_spaces = prepend - match_obj.end(2)
        if n_spaces > 4:
            return match_obj.end(0) - (n_spaces - 1)
        return match_obj.end(0)

    @classmethod
    def continuation_prefix_len(cls, line, prepend):
        match_obj = cls.continuation_pattern.match(line)
        if match_obj is None:
            return 0
        if match_obj.group(2) == "\n":
            return len(line) - 1

        consumed_columns = 0
        consumed_chars = 0
        for ch in match_obj.group(1):
            width = 4 if ch == "\t" else 1
            if consumed_columns + width > prepend:
                break
            consumed_columns += width
            consumed_chars += 1
        return consumed_chars

    @classmethod
    def read(cls, lines, prev_marker=None):
        from markcraft.tokens import block

        next_marker = None
        line_buffer = []
        line_start_offsets = []
        line_start_columns = []
        line = next(lines)
        start_index = lines.get_pos()
        start_line = lines.line_number()
        start_offset = lines.line_start_offset(start_index)
        next_line = lines.peek()
        indentation, prepend, leader, content = prev_marker if prev_marker else cls.parse_marker(line)
        if content.strip() == "":
            prepend = indentation + len(leader) + 1
            blanks = 1
            while next_line is not None and next_line.strip() == "":
                blanks += 1
                next(lines)
                next_line = lines.peek()
            if blanks > 1:
                parse_buffer = tokenizer.ParseBuffer()
                parse_buffer.loose = True
                next_marker = cls.parse_marker(next_line) if next_line is not None else None
                end_index = lines.get_pos()
                end_line = lines.line_number()
                end_column = lines.line_end_column(end_index)
                end_offset = lines.line_end_offset(end_index)
                return (
                    (
                        parse_buffer,
                        indentation,
                        prepend,
                        leader,
                        start_line,
                        ((start_line, 1), (end_line, end_column)),
                        (start_offset, end_offset),
                    ),
                    next_marker,
                )
        else:
            line_buffer.append(content)
            marker_prefix = cls.marker_prefix_len(line)
            line_start_offsets.append(start_offset + marker_prefix)
            line_start_columns.append(marker_prefix + 1)

        breaking_tokens = [
            t
            for t in block.get_token_types()
            if hasattr(t, "check_interrupts_paragraph") and t != block.List
        ]
        newline_count = 0
        while True:
            if next_line is None:
                if newline_count:
                    lines.backstep()
                    del line_buffer[-newline_count:]
                    del line_start_offsets[-newline_count:]
                    del line_start_columns[-newline_count:]
                break

            continuation = cls.parse_continuation(next_line, prepend)
            if not continuation:
                if any(token_type.check_interrupts_paragraph(lines) for token_type in breaking_tokens):
                    if newline_count:
                        lines.backstep()
                        del line_buffer[-newline_count:]
                        del line_start_offsets[-newline_count:]
                        del line_start_columns[-newline_count:]
                    break
                marker_info = cls.parse_marker(next_line)
                if marker_info is not None:
                    next_marker = marker_info
                    break
                if newline_count:
                    lines.backstep()
                    del line_buffer[-newline_count:]
                    del line_start_offsets[-newline_count:]
                    del line_start_columns[-newline_count:]
                    break
                continuation = next_line

            next_index = lines.get_pos() + 1
            continuation_prefix = 0 if continuation == next_line else cls.continuation_prefix_len(next_line, prepend)
            line_buffer.append(continuation)
            line_start_offsets.append(lines.line_start_offset(next_index) + continuation_prefix)
            line_start_columns.append(continuation_prefix + 1)
            newline_count = newline_count + 1 if continuation == "\n" else 0
            next(lines)
            next_line = lines.peek()

        parse_buffer = tokenizer.tokenize_block(
            line_buffer,
            block.get_token_types(),
            start_line=start_line,
            start_offset=start_offset,
            line_start_offsets=line_start_offsets,
            line_start_columns=line_start_columns,
        )
        end_index = lines.get_pos()
        end_line = lines.line_number()
        end_column = lines.line_end_column(end_index)
        end_offset = lines.line_end_offset(end_index)
        return (
            (
                parse_buffer,
                indentation,
                prepend,
                leader,
                start_line,
                ((start_line, 1), (end_line, end_column)),
                (start_offset, end_offset),
            ),
            next_marker,
        )
