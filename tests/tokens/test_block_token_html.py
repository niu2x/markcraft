import unittest

from markcraft.tokens import block as block_token


class TestHtmlBlock(unittest.TestCase):
    def setUp(self):
        block_token.add_token(block_token.HtmlBlock)
        self.addCleanup(block_token.reset_tokens)

    def test_textarea_block_may_contain_blank_lines(self):
        lines = ['<textarea>\n', '\n', '*foo*\n', '\n', '_bar_\n', '\n', '</textarea>\n']
        document = block_token.Document(lines)
        tokens = document.children
        self.assertEqual(1, len(tokens))
        self.assertIsInstance(tokens[0], block_token.HtmlBlock)


class TestLeafBlockTokenContentProperty(unittest.TestCase):
    def setUp(self):
        block_token.add_token(block_token.HtmlBlock)
        self.addCleanup(block_token.reset_tokens)

    def test_code_fence(self):
        lines = ['```\n', 'line 1\n', 'line 2\n', '```\n']
        document = block_token.Document(lines)
        tokens = document.children
        self.assertEqual(1, len(tokens))
        self.assertIsInstance(tokens[0], block_token.CodeFence)
        self.assertEqual('line 1\nline 2\n', tokens[0].children[0].content)
        self.assertEqual('line 1\nline 2\n', tokens[0].content)

    def test_block_code(self):
        lines = ['    line 1\n', '    line 2\n']
        document = block_token.Document(lines)
        tokens = document.children
        self.assertEqual(1, len(tokens))
        self.assertIsInstance(tokens[0], block_token.BlockCode)
        self.assertEqual('line 1\nline 2\n', tokens[0].children[0].content)
        self.assertEqual('line 1\nline 2\n', tokens[0].content)

    def test_html_block(self):
        lines = ['<div>\n', 'text\n' '</div>\n']
        document = block_token.Document(lines)
        tokens = document.children
        self.assertEqual(1, len(tokens))
        self.assertIsInstance(tokens[0], block_token.HtmlBlock)
        self.assertEqual(''.join(lines).strip(), tokens[0].children[0].content)
        self.assertEqual(''.join(lines).strip(), tokens[0].content)
