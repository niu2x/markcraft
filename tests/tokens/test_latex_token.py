import unittest
from markcraft.tokens.span import tokenize_inner
from markcraft.tokens.latex import Math
from markcraft.renderers.latex import LaTeXRenderer


class TestLaTeXToken(unittest.TestCase):
    def setUp(self):
        self.renderer = LaTeXRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def test_span(self):
        token = next(iter(tokenize_inner('$ 1 + 2 = 3 $')))
        self.assertIsInstance(token, Math)
        self.assertEqual(token.content, '$ 1 + 2 = 3 $')
