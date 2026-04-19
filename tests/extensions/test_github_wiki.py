from unittest import TestCase, mock
from markcraft import Document
from markcraft.tokens import base as token
from markcraft.tokens import span as span_token
from markcraft.tokens.span import tokenize_inner
from markcraft.extensions.github_wiki import GithubWiki, GithubWikiRenderer


class TestGithubWiki(TestCase):
    def setUp(self):
        token._root_node = Document([])
        self.renderer = GithubWikiRenderer()
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def test_parse(self):
        MockRawText = mock.Mock()
        token_types = list(span_token.get_token_types())
        RawText = token_types[-1]
        token_types[-1] = MockRawText
        token_handle = span_token.activate_token_types(token_types)
        try:
            tokens = tokenize_inner('text with [[wiki | target]]')
            token = tokens[1]
            self.assertIsInstance(token, GithubWiki)
            self.assertEqual(token.target, 'target')
            MockRawText.assert_has_calls([mock.call('text with '), mock.call('wiki')])
        finally:
            span_token.deactivate_token_types(token_handle)
            token_types[-1] = RawText

    def test_render(self):
        token = next(iter(tokenize_inner('[[wiki|target]]')))
        output = '<a href="target">wiki</a>'
        self.assertEqual(self.renderer.render(token), output)
