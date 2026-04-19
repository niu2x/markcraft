import unittest

from markcraft.tokens import block as block_token, span as span_token
from markcraft.tokens.block import Document
from markcraft.renderers.markdown import MarkdownRenderer


class TestMarkdownRenderer(unittest.TestCase):
    @staticmethod
    def roundtrip(input, **rendererArgs):
        """Parses the given markdown input and renders it back to markdown again."""
        with MarkdownRenderer(**rendererArgs) as renderer:
            return renderer.render(Document(input))

    def test_empty_document(self):
        input = []
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_paragraphs_and_blank_lines(self):
        input = [
            "Paragraph 1. Single line. Followed by two white-space-only lines.\n",
            "\n",
            "\n",
            "Paragraph 2. Two\n",
            "lines, no final line break.",
        ]
        output = self.roundtrip(input)
        # note: a line break is always added at the end of a paragraph.
        self.assertEqual(output, "".join(input) + "\n")

    def test_line_breaks(self):
        input = [
            "soft line break\n",
            "hard line break (backslash)\\\n",
            "another hard line break (double spaces)  \n",
            "yet another hard line break    \n",
            "that's all.\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_emphasized_and_strong(self):
        input = ["*emphasized* __strong__ _**emphasized and strong**_\n"]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_strikethrough(self):
        input = ["~~strikethrough~~\n"]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_escaped_chars(self):
        input = ["\\*escaped, not emphasized\\*\n"]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_html_span(self):
        input = ["so <p>hear ye</p><h1>\n"]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_code_span(self):
        input = [
            "a) `code span` b) ``trailing space, double apostrophes `` c) ` leading and trailing space `\n"
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_code_span_with_embedded_line_breaks(self):
        input = [
            "a `multi-line\n",
            "code\n",
            "span`.\n"
        ]
        output = self.roundtrip(input)
        expected = [
            "a `multi-line code span`.\n"
        ]
        self.assertEqual(output, "".join(expected))

    def test_images_and_links(self):
        input = [
            "[a link](#url (title))\n",
            "[another link](<url-in-angle-brackets> '*emphasized\n",
            "title*')\n",
            '![an \\[*image*\\], escapes and emphasis](#url "title")\n',
            "<http://auto.link>\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_multiline_fragment(self):
        input = [
            "[a link](<url-in-angle-brackets> '*emphasized\n",
            "title\n",
            "spanning\n",
            "many\n",
            "lines*')\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_thematic_break(self):
        input = [
            " **  * ** * ** * **\n",
            "followed by a paragraph of text\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_atx_headings(self):
        input = [
            "## atx *heading* ##\n",
            "# another atx heading, without trailing hashes\n",
            "###\n",
            "^ empty atx heading\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_setext_headings(self):
        input = [
            "*setext*\n",
            "heading!\n",
            "===============\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_numbered_list(self):
        input = [
            "  22) *emphasized list item*\n",
            "  96) \n",
            " 128) here begins a nested list.\n",
            "       + apples\n",
            "       + bananas\n",
        ]
        output = self.roundtrip(input)
        expected = [
            "  22) *emphasized list item*\n",
            "  96) \n",
            " 128) here begins a nested list.\n",
            "       + apples\n",
            "       + bananas\n",
        ]
        self.assertEqual(output, "".join(expected))

    def test_bulleted_list(self):
        input = [
            "* **test case**:\n",
            "  testing a link as the first item on a continuation line\n",
            "  [links must be indented][properly].\n",
            "\n",
            "[properly]: uri\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_list_item_margin_indentation_preserved(self):
        # 0 to 4 spaces of indentation from the margin
        input = [
            "- 0 space: ok.\n",
            "  subsequent line.\n",
            " - 1 space: ok.\n",
            "   subsequent line.\n",
            "  - 2 spaces: ok.\n",
            "    subsequent line.\n",
            "   - 3 spaces: ok.\n",
            "     subsequent line.\n",
            "    - 4 spaces: in the paragraph of the above list item.\n",
            "      subsequent line.\n",
        ]
        output = self.roundtrip(input)
        expected = [
            "- 0 space: ok.\n",
            "  subsequent line.\n",
            " - 1 space: ok.\n",
            "   subsequent line.\n",
            "  - 2 spaces: ok.\n",
            "    subsequent line.\n",
            # note: we still always normalize the indentation of all list item lines:
            "   - 3 spaces: ok.\n",
            "     subsequent line.\n",
            "     - 4 spaces: in the paragraph of the above list item.\n",
            "     subsequent line.\n",
        ]
        self.assertEqual(output, "".join(expected))

    def test_list_item_margin_indentation_normalized(self):
        # 0 to 4 spaces of indentation from the margin
        input = [
            "- 0 space: ok.\n",
            "  subsequent line.\n",
            " - 1 space: ok.\n",
            "   subsequent line.\n",
            "  - 2 spaces: ok.\n",
            "    subsequent line.\n",
            "   - 3 spaces: ok.\n",
            "     subsequent line.\n",
            "    - 4 spaces: in the paragraph of the above list item.\n",
            "      subsequent line.\n",
        ]
        output = self.roundtrip(input, normalize_whitespace=True)
        expected = [
            "- 0 space: ok.\n",
            "  subsequent line.\n",
            "- 1 space: ok.\n",
            "  subsequent line.\n",
            "- 2 spaces: ok.\n",
            "  subsequent line.\n",
            "- 3 spaces: ok.\n",
            "  subsequent line.\n",
            "  - 4 spaces: in the paragraph of the above list item.\n",
            "  subsequent line.\n",
        ]
        self.assertEqual(output, "".join(expected))

    def test_list_item_indentation_after_leader_preserved(self):
        # leaders followed by 1 to 5 spaces
        input = [
            "- 1 space: ok.\n",
            "  subsequent line.\n",
            "-  2 spaces: ok.\n",
            "   subsequent line.\n",
            "-   3 spaces: ok.\n",
            "    subsequent line.\n",
            "-    4 spaces: ok.\n",
            "     subsequent line.\n",
            "-     5 spaces: list item starting with indented code.\n",
            "  subsequent line.\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_list_item_indentation_after_leader_normalized(self):
        # leaders followed by 1 to 5 spaces
        input = [
            "- 1 space: ok.\n",
            "  subsequent line.\n",
            "-  2 spaces: ok.\n",
            "   subsequent line.\n",
            "-   3 spaces: ok.\n",
            "    subsequent line.\n",
            "-    4 spaces: ok.\n",
            "     subsequent line.\n",
            "-     5 spaces: list item starting with indented code.\n",
            "  subsequent line.\n",
        ]
        output = self.roundtrip(input, normalize_whitespace=True)
        expected = [
            "- 1 space: ok.\n",
            "  subsequent line.\n",
            "- 2 spaces: ok.\n",
            "  subsequent line.\n",
            "- 3 spaces: ok.\n",
            "  subsequent line.\n",
            "- 4 spaces: ok.\n",
            "  subsequent line.\n",
            "-     5 spaces: list item starting with indented code.\n",
            "  subsequent line.\n",
        ]
        self.assertEqual(output, "".join(expected))

    def test_code_blocks(self):
        input = [
            "    this is an indented code block\n",
            "      on two lines \n",
            "    with some extra whitespace here and there, to be preserved  \n",
            "      just as it is.\n",
            "```\n",
            "now for a fenced code block \n",
            "  where indentation is also preserved. as are the double spaces at the end of this line:  \n",
            "```\n",
            "  ~~~this is an info string: behold the fenced code block with tildes!\n",
            "  *tildes are great*\n",
            "  ~~~\n",
            "1. a list item with an embedded\n",
            "\n",
            "       indented code block.\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_blank_lines_following_code_block(self):
        input = [
            "    code block\n",
            "\n",
            "paragraph.\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_html_block(self):
        input = [
            "<h1>some text <img src='https://cdn.rawgit.com/' align='right'></h1>\n",
            "<br>\n",
            "\n",
            "+ <h1>html block embedded in list <img src='https://cdn.rawgit.com/' align='right'></h1>\n",
            "  <br>\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_block_quote(self):
        input = [
            "> a block quote\n",
            "> > and a nested block quote\n",
            "> 1. > and finally, a list with a nested block quote\n",
            ">    > which continues on a second line.\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_link_reference_definition(self):
        input = [
            "[label]: https://domain.com\n",
            "\n",
            "paragraph [with a link][label-2], etc, etc.\n",
            "and [a *second* link][label] as well\n",
            "shortcut [label] & collapsed [label][]\n",
            "\n",
            "[label-2]: <https://libraries.io/> 'title\n",
            "with line break'\n",
            "[label-not-referred-to]: https://foo (title)\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_table(self):
        input = [
            "| Emoji | Description               |\n",
            "| :---: | ------------------------- |\n",
            "|   📚   | Update documentation.     |\n",
            "|   🐎   | Performance improvements. |\n",
            "etc, etc\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_table_with_varying_column_counts(self):
        input = [
            "   |   header | x |  \n",
            "   | --- | ---: |   \n",
            "   | . | Performance improvements. | an extra column |   \n",
            "etc, etc\n",
        ]
        output = self.roundtrip(input)
        expected = [
            "| header |                         x |                 |\n",
            "| ------ | ------------------------: | --------------- |\n",
            "| .      | Performance improvements. | an extra column |\n",
            "etc, etc\n",
        ]
        self.assertEqual(output, "".join(expected))

    def test_table_with_narrow_column(self):
        input = [
            "| xyz | ? |\n",
            "| --- | - |\n",
            "| a   | p |\n",
            "| b   | q |\n",
        ]
        output = self.roundtrip(input)
        expected = [
            "| xyz | ?   |\n",
            "| --- | --- |\n",
            "| a   | p   |\n",
            "| b   | q   |\n",
        ]
        self.assertEqual(output, "".join(expected))

    def test_two_tables_separated_by_single_blank_line(self):
        input = [
            "| Name  | Score |\n",
            "| ----- | ----- |\n",
            "| Alice | 95    |\n",
            "| Bob   | 88    |\n",
            "\n",
            "| Item  | Qty |\n",
            "| ----- | --- |\n",
            "| Pen   | 2   |\n",
            "| Paper | 5   |\n",
        ]
        output = self.roundtrip(input)
        self.assertEqual(output, "".join(input))

    def test_direct_rendering_of_block_token(self):
        input = [
            "Line 1\n",
            "Line 2\n",
        ]
        paragraph = block_token.Paragraph(input)
        with MarkdownRenderer() as renderer:
            lines = renderer.render(paragraph)
        assert lines == "".join(input)

    def test_direct_rendering_of_span_token(self):
        input = "some text"
        raw_text = span_token.RawText(input)
        with MarkdownRenderer() as renderer:
            lines = renderer.render(raw_text)
        assert lines == input + "\n"

    def test_rendering_rejects_mismatched_document_parser_config(self):
        document = Document(["paragraph\n"])
        with MarkdownRenderer() as renderer:
            with self.assertRaisesRegex(RuntimeError, r"renderer\.parse"):
                renderer.render(document)
