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


def tokenize_block(iterable, token_types, start_line=1):
    """
    Returns a list of tuples (token_type, read_result, line_number).

    Footnotes are parsed here, but span-level parsing has not
    started yet.
    """
    lines = FileWrapper(iterable, start_line=start_line)
    parse_buffer = ParseBuffer()
    line = lines.peek()
    while line is not None:
        for token_type in token_types:
            if token_type.start(line):
                line_number = lines.line_number() + 1
                result = token_type.read(lines)
                if result is not None:
                    parse_buffer.append((token_type, result, line_number))
                    break
        else:  # unmatched newlines
            next(lines)
            parse_buffer.loose = True
        line = lines.peek()
    return parse_buffer


def make_tokens(parse_buffer):
    """
    Takes a list of tuples (token_type, read_result, line_number),
    applies token_type(read_result), and sets the line_number attribute.

    Footnotes are already parsed before this point,
    and span-level parsing is started here.
    """
    tokens = []
    for token_type, result, line_number in parse_buffer:
        token = token_type(result)
        if token is not None:
            token.line_number = line_number
            tokens.append(token)
    return tokens
