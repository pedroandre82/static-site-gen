import re
from textnode import TextNode, TextType

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        parts = node.text.split(delimiter)

        if len(parts) % 2 == 0:
            raise ValueError(f"Missing closing delimiter: {delimiter}")

        for i, part in enumerate(parts):
            if part == "":
                continue
            if i % 2 == 0:
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))

    return new_nodes

# images
IMG_PATTERN = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"

# regular links
# LINK_PATTERN = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
LINK_PATTERN = r"(?<!!)\[([^\[\]]+)\]\(([^()\s]+(?:\([^()\s]+\))?[^()\s]*)\)"

def extract_markdown_images(text) -> list[tuple[str, str]]:
    return re.findall(IMG_PATTERN, text)

def extract_markdown_links(text) -> list[tuple[str, str]]:
    # The (?<!!) is a negative lookbehind
    matches = re.findall(LINK_PATTERN, text)
    return matches

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    if not old_nodes:
        return []
    nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            if node.text != "":
                nodes.append(node)
            continue
        images = extract_markdown_images(node.text)
        if not images:
            if node.text != "":
                nodes.append(node)
            continue
        original_text = node.text
        for image in images:
            sections = original_text.split(f"![{image[0]}]({image[1]})", 1)
            if sections[0] != "":
                nodes.append(TextNode(sections[0], TextType.TEXT))
            nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
            original_text = sections[1]
        if original_text != "":
            nodes.append(TextNode(original_text, TextType.TEXT))
    return nodes

def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    if not old_nodes:
        return []
    nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            if node.text != "":
                nodes.append(node)
            continue
        links = extract_markdown_links(node.text)
        if not links:
            if node.text != "":
                nodes.append(node)
            continue
        original_text = node.text
        for link in links:
            sections = original_text.split(f"[{link[0]}]({link[1]})", 1)
            if sections[0] != "":
                nodes.append(TextNode(sections[0], TextType.TEXT))
            nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            original_text = sections[1]
        if original_text != "":
            nodes.append(TextNode(original_text, TextType.TEXT))
    return nodes

def text_to_textnodes(text: str) -> list[TextNode]:
    # Start with a single TextNode containing the raw text
    nodes = [TextNode(text, TextType.TEXT)]
    
    # Process images first (usually best to do images before links, 
    # since images look like links but start with an exclamation mark)
    nodes = split_nodes_image(nodes)
    
    # Process links
    nodes = split_nodes_link(nodes)
    
    # Process bold (must be processed before italic since ** contains _)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    
    # Process italic
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    
    # Process code blocks
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    
    return nodes    

def markdown_to_blocks(markdown: str) -> list[str]:
    blocks = re.split(r"\n\s*\n", markdown)
    return [block.strip() for block in blocks if block.strip()]
