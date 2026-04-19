import unittest

from markcraft.tokens import block as block_token


class TestDocument(unittest.TestCase):
    def test_store_footnote(self):
        lines = ['[key 1]: value1\n', '[key 2]: value2\n']
        document = block_token.Document(lines)
        self.assertEqual(document.footnotes['key 1'], ('value1', ''))
        self.assertEqual(document.footnotes['key 2'], ('value2', ''))

    def test_auto_splitlines(self):
        lines = "some\ncontinual\nlines\n"
        document = block_token.Document(lines)
        self.assertIsInstance(document.children[0], block_token.Paragraph)
        self.assertEqual(len(document.children), 1)


class TestThematicBreak(unittest.TestCase):
    def test_match(self):
        def test_case(line):
            token = next(iter(block_token.tokenize([line])))
            self.assertIsInstance(token, block_token.ThematicBreak)

        cases = ['---\n', '* * *\n', '_    _    _\n']
        for case in cases:
            test_case(case)


class TestContains(unittest.TestCase):
    def test_contains(self):
        lines = ['# heading\n', '\n', 'paragraph\n', 'with\n', '`code`\n']
        token = block_token.Document(lines)
        self.assertTrue('heading' in token)
        self.assertTrue('code' in token)
        self.assertFalse('foo' in token)


class TestParent(unittest.TestCase):
    def test_parent(self):
        lines = ['# heading\n', '\n', 'paragraph\n']
        token = block_token.Document(lines)
        self.assertEqual(len(token.children), 2)
        self.assertIsNone(token.parent)
        for child in token.children:
            self.assertEqual(child.parent, token)
            for grandchild in child.children:
                self.assertEqual(grandchild.parent, child)
