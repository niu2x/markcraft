from __future__ import annotations

from markcraft.tokens import block, span


def add_block_token(token_cls, position: int = 0) -> None:
    """Insert a block token class into the parsing pipeline."""
    block.add_token(token_cls, position=position)


def remove_block_token(token_cls) -> None:
    """Remove a block token class from the parsing pipeline."""
    block.remove_token(token_cls)


def reset_block_tokens() -> None:
    """Reset block token classes to built-in defaults."""
    block.reset_tokens()


def add_span_token(token_cls, position: int = 1) -> None:
    """Insert a span token class into the parsing pipeline."""
    span.add_token(token_cls, position=position)


def remove_span_token(token_cls) -> None:
    """Remove a span token class from the parsing pipeline."""
    span.remove_token(token_cls)


def reset_span_tokens() -> None:
    """Reset span token classes to built-in defaults."""
    span.reset_tokens()
