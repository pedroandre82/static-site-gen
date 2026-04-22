import unittest
from extract_md import extract_markdown_images, extract_markdown_links, \
    split_nodes_delimiter, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks
from textnode import TextNode, TextType

class TestSplitNodesDelimiter(unittest.TestCase):
    def test_split_code_delimiter(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)

        actual = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]

        self.assertEqual(actual, expected)

    def test_split_bold_delimiter(self):
        node = TextNode("This has **bold** text", TextType.TEXT)

        actual = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]

        self.assertEqual(actual, expected)

    def test_split_italic_delimiter(self):
        node = TextNode("This has _italic_ text", TextType.TEXT)

        actual = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]

        self.assertEqual(actual, expected)

    def test_no_delimiter_returns_same_node(self):
        node = TextNode("Just plain text", TextType.TEXT)

        actual = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [TextNode("Just plain text", TextType.TEXT)]

        self.assertEqual(actual, expected)

    def test_non_text_nodes_are_unchanged(self):
        node = TextNode("bold", TextType.BOLD)

        actual = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [TextNode("bold", TextType.BOLD)]

        self.assertEqual(actual, expected)

    def test_multiple_input_nodes(self):
        nodes = [
            TextNode("Text with `code` here", TextType.TEXT),
            TextNode("already bold", TextType.BOLD),
        ]

        actual = split_nodes_delimiter(nodes, "`", TextType.CODE)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" here", TextType.TEXT),
            TextNode("already bold", TextType.BOLD),
        ]

        self.assertEqual(actual, expected)

    def test_raises_error_on_missing_closing_delimiter(self):
        node = TextNode("This has `broken code", TextType.TEXT)

        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_delimiter_at_start_and_end(self):
        node = TextNode("`code`", TextType.TEXT)

        actual = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [TextNode("code", TextType.CODE)]

        self.assertEqual(actual, expected)

    def test_two_delimited_sections_in_one_node(self):
        node = TextNode("a `code` and `more` text", TextType.TEXT)

        actual = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("a ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("more", TextType.CODE),
            TextNode(" text", TextType.TEXT),
        ]

        self.assertEqual(actual, expected)


class TestMarkdownExtractors(unittest.TestCase):

    # --- Tests for Images ---
    def test_extract_markdown_images(self):
        text = "This is an ![image](https://i.imgur.com/zhy2o.png) and ![another](https://i.imgur.com/fjr99.png)"
        expected = [("image", "https://i.imgur.com/zhy2o.png"), ("another", "https://i.imgur.com/fjr99.png")]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_extract_images_no_matches(self):
        text = "This text has no images, only [a link](https://google.com)"
        self.assertEqual(extract_markdown_images(text), [])

    # --- Tests for Links ---
    def test_extract_markdown_links(self):
        text = "Check out [Google](https://www.google.com) and [Boot.dev](https://www.boot.dev)"
        expected = [("Google", "https://www.google.com"), ("Boot.dev", "https://www.boot.dev")]
        self.assertEqual(extract_markdown_links(text), expected)

    def test_wikipedia_link(self):
        text = "Search on [Wikipedia](https://en.wikipedia.org/wiki/Python_(programming_language))"
        expected = [("Wikipedia", "https://en.wikipedia.org/wiki/Python_(programming_language)")]
        self.assertEqual(extract_markdown_links(text), expected)

    def test_extract_links_ignores_images(self):
        # NOTE: This test will currently FAIL with your existing code
        text = "Here is a link [home](/) and an image ![logo](/logo.png)"
        expected = [("home", "/")]
        self.assertEqual(extract_markdown_links(text), expected)

    def test_malformed_markdown(self):
        # Testing that it doesn't "bleed" two broken links together
        text = "Check [this link out! (missing closing paren) and [valid link](https://google.com)"
        
        # The new regex should ignore the first one and only catch the second
        expected = [("valid link", "https://google.com")]
        self.assertEqual(extract_markdown_links(text), expected)


class TestSplitNodesImage(unittest.TestCase):
    def test_split_image(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjceVZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjceVZ.png"),
            ],
            new_nodes,
        )

    def test_split_image_single(self):
        node = TextNode(
            "![image](https://www.example.com/image.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://www.example.com/image.png"),
            ],
            new_nodes,
        )

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjceVZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjceVZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_no_images(self):
        node = TextNode("This is just text with no images.", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is just text with no images.", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_non_text_node(self):
        node = TextNode("This is a bold node.", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is a bold node.", TextType.BOLD),
            ],
            new_nodes,
        )


