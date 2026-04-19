from __future__ import annotations

from typing import Iterable

from markcraft.tokens.block import tokenize as _tokenize_blocks
from markcraft.tokens.span import tokenize_inner as _tokenize_spans


def tokenize_blocks(lines: Iterable[str]):
    """Tokenize block-level markdown input."""
    return _tokenize_blocks(lines)


def tokenize_spans(content: str):
    """Tokenize span-level markdown input."""
    return _tokenize_spans(content)
