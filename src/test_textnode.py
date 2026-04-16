import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_ne(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_text_node_not_equal_url(self):
        node1 = TextNode("hello", TextType.LINK, "https://example.com")
        node2 = TextNode("hello", TextType.LINK, "https://another.com")
        self.assertNotEqual(node1, node2)

    def test_with_other_class(self):
        node = TextNode("This is a text node", TextType.BOLD)
        class Dummy:
            pass
        with self.assertRaises(AttributeError):
            node == Dummy()

    def test_repr(self):
        node = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(
            repr(node),
            "TextNode(This is a text node, bold, None)",
        )

class TestTextNodeToHTML(unittest.TestCase):
    def test_text_type_text(self):
        leaf_node = TextNode("plain text", TextType.TEXT).to_html_node()
        self.assertEqual(leaf_node.tag, None)
        self.assertEqual(leaf_node.value, "plain text")
        self.assertEqual(leaf_node.children, None)
        self.assertEqual(leaf_node.props, None)

    def test_text_type_bold(self):
        leaf_node = TextNode("bold text", TextType.BOLD).to_html_node()
        self.assertEqual(leaf_node.tag, "b")
        self.assertEqual(leaf_node.value, "bold text")
        self.assertEqual(leaf_node.children, None)
        self.assertEqual(leaf_node.props, None)

    def test_text_type_italic(self):
        leaf_node = TextNode("italic text", TextType.ITALIC).to_html_node()
        self.assertEqual(leaf_node.tag, "i")
        self.assertEqual(leaf_node.value, "italic text")
        self.assertEqual(leaf_node.children, None)
        self.assertEqual(leaf_node.props, None)

    def test_text_type_code(self):
        leaf_node = TextNode("code text", TextType.CODE).to_html_node()
        self.assertEqual(leaf_node.tag, "code")
        self.assertEqual(leaf_node.value, "code text")
        self.assertEqual(leaf_node.children, None)
        self.assertEqual(leaf_node.props, None)

    def test_text_type_link(self):
        leaf_node = TextNode("Perplexity", TextType.LINK, "https://perplexity.ai").to_html_node()
        self.assertEqual(leaf_node.tag, "a")
        self.assertEqual(leaf_node.value, "Perplexity")
        self.assertEqual(leaf_node.children, None)
        self.assertEqual(leaf_node.props, {"href": "https://perplexity.ai"})

    def test_text_type_image(self):
        leaf_node = TextNode("logo", TextType.IMAGE, "/images/logo.png").to_html_node()
        self.assertEqual(leaf_node.tag, "img")
        self.assertEqual(leaf_node.value, "")
        self.assertEqual(leaf_node.children, None)
        self.assertEqual(leaf_node.props, {"src": "/images/logo.png", "alt": "logo"})

    def test_invalid_text_type_raises(self):
        node = TextNode("oops", "not-a-real-type")
        with self.assertRaisesRegex(ValueError, "Unknown text type"):
            node.to_html_node()


if __name__ == "__main__":
    unittest.main()
