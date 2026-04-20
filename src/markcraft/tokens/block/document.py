from __future__ import annotations

from typing import Iterable, Sequence

from markcraft.tokens import base as token
from markcraft.tokens import span

from .base import BlockToken


class Document(BlockToken):
    def __init__(
        self,
        lines: str | Iterable[str],
        *,
        block_token_types: Sequence[type] | None = None,
        span_token_types: Sequence[type] | None = None,
    ):
        if isinstance(lines, str):
            lines = lines.splitlines(keepends=True)
        normalized_lines = [line if line.endswith("\n") else f"{line}\n" for line in lines]
        self._source_lines = tuple(normalized_lines)
        self._parse_signature = None
        self.footnotes = {}
        self.line_number = 1
        end_line = len(self._source_lines) if self._source_lines else 1
        end_col = len(self._source_lines[-1]) + 1 if self._source_lines else 1
        end_offset = sum(len(line) for line in self._source_lines)
        self.span = ((1, 1), (end_line, end_col))
        self.offset_span = (0, end_offset)

        from markcraft.tokens import block

        active_block_types = tuple(block_token_types) if block_token_types is not None else tuple(block.get_token_types())
        active_span_types = tuple(span_token_types) if span_token_types is not None else tuple(span.get_token_types())
        self._parse(active_block_types, active_span_types)

    def ensure_parsed(
        self,
        block_token_types: Sequence[type],
        span_token_types: Sequence[type],
    ) -> None:
        signature = (tuple(block_token_types), tuple(span_token_types))
        if self._parse_signature != signature:
            raise RuntimeError(
                "Document parser configuration does not match current renderer. "
                "Build documents with renderer.parse(...) or markcraft.parse(..., renderer)."
            )

    def _parse(
        self,
        block_token_types: Sequence[type],
        span_token_types: Sequence[type],
    ) -> None:
        from markcraft.tokens import block

        token._root_node = self
        block_ctx_token = block.activate_token_types(block_token_types)
        span_ctx_token = span.activate_token_types(span_token_types)
        try:
            self.children = block.tokenize(self._source_lines, token_types=block_token_types)
            self._parse_signature = (tuple(block_token_types), tuple(span_token_types))
        finally:
            span.deactivate_token_types(span_ctx_token)
            block.deactivate_token_types(block_ctx_token)
            token._root_node = None
