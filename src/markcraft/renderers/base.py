"""
Base class for renderers.
"""

import re
from typing import Iterable

from markcraft.tokens import block, span


class BaseRenderer(object):
    """
    Base class for renderers.

    All renderers should ...
    *   ... define all render functions specified in self.render_map;
    *   ... be a context manager (by inheriting __enter__ and __exit__);

    Custom renderers could ...
    *   ... add additional tokens into the parsing process by passing custom
        tokens to super().__init__();
    *   ... add additional render functions by appending to self.render_map;

    Usage:
        Suppose SomeRenderer inherits BaseRenderer, and fin is the input file.
        The syntax looks something like this:

            >>> from markcraft import Document
            >>> from some_renderer import SomeRenderer
            >>> with SomeRenderer() as renderer:
            ...     rendered = renderer.render(Document(fin))

        See markcraft.renderers.html for an implementation example.

    Naming conventions:
        *   The keys of self.render_map should exactly match the class
            name of tokens;
        *   Render function names should be of form: "render_" + the
            "snake-case" form of token's class name.

    Attributes:
        render_map (dict): maps tokens to their corresponding render functions.
        _extras (list): a list of custom tokens to be added to the
                        parsing process.
    """
    _parse_name = re.compile(r"([A-Z][a-z]+|[A-Z]+(?![a-z]))")

    def __init__(self, *extras, **kwargs):
        self.render_map = {
            'Strong':         self.render_strong,
            'Emphasis':       self.render_emphasis,
            'InlineCode':     self.render_inline_code,
            'RawText':        self.render_raw_text,
            'Strikethrough':  self.render_strikethrough,
            'Image':          self.render_image,
            'Link':           self.render_link,
            'AutoLink':       self.render_auto_link,
            'EscapeSequence': self.render_escape_sequence,
            'Heading':        self.render_heading,
            'SetextHeading':  self.render_heading,
            'Quote':          self.render_quote,
            'Paragraph':      self.render_paragraph,
            'CodeFence':      self.render_block_code,
            'BlockCode':      self.render_block_code,
            'List':           self.render_list,
            'ListItem':       self.render_list_item,
            'Table':          self.render_table,
            'TableRow':       self.render_table_row,
            'TableCell':      self.render_table_cell,
            'ThematicBreak':  self.render_thematic_break,
            'LineBreak':      self.render_line_break,
            'Document':       self.render_document,
        }
        self._extras = extras
        self._block_token_types = list(block._token_types)
        self._span_token_types = list(span._token_types)
        self._block_token_var_token = None
        self._span_token_var_token = None

        for token in extras:
            if issubclass(token, span.SpanToken):
                self._span_token_types.insert(1, token)
            else:
                self._block_token_types.insert(0, token)
            render_func = getattr(self, self._cls_to_func(token.__name__))
            self.render_map[token.__name__] = render_func

        self.footnotes = {}

    def render(self, token):
        """
        Grabs the class name from input token and finds its corresponding
        render function.

        Basically a janky way to do polymorphism.

        Arguments:
            token: whose __class__.__name__ is in self.render_map.
        """
        self._ensure_document_parser_config(token)
        return self.render_map[token.__class__.__name__](token)

    def parse(self, lines: str | Iterable[str]) -> block.Document:
        return block.Document(
            lines,
            block_token_types=self._block_token_types,
            span_token_types=self._span_token_types,
        )

    def _ensure_document_parser_config(self, token) -> None:
        if isinstance(token, block.Document):
            token.ensure_parsed(self._block_token_types, self._span_token_types)

    def add_block_token(self, token_cls, position: int = 0):
        self._block_token_types.insert(position, token_cls)

    def remove_block_token(self, token_cls):
        if token_cls in self._block_token_types:
            self._block_token_types.remove(token_cls)

    def add_span_token(self, token_cls, position: int = 1):
        self._span_token_types.insert(position, token_cls)

    def remove_span_token(self, token_cls):
        if token_cls in self._span_token_types:
            self._span_token_types.remove(token_cls)

    def render_inner(self, token) -> str:
        """
        Recursively renders child tokens. Joins the rendered
        strings with no space in between.

        If newlines / spaces are needed between tokens, add them
        in their respective templates, or override this function
        in the renderer subclass, so that whitespace won't seem to
        appear magically for anyone reading your program.

        Arguments:
            token: a branch node who has children attribute.
        """
        return ''.join(map(self.render, token.children))

    def __enter__(self):
        """
        Make renderer classes into context managers.
        """
        self._block_token_var_token = block.activate_token_types(self._block_token_types)
        self._span_token_var_token = span.activate_token_types(self._span_token_types)
        return self

    def __exit__(self, exception_type, exception_val, traceback):
        """
        Make renderer classes into context managers.

        Reset parser token context overrides.
        """
        if self._block_token_var_token is not None:
            block.deactivate_token_types(self._block_token_var_token)
            self._block_token_var_token = None
        if self._span_token_var_token is not None:
            span.deactivate_token_types(self._span_token_var_token)
            self._span_token_var_token = None

    @classmethod
    def _cls_to_func(cls, cls_name):
        snake = '_'.join(map(str.lower, cls._parse_name.findall(cls_name)))
        return 'render_{}'.format(snake)

    @staticmethod
    def _tokens_from_module(module):
        """
        Helper method; takes a module and returns a list of all token classes
        specified in module.__all__. Useful when custom tokens are defined in a
        separate module.
        """
        return [getattr(module, name) for name in module.__all__]

    def render_raw_text(self, token) -> str:
        """
        Default render method for RawText. Simply return token.content.
        """
        return token.content

    def render_strong(self, token: span.Strong) -> str:
        return self.render_inner(token)

    def render_emphasis(self, token: span.Emphasis) -> str:
        return self.render_inner(token)

    def render_inline_code(self, token: span.InlineCode) -> str:
        return self.render_inner(token)

    def render_strikethrough(self, token: span.Strikethrough) -> str:
        return self.render_inner(token)

    def render_image(self, token: span.Image) -> str:
        return self.render_inner(token)

    def render_link(self, token: span.Link) -> str:
        return self.render_inner(token)

    def render_auto_link(self, token: span.AutoLink) -> str:
        return self.render_inner(token)

    def render_escape_sequence(self, token: span.EscapeSequence) -> str:
        return self.render_inner(token)

    def render_line_break(self, token: span.LineBreak) -> str:
        return self.render_inner(token)

    def render_heading(self, token: block.Heading) -> str:
        return self.render_inner(token)

    def render_quote(self, token: block.Quote) -> str:
        return self.render_inner(token)

    def render_paragraph(self, token: block.Paragraph) -> str:
        return self.render_inner(token)

    def render_block_code(self, token: block.BlockCode) -> str:
        return self.render_inner(token)

    def render_list(self, token: block.List) -> str:
        return self.render_inner(token)

    def render_list_item(self, token: block.ListItem) -> str:
        return self.render_inner(token)

    def render_table(self, token: block.Table) -> str:
        return self.render_inner(token)

    def render_table_cell(self, token: block.TableCell) -> str:
        return self.render_inner(token)

    def render_table_row(self, token: block.TableRow) -> str:
        return self.render_inner(token)

    def render_thematic_break(self, token: block.ThematicBreak) -> str:
        return self.render_inner(token)

    def render_document(self, token: block.Document) -> str:
        return self.render_inner(token)


# Safe characters for URL quoting. These are basically all the URI
# reserved characters as per [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986#section-2.2).
# Plus we add the percent character (%) to avoid double-escaping.
URI_SAFE_CHARACTERS = ":/?#[]@!$&'()*+,;=%"
