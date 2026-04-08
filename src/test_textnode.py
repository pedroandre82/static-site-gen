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

if __name__ == "__main__":
    unittest.main()
