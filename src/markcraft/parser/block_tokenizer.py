from __future__ import annotations

"""Block-level tokenizer implementation."""

from markcraft.parser.state import FileWrapper, ParseBuffer


def tokenize(iterable, token_types):
    """
    Searches for token_types in iterable.

    Args:
        iterable (list): user input lines to be parsed.
        token_types (list): a list of block-level token constructors.

    Returns:
        block-level token instances.
    """
    return make_tokens(tokenize_block(iterable, token_types))


def tokenize_block(
    iterable,
    token_types,
    start_line=1,
    start_offset=0,
    line_start_offsets: list[int] | None = None,
    line_start_columns: list[int] | None = None,
):
    """
    Returns tuples:
    (token_type, read_result, line_number, span, offset_span).

    Footnotes are parsed here, but span-level parsing has not
    started yet.
    """
    lines = FileWrapper(
        iterable,
        start_line=start_line,
        start_offset=start_offset,
        line_start_offsets=line_start_offsets,
        line_start_columns=line_start_columns,
    )
    parse_buffer = ParseBuffer()
    line = lines.peek()
    while line is not None:
        for token_type in token_types:
            if token_type.start(line):
                start_index = lines.get_pos() + 1
                line_number = lines.line_number() + 1
                result = token_type.read(lines)
                if result is not None:
                    end_index = max(start_index, lines.get_pos())
                    end_line = max(line_number, lines.line_number())
                    end_column = lines.line_end_column(end_index)
                    start_offset_value = lines.line_start_offset(start_index)
                    end_offset_value = lines.line_end_offset(end_index)
                    start_column = lines.line_start_column(start_index)
                    parse_buffer.append(
                        (
                            token_type,
                            result,
                            line_number,
                            ((line_number, start_column), (end_line, end_column)),
                            (start_offset_value, end_offset_value),
                        )
                    )
                    break
        else:  # unmatched newlines
            next(lines)
            parse_buffer.loose = True
        line = lines.peek()
    return parse_buffer


def make_tokens(parse_buffer):
    """
    Takes tuples (token_type, read_result, line_number, span, offset_span),
    applies token_type(read_result), and sets line_number/span/offset_span.

    Footnotes are already parsed before this point,
    and span-level parsing is started here.
    """
    tokens = []
    for token_type, result, line_number, span, offset_span in parse_buffer:
        token = token_type(result)
        if token is not None:
            token.line_number = line_number
            token.span = span
            token.offset_span = offset_span
            tokens.append(token)
    return tokens
