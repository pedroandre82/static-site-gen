
class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        if not self.props:
            return ""
        return "".join([f' {key}="{value}"' for key, value in self.props.items()])

    def __repr__(self) -> str:
        return f"HTMLNode(<{self.tag}{self.props_to_html()}>{self.value} <- {self.children})"

    def __str__(self) -> str:
        return self.to_html()


class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self) -> str:
        if self.tag == "img":
            return f"<img{self.props_to_html()}>"
        if not self.value:
            return ""
        if not self.tag:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self) -> str:
        return f"LeafNode({self.tag},{self.props_to_html()}, {self.value})"
    

class ParentNode(HTMLNode):
    def __init__(self, tag, children: list, props=None):        
        super().__init__(tag, None, children, props)

    def to_html(self) -> str:
        if not self.children:
            raise ValueError("Parent node must have children")
        if self.tag is None:
            raise ValueError("Parent node must have a tag")
        children_html = "".join(child.to_html() for child in self.children)
        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"
