from __future__ import annotations

"""Parser-oriented namespace for markcraft internals and extensions."""

__all__ = [
    "BlockToken",
    "Document",
    "FileWrapper",
    "ParseBuffer",
    "SpanToken",
    "Token",
    "add_block_token",
    "add_span_token",
    "parse_document",
    "parse_with_renderer",
    "remove_block_token",
    "remove_span_token",
    "reset_block_tokens",
    "reset_span_tokens",
    "tokenize_blocks",
    "tokenize_spans",
]


def __getattr__(name: str):
    if name in {"FileWrapper", "ParseBuffer"}:
        from . import state

        return getattr(state, name)
    if name in {"BlockToken", "Document"}:
        from markcraft.tokens import block

        return getattr(block, name)
    if name == "SpanToken":
        from markcraft.tokens import span

        return span.SpanToken
    if name == "Token":
        from markcraft.tokens import base

        return base.Token
    if name in {"parse_document", "parse_with_renderer"}:
        from .document import parse_document
        from .document import parse_with_renderer

        return parse_document if name == "parse_document" else parse_with_renderer
    if name in {"tokenize_blocks", "tokenize_spans"}:
        from . import tokenizers

        return getattr(tokenizers, name)
    if name in {
        "add_block_token",
        "remove_block_token",
        "reset_block_tokens",
        "add_span_token",
        "remove_span_token",
        "reset_span_tokens",
    }:
        from . import tokens

        return getattr(tokens, name)
    raise AttributeError(name)
