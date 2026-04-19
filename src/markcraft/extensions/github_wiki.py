"""
GitHub Wiki support for markcraft.
"""

import re

from markcraft.tokens.span import SpanToken
from markcraft.renderers.html import HtmlRenderer


__all__ = ["GithubWiki", "GithubWikiRenderer"]


class GithubWiki(SpanToken):
    pattern = re.compile(r"\[\[ *(.+?) *\| *(.+?) *\]\]")

    def __init__(self, match):
        self.target = match.group(2)


class GithubWikiRenderer(HtmlRenderer):
    def __init__(self, **kwargs):
        """
        Args:
            **kwargs: additional parameters to be passed to the ancestor's
                      constructor.
        """
        super().__init__(GithubWiki, **kwargs)

    def render_github_wiki(self, token):
        template = '<a href="{target}">{inner}</a>'
        target = self.escape_url(token.target)
        inner = self.render_inner(token)
        return template.format(target=target, inner=inner)