class TestSplitNodesLink(unittest.TestCase):
    def test_split_link(self):
        node = TextNode(
            "This is text with a [link](https://boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            new_nodes,
        )

    def test_split_link_single(self):
        node = TextNode(
            "[link](https://boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://boot.dev) and [another link](https://blog.boot.dev) with text that follows",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("another link", TextType.LINK, "https://blog.boot.dev"),
                TextNode(" with text that follows", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_no_links(self):
        node = TextNode("This is just text with no links.", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is just text with no links.", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_non_text_node(self):
        node = TextNode("This is an italic node.", TextType.ITALIC)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is an italic node.", TextType.ITALIC),
            ],
            new_nodes,
        )


class TestTextToTextNodes(unittest.TestCase):
    def test_comprehensive(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_just_text(self):
        text = "This is just a plain text string."
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is just a plain text string.", TextType.TEXT),
            ],
            nodes,
        )

    def test_consecutive_formatting(self):
        text = "**Bold**_Italic_`Code`"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("Bold", TextType.BOLD),
                TextNode("Italic", TextType.ITALIC),
                TextNode("Code", TextType.CODE),
            ],
            nodes,
        )

    def test_formatting_at_edges(self):
        text = "**Start** and then the _end_"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("Start", TextType.BOLD),
                TextNode(" and then the ", TextType.TEXT),
                TextNode("end", TextType.ITALIC),
            ],
            nodes,
        )

    def test_multiple_of_same_type(self):
        text = "This **bold** and that **bold**"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" and that ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
            ],
            nodes,
        )
        
    def test_multiple_links(self):
        text = "Here is a [link1](url1) and here is [link2](url2)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("Here is a ", TextType.TEXT),
                TextNode("link1", TextType.LINK, "url1"),
                TextNode(" and here is ", TextType.TEXT),
                TextNode("link2", TextType.LINK, "url2"),
            ],
            nodes,
        )

    def test_image_and_link_together(self):
        text = "![image](img.png)[link](site.com)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "img.png"),
                TextNode("link", TextType.LINK, "site.com"),
            ],
            nodes,
        )


class TestMarkdownToBlocks(unittest.TestCase):
    def test_single_block(self):
        markdown = "This is one paragraph."
        expected = ["This is one paragraph."]
        self.assertEqual(markdown_to_blocks(markdown), expected)

    def test_two_blocks(self):
        markdown = "First paragraph.\n\nSecond paragraph."
        expected = ["First paragraph.", "Second paragraph."]
        self.assertEqual(markdown_to_blocks(markdown), expected)

    def test_blocks_are_stripped(self):
        markdown = "   First paragraph with spaces.   \n\n\tSecond paragraph with tabs.\t"
        expected = ["First paragraph with spaces.", "Second paragraph with tabs."]
        self.assertEqual(markdown_to_blocks(markdown), expected)

    def test_multiple_blank_lines(self):
        markdown = "First paragraph.\n\n\n\nSecond paragraph."
        expected = ["First paragraph.", "Second paragraph."]
        self.assertEqual(markdown_to_blocks(markdown), expected)

    def test_blank_only_input(self):
        markdown = "   \n   \n\t"
        expected = []
        self.assertEqual(markdown_to_blocks(markdown), expected)

    def test_empty_string(self):
        markdown = ""
        expected = []
        self.assertEqual(markdown_to_blocks(markdown), expected)

    def test_blank_lines_with_spaces(self):
        markdown = "First paragraph.\n  \n\t\nSecond paragraph."
        expected = ["First paragraph.", "Second paragraph."]
        self.assertEqual(markdown_to_blocks(markdown), expected)

    def test_multiline_paragraphs(self):
        markdown = """This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items"""
        expected = [
            "This is **bolded** paragraph",
            "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
            "- This is a list\n- with items",
        ]
        self.assertEqual(markdown_to_blocks(markdown), expected)

from extract_md import extract_title

class TestExtractTitle(unittest.TestCase):
    def test_extract_title_basic(self):
        markdown = "# My Page Title"
        self.assertEqual(extract_title(markdown), "My Page Title")

    def test_extract_title_with_body_content(self):
        markdown = "# My Page Title\n\nThis is a paragraph below the title."
        self.assertEqual(extract_title(markdown), "My Page Title")

    def test_extract_title_raises_when_no_h1_title(self):
        markdown = "## Not the main title"
        with self.assertRaises(ValueError):
            extract_title(markdown)

    def test_extract_title_raises_when_empty_string(self):
        markdown = ""
        with self.assertRaises(ValueError):
            extract_title(markdown)

    def test_extract_title_when_tags_come_first(self):
        markdown = "#tag1 #tag2\n# Title"
        self.assertEqual(extract_title(markdown), "Title")

    def test_extract_title_when_comment_comes_first(self):
        markdown = "comment\n# Title"
        self.assertEqual(extract_title(markdown), "Title")
    

if __name__ == "__main__":
    unittest.main()
