import re
from textnode import TextNode, TextType
from enum import Enum
from htmlnode import HTMLNode, LeafNode, ParentNode
import os

class BlockType(Enum):
    PARAGRAPH = 1
    HEADING = 2
    CODE = 3
    QUOTE = 4
    UNORDERED_LIST = 5
    ORDERED_LIST = 6


def split_nodes_delimiter(old_nodes, delimiter, text_type) -> list[TextNode]:
    """
    Splits a list of TextNodes based on a delimiter, and returns a new list of TextNodes.
    """
    if not old_nodes:
        return []
    
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

def extract_markdown_images(text) -> list[tuple[str, str]]:
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text) -> list[tuple[str, str]]:
    matches = re.findall(r"(?<!!)\[([^\[\]]+)\]\(([^()\s]+(?:\([^()\s]+\))?[^()\s]*)\)", text)
    return matches

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    """
    Splits a list of TextNodes based on images, and returns a new list of TextNodes.
    """
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


def block_to_block_type(block: str) -> BlockType:
    if re.match(r"^#{1,6} .+", block):
        return BlockType.HEADING

    if re.match(r"^```[\w]*\n[\s\S]*\n```$", block):
        return BlockType.CODE

    lines = block.split("\n")

    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    if all(re.match(r"^\d+\. ", line) for line in lines):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


def markdown_to_html_node(markdown: str) -> HTMLNode:
    blocks = markdown_to_blocks(markdown)
    nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.PARAGRAPH:
            block = block.replace("\n", " ")
            html_nodes = [text_node.to_html_node() for text_node in text_to_textnodes(block)]
            nodes.append(ParentNode("p", html_nodes))
        
        elif block_type == BlockType.HEADING:
            header, text = block.split(" ", 1)
            level = len(header)
            html_nodes = [text_node.to_html_node() for text_node in text_to_textnodes(text)]
            nodes.append(ParentNode(f"h{level}", html_nodes))
        
        elif block_type == BlockType.CODE:
            language = re.findall(r"```([\w]*)", block)[0]
            block = block.replace(f"```{language}\n", "")
            block = block.replace("\n```", "")
            nodes.append(ParentNode("pre", [LeafNode("code", block)]))

        elif block_type == BlockType.QUOTE:
            lines = block.split("\n")
            cleaned_lines = [line.removeprefix("> ").removeprefix(">") for line in lines]
            quote_text = "\n".join(cleaned_lines)
            html_nodes = [text_node.to_html_node() for text_node in text_to_textnodes(quote_text)]
            nodes.append(ParentNode("blockquote", html_nodes))
        
        elif block_type == BlockType.UNORDERED_LIST:
            lines = block.split("\n")
            list_items = [line.removeprefix("- ") for line in lines if line.startswith("- ")]
            html_nodes = [ParentNode("li", [text_node.to_html_node() for text_node in text_to_textnodes(line)]) for line in list_items]
            nodes.append(ParentNode("ul", html_nodes))
            
        elif block_type == BlockType.ORDERED_LIST:
            lines = block.split("\n")
            list_items = [line[3:] for line in lines if re.match(r"^\d+\. ", line)]
            html_nodes = [ParentNode("li", [text_node.to_html_node() for text_node in text_to_textnodes(line)]) for line in list_items]
            nodes.append(ParentNode("ol", html_nodes))

    return ParentNode("div", nodes)


def extract_title(markdown: str) -> str:
    matches = re.findall(r"^# (.+)", markdown, re.MULTILINE)
    if not matches:
        raise ValueError("No title found in markdown")
    return matches[0]

def url_join(basepath: str, path: str) -> str:
    if not basepath or basepath == "/":
        return "/" + path.lstrip("/")
    return basepath.rstrip("/") + "/" + path.lstrip("/")

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r") as f:
        markdown = f.read()

    with open(template_path, "r") as f:
        template = f.read()

    content_html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    full_page = template.replace("{{ Title }}", title).replace("{{ Content }}", content_html)

    full_page = full_page.replace('href="/', f'href="{url_join(basepath, "")}')
    full_page = full_page.replace('src="/', f'src="{url_join(basepath, "")}')

    dest_dir = os.path.dirname(dest_path)
    if dest_dir != "":
        os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w") as f:
        f.write(full_page)


def generate_page_recursive(content_path_dir, template_path, dest_path_dir, basepath):
    for entry in os.listdir(content_path_dir):        
        src_path = os.path.join(content_path_dir, entry)
        dest_path = os.path.join(dest_path_dir, entry)

        if os.path.isfile(src_path) and src_path.endswith(".md"):
            generate_page(src_path, template_path, dest_path.removesuffix(".md") + ".html", basepath)
        else:
            generate_page_recursive(src_path, template_path, dest_path, basepath)
