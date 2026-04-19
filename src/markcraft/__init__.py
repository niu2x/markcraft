from __future__ import annotations

"""Top-level API for markcraft."""

__version__ = "1.0.1"
__all__ = [
    "Document",
    "render",
    "parse",
    "parser",
    "renderers",
    "tokens",
]

from typing import Callable, Iterable

from markcraft.tokens.block import Document
from markcraft.renderers.base import BaseRenderer
from markcraft.renderers.html import HtmlRenderer
from markcraft.parser.document import parse_document, parse_with_renderer
from markcraft import tokens


def parse(
    iterable: str | Iterable[str],
    renderer: BaseRenderer | Callable[..., BaseRenderer] | None = None,
) -> Document:
    """Parse markdown into a ``Document`` tree with an explicit parser entrypoint."""
    if renderer is None:
        return parse_document(iterable)
    return parse_with_renderer(iterable, renderer)


def render(
    iterable: str | Iterable[str],
    renderer: BaseRenderer | Callable[..., BaseRenderer] = HtmlRenderer,
):
    """
    Converts markdown input to the output supported by the given renderer.
    If no renderer is supplied, ``HtmlRenderer`` is used.

    Note that extra token types supported by the given renderer
    are automatically (and temporarily) added to the parsing process.
    """
    if isinstance(renderer, BaseRenderer):
        with renderer as r:
            return r.render(r.parse(iterable))
    with renderer() as r:
        return r.render(r.parse(iterable))
