import re

from markcraft.tokens import span as span_token


__all__ = ['Math']


class Math(span_token.SpanToken):
    pattern = re.compile(r'(\${1,2})([^$]+?)\1')
    parse_inner = False
    parse_group = 0
