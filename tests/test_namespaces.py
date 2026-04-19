from __future__ import annotations

from unittest import TestCase

import markcraft
from markcraft.tokens.block import Document
from markcraft.parser import parse_document, parse_with_renderer, tokenize_spans
from markcraft.renderers import AstRenderer, HtmlRenderer, LaTeXRenderer, MarkdownRenderer


class TestNamespaces(TestCase):
    def test_parser_parse_document(self):
        doc = parse_document("# title\n")
        self.assertIsInstance(doc, Document)

    def test_top_level_parse(self):
        doc = markcraft.parse("# title\n")
        self.assertIsInstance(doc, Document)

    def test_top_level_render(self):
        self.assertEqual(markcraft.render("# title\n"), "<h1>title</h1>\n")

    def test_parser_parse_with_renderer(self):
        doc = parse_with_renderer("# title\n", MarkdownRenderer)
        self.assertIsInstance(doc, Document)

    def test_parser_tokenize_spans(self):
        tokens = tokenize_spans("hello")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].content, "hello")

    def test_renderer_namespace_exports(self):
        self.assertTrue(issubclass(HtmlRenderer, object))
        self.assertTrue(issubclass(LaTeXRenderer, object))
        self.assertTrue(issubclass(AstRenderer, object))
        self.assertTrue(issubclass(MarkdownRenderer, object))
