from __future__ import annotations

from typing import Callable, Iterable, Sequence

from markcraft.tokens.block import Document
from markcraft.renderers.base import BaseRenderer


def parse_document(
    lines: str | Iterable[str],
    *,
    block_token_types: Sequence[type] | None = None,
    span_token_types: Sequence[type] | None = None,
) -> Document:
    """Parse markdown content into a ``Document`` token tree."""
    return Document(
        lines,
        block_token_types=block_token_types,
        span_token_types=span_token_types,
    )


def parse_with_renderer(
    lines: str | Iterable[str],
    renderer: BaseRenderer | Callable[..., BaseRenderer],
) -> Document:
    """Parse markdown content using a renderer-specific token configuration."""
    if isinstance(renderer, BaseRenderer):
        return renderer.parse(lines)
    with renderer() as active_renderer:
        return active_renderer.parse(lines)
