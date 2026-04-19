import unittest

from markcraft.tokens import block as block_token
from markcraft.renderers.markdown import MarkdownRenderer


class TestMarkdownFormatting(unittest.TestCase):
    def test_wordwrap_plain_paragraph(self):
        with MarkdownRenderer() as renderer:
            paragraph = block_token.Paragraph(
                [
                    "A \n",
                    "short   paragraph \n",
                    "   without any \n",
                    "long words \n",
                    "or hard line breaks.\n",
                ]
            )
            renderer.max_line_length = 30
            lines = renderer.render(paragraph)
            assert lines == (
                "A short paragraph without any\n"
                "long words or hard line\n"
                "breaks.\n"
            )
            renderer.max_line_length = 8
            lines = renderer.render(paragraph)
            assert lines == (
                "A short\n"
                "paragraph\n"
                "without\n"
                "any long\n"
                "words or\n"
                "hard\n"
                "line\n"
                "breaks.\n"
            )

    def test_wordwrap_paragraph_with_emphasized_words(self):
        with MarkdownRenderer() as renderer:
            paragraph = block_token.Paragraph(["*emphasized* _nested *emphasis* too_\n"])
            renderer.max_line_length = 1
            lines = renderer.render(paragraph)
            assert lines == ("*emphasized*\n" "_nested\n" "*emphasis*\n" "too_\n")

    def test_wordwrap_paragraph_with_inline_code(self):
        with MarkdownRenderer() as renderer:
            paragraph = block_token.Paragraph(
                ["`inline code` and\n", "`` inline with\n", "line break ``\n"]
            )
            renderer.max_line_length = 1
            lines = renderer.render(paragraph)
            assert lines == (
                "`inline\n"
                "code`\n"
                "and\n"
                "`` inline\n"
                "with\n"
                "line\n"
                "break ``\n"
            )

    def test_wordwrap_paragraph_with_hard_line_breaks(self):
        with MarkdownRenderer() as renderer:
            paragraph = block_token.Paragraph(
                ["A short paragraph  \n", "  without any\\\n", "very long\n", "words.\n"]
            )
            renderer.max_line_length = 80
            lines = renderer.render(paragraph)
            assert lines == ("A short paragraph  \n" "without any\\\n" "very long words.\n")

    def test_wordwrap_paragraph_with_link(self):
        with MarkdownRenderer() as renderer:
            paragraph = block_token.Paragraph(
                [
                    "A paragraph\n",
                    "containing [a link](<link destination with non-breaking spaces> 'which\n",
                    "has a rather long title\n",
                    "spanning multiple lines.')\n",
                ]
            )
            renderer.max_line_length = 1
            lines = renderer.render(paragraph)
            assert lines == (
                "A\n"
                "paragraph\n"
                "containing\n"
                "[a\n"
                "link](<link destination with non-breaking spaces>\n"
                "'which\n"
                "has\n"
                "a\n"
                "rather\n"
                "long\n"
                "title\n"
                "spanning\n"
                "multiple\n"
                "lines.')\n"
            )

    def test_wordwrap_text_in_setext_heading(self):
        with MarkdownRenderer() as renderer:
            document = block_token.Document(
                [
                    "A \n",
                    "setext   heading \n",
                    "   without any \n",
                    "long words \n",
                    "or hard line breaks.\n",
                    "=====\n",
                ]
            )
            renderer.max_line_length = 30
            lines = renderer.render(document)
            assert lines == (
                "A setext heading without any\n"
                "long words or hard line\n"
                "breaks.\n"
                "=====\n"
            )

    def test_wordwrap_text_in_link_reference_definition(self):
        with MarkdownRenderer() as renderer:
            document = block_token.Document(
                [
                    "[This is\n",
                    "  the *link label*.]:<a long, non-breakable link reference> 'title (with parens). new\n",
                    "lines allowed.'\n",
                    "[*]:url  'Another   link      reference\tdefinition'\n",
                ]
            )
            renderer.max_line_length = 30
            lines = renderer.render(document)
            assert lines == (
                "[This is the *link label*.]:\n"
                "<a long, non-breakable link reference>\n"
                "'title (with parens). new\n"
                "lines allowed.'\n"
                "[*]: url 'Another link\n"
                "reference definition'\n"
            )

    def test_wordwrap_paragraph_in_list(self):
        with MarkdownRenderer() as renderer:
            document = block_token.Document(
                [
                    "1. List item\n",
                    "2. A second list item including:\n",
                    "   * Nested list.\n",
                    "     This is a continuation line\n",
                ]
            )
            renderer.max_line_length = 25
            lines = renderer.render(document)
            assert lines == (
                "1. List item\n"
                "2. A second list item\n"
                "   including:\n"
                "   * Nested list. This is\n"
                "     a continuation line\n"
            )

    def test_wordwrap_paragraph_in_block_quote(self):
        with MarkdownRenderer() as renderer:
            document = block_token.Document(
                [
                    "> Devouring Time, blunt thou the lion's paws,\n",
                    "> And make the earth devour her own sweet brood;\n",
                    "> > When Dawn strides out to wake a dewy farm\n",
                    "> > Across green fields and yellow hills of hay\n",
                ]
            )
            renderer.max_line_length = 30
            lines = renderer.render(document)
            assert lines == (
                "> Devouring Time, blunt thou\n"
                "> the lion's paws, And make\n"
                "> the earth devour her own\n"
                "> sweet brood;\n"
                "> > When Dawn strides out to\n"
                "> > wake a dewy farm Across\n"
                "> > green fields and yellow\n"
                "> > hills of hay\n"
            )

    def test_wordwrap_tables(self):
        with MarkdownRenderer(max_line_length=30) as renderer:
            input = [
                "| header |                         x |                 |\n",
                "| ------ | ------------------------: | --------------- |\n",
                "| .      | Performance improvements. | an extra column |\n",
            ]
            document = block_token.Document(input)
            lines = renderer.render(document)
            assert lines == "".join(input)
