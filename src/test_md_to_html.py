import unittest

from extract_md import markdown_to_html_node


class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_single_paragraph(self):
        md = "This is a paragraph."
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><p>This is a paragraph.</p></div>"
        )

    def test_multiline_paragraph_becomes_single_p_tag(self):
        md = "This is line one.\nThis is line two."
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><p>This is line one. This is line two.</p></div>"
        )

    def test_paragraph_with_bold_italic_and_code(self):
        md = "This has **bold**, _italic_, and `code`."
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><p>This has <b>bold</b>, <i>italic</i>, and <code>code</code>.</p></div>"
        )

    def test_paragraph_with_link(self):
        md = "This has a [link](https://example.com)."
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            '<div><p>This has a <a href="https://example.com">link</a>.</p></div>'
        )

    def test_paragraph_with_image(self):
        md = "This has an ![alt text](https://example.com/image.png)"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            '<div><p>This has an <img src="https://example.com/image.png" alt="alt text"></p></div>'
        )

    def test_heading(self):
        md = "## This is a heading"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><h2>This is a heading</h2></div>"
        )

    def test_quote_block(self):
        md = ">This is a quote"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><blockquote>This is a quote</blockquote></div>"
        )

    def test_multiline_quote_block(self):
        md = ">This is line one\n>This is line two"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><blockquote>This is line one\nThis is line two</blockquote></div>"
        )

    def test_unordered_list(self):
        md = "- First item\n- Second item\n- Third item"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><ul><li>First item</li><li>Second item</li><li>Third item</li></ul></div>"
        )

    def test_ordered_list(self):
        md = "1. First item\n2. Second item\n3. Third item"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><ol><li>First item</li><li>Second item</li><li>Third item</li></ol></div>"
        )

    def test_code_block(self):
        md = "```python\nprint('hello')\n```"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><pre><code>print('hello')</code></pre></div>"
        )

    def test_multiple_blocks(self):
        md = "# Heading\n\nThis is a paragraph.\n\n- One\n- Two"
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><h1>Heading</h1><p>This is a paragraph.</p><ul><li>One</li><li>Two</li></ul></div>"
        )

    def test_multiple_paragraphs(self):
        md = "First paragraph.\nStill first paragraph.\n\nSecond paragraph."
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><p>First paragraph. Still first paragraph.</p><p>Second paragraph.</p></div>"
        )


if __name__ == "__main__":
    unittest.main()
