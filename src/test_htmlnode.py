import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_init_no_args(self):
        node = HTMLNode()
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)

    def test_init_with_values(self):
        props = {"href": "/home", "title": "Home"}
        children = [HTMLNode("b"), HTMLNode("i")]
        node = HTMLNode(tag="a", value="link text", children=children, props=props)

        self.assertEqual(node.tag, "a")
        self.assertEqual(node.value, "link text")
        self.assertEqual(node.children, children)
        self.assertEqual(node.props, props)

    def test_props_to_html_no_props(self):
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_with_props(self):
        node = HTMLNode(props={"href": "/home", "class": "btn"})
        expected = ' href="/home" class="btn"'
        self.assertEqual(node.props_to_html(), expected)

    # def test_props_to_html_with_quotes_in_value(self):
    #     node = HTMLNode(props={"data-tooltip": 'Click "here" to continue'})
    #     expected = r' data-tooltip="Click &quot;here&quot; to continue"'
    #     # Note: HTML quoting is not handled inside your current implementation;
    #     # if you want to escape, you’ll need to expand props_to_html.
    #     # For now, just test the raw string.
    #     self.assertEqual(node.props_to_html(), expected)

    def test_props_to_html_with_boolean_attr_value(self):
        node = HTMLNode(props={"disabled": True})
        expected = ' disabled="True"'
        self.assertEqual(node.props_to_html(), expected)

    def test_repr_no_props_no_children(self):
        node = HTMLNode(tag="p", value="Hello")
        expected = 'HTMLNode(<p>Hello <- None)'
        self.assertEqual(repr(node), expected)

    def test_repr_with_props(self):
        node = HTMLNode(tag="a", value="link", props={"href": "/home"})
        expected = 'HTMLNode(<a href="/home">link <- None)'
        self.assertEqual(repr(node), expected)

    def test_repr_with_children(self):
        children = [HTMLNode("span")]
        node = HTMLNode(tag="div", children=children)
        # repr will show the children list, which is messy but consistent
        expected_start = 'HTMLNode(<div>None <-'
        self.assertTrue(repr(node).startswith(expected_start))

    def test_to_html_raises_not_implemented(self):
        node = HTMLNode()
        with self.assertRaises(NotImplementedError):
            node.to_html()


class TestLeafNode(unittest.TestCase):
    def test_init_without_props(self):
        node = LeafNode("p", "hello")
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, "hello")
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)

    def test_init_with_props(self):
        node = LeafNode("a", "link", {"href": "https://example.com"})
        self.assertEqual(node.tag, "a")
        self.assertEqual(node.value, "link")
        self.assertEqual(node.props, {"href": "https://example.com"})

    def test_to_html_without_props(self):
        node = LeafNode("p", "hello")
        self.assertEqual(node.to_html(), "<p>hello</p>")

    def test_to_html_with_props(self):
        node = LeafNode("a", "click here", {"href": "https://example.com", "target": "_blank"})
        self.assertEqual(
            node.to_html(),
            '<a href="https://example.com" target="_blank">click here</a>',
        )

    def test_to_html_empty_value(self):
        node = LeafNode("p", "")
        self.assertEqual(node.to_html(), "")

    def test_to_html_none_value(self):
        node = LeafNode("p", None)
        self.assertEqual(node.to_html(), "")

    def test_repr_without_props(self):
        node = LeafNode("p", "hello")
        self.assertEqual(repr(node), "LeafNode(p,, hello)")

    def test_repr_with_props(self):
        node = LeafNode("a", "link", {"href": "https://example.com"})
        self.assertEqual(repr(node), 'LeafNode(a, href="https://example.com", link)')

    def test_str_matches_to_html(self):
        node = LeafNode("strong", "bold text")
        self.assertEqual(str(node), node.to_html())
        self.assertEqual(str(node), "<strong>bold text</strong>")


class TestParentNode(unittest.TestCase):
    def test_to_html_with_one_child(self):
        child = LeafNode("span", "child")
        node = ParentNode("p", [child])
        self.assertEqual(node.to_html(), "<p><span>child</span></p>")

    def test_to_html_with_multiple_children(self):
        child1 = LeafNode("b", "bold")
        child2 = LeafNode("i", "italic")
        child3 = LeafNode("span", "plain")
        node = ParentNode("p", [child1, child2, child3])

        self.assertEqual(
            node.to_html(),
            "<p><b>bold</b><i>italic</i><span>plain</span></p>"
        )

    def test_to_html_with_props(self):
        child = LeafNode("a", "click")
        node = ParentNode("div", [child], {"class": "container", "id": "main"})

        self.assertEqual(
            node.to_html(),
            '<div class="container" id="main"><a>click</a></div>'
        )

    def test_to_html_raises_value_error_when_tag_is_none(self):
        child = LeafNode("span", "child")
        node = ParentNode(None, [child])

        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_raises_value_error_when_children_is_none(self):
        node = ParentNode("div", None)

        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_raises_value_error_when_children_is_empty_list(self):
        node = ParentNode("div", [])

        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_with_nested_parent_nodes(self):
        inner = ParentNode("span", [LeafNode("b", "deep")])
        outer = ParentNode("div", [inner])

        self.assertEqual(
            outer.to_html(),
            "<div><span><b>deep</b></span></div>"
        )