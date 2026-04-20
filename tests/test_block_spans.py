import unittest

import markcraft.tokens.block as block_token


class TestBlockSpans(unittest.TestCase):
    def test_spans_are_attached_to_block_tokens(self):
        document = block_token.Document(
            [
                "# H\n",
                "\n",
                "para1\n",
                "para2\n",
                "\n",
                "- item1\n",
                "- item2\n",
                "\n",
                "| a | b |\n",
                "| - | - |\n",
                "| c | d |\n",
            ]
        )

        heading, paragraph, list_token, table = document.children

        self.assertEqual(document.span, ((1, 1), (11, 11)))
        self.assertEqual(document.offset_span, (0, 65))
        self.assertEqual(heading.span, ((1, 1), (1, 5)))
        self.assertEqual(heading.offset_span, (0, 4))
        self.assertEqual(paragraph.span, ((3, 1), (4, 7)))
        self.assertEqual(paragraph.offset_span, (5, 17))
        self.assertEqual(list_token.span, ((6, 1), (7, 9)))
        self.assertEqual(list_token.offset_span, (18, 34))
        self.assertEqual(list_token.children[0].span, ((6, 1), (6, 9)))
        self.assertEqual(list_token.children[0].offset_span, (18, 26))
        self.assertEqual(list_token.children[1].span, ((7, 1), (7, 9)))
        self.assertEqual(list_token.children[1].offset_span, (26, 34))
        self.assertEqual(table.span, ((9, 1), (11, 11)))
        self.assertEqual(table.offset_span, (35, 65))
        self.assertEqual(table.header.span, ((9, 1), (9, 11)))
        self.assertEqual(table.header.offset_span, (35, 45))
        self.assertEqual(table.children[0].span, ((11, 1), (11, 11)))
        self.assertEqual(table.children[0].offset_span, (55, 65))
        self.assertEqual(table.header.children[0].span, ((9, 1), (9, 11)))
        self.assertEqual(table.header.children[0].offset_span, (35, 45))

        self._assert_all_block_tokens_have_span(document)

    def _assert_all_block_tokens_have_span(self, token):
        self.assertTrue(hasattr(token, "span"))
        self.assertEqual(len(token.span), 2)
        start, end = token.span
        self.assertEqual(len(start), 2)
        self.assertEqual(len(end), 2)
        self.assertGreaterEqual(end[0], start[0])
        self.assertTrue(hasattr(token, "offset_span"))
        self.assertEqual(len(token.offset_span), 2)
        self.assertGreaterEqual(token.offset_span[1], token.offset_span[0])

        if isinstance(token, block_token.Table):
            self._assert_all_block_tokens_have_span(token.header)

        if token.children is None:
            return
        for child in token.children:
            if isinstance(child, block_token.BlockToken):
                self._assert_all_block_tokens_have_span(child)

    def test_nested_quote_content_spans_use_original_source_positions(self):
        document = block_token.Document(["> quoted\n"])

        quote = document.children[0]
        paragraph = quote.children[0]

        self.assertEqual(quote.span, ((1, 1), (1, 10)))
        self.assertEqual(quote.offset_span, (0, 9))
        self.assertEqual(paragraph.span, ((1, 3), (1, 10)))
        self.assertEqual(paragraph.offset_span, (2, 9))

    def test_nested_list_content_spans_use_original_source_positions(self):
        document = block_token.Document(["- item\n"])

        list_token = document.children[0]
        item = list_token.children[0]
        paragraph = item.children[0]

        self.assertEqual(list_token.span, ((1, 1), (1, 8)))
        self.assertEqual(list_token.offset_span, (0, 7))
        self.assertEqual(item.span, ((1, 1), (1, 8)))
        self.assertEqual(item.offset_span, (0, 7))
        self.assertEqual(paragraph.span, ((1, 3), (1, 8)))
        self.assertEqual(paragraph.offset_span, (2, 7))
