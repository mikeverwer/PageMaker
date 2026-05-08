"""
Reformat HTML output to be more readable than BeautifulSoup's prettify().

prettify() puts every element on its own line with single-space indentation,
which makes simple structures like nav menus unnecessarily verbose:

    <li>
     <a href="/foo">
      Foo
     </a>
    </li>

This module collapses such structures while preserving block-level
hierarchy with 2-space indentation:

    <li><a href="/foo">Foo</a></li>

Three rules govern multi-line vs. inline rendering:

  1. Tags in ALWAYS_EXPAND (structural containers like <head>, <main>, <body>)
     always expand multi-line if they have any non-empty children.
  2. Tags in VERBATIM_TAGS (<pre>, <script>, <style>, <textarea>) have their
     contents preserved as-is.
  3. Other block-level tags expand multi-line only if they contain block
     descendants; otherwise they collapse onto a single line.

Comments and DOCTYPE declarations are preserved with their delimiters intact.
"""

import html
import re
import sys
from bs4 import BeautifulSoup, Comment, Doctype, NavigableString, Tag

INDENT = "  "

# Tags that, when present, should be detected as block-level by ancestors
# (i.e. force the parent to render multi-line).
BLOCK_TAGS = frozenset({
    'html', 'head', 'body',
    'nav', 'header', 'footer', 'main', 'article', 'section', 'aside',
    'div', 'form', 'fieldset', 'figure', 'pre', 'blockquote', 'address',
    'ul', 'ol', 'li', 'dl', 'dt', 'dd', 'menu',
    'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'caption',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p',
    # Head children — included so <head> sees them as block descendants.
    'meta', 'link', 'title', 'script', 'style', 'base', 'noscript',
})

# Tags that always render multi-line if they have any non-empty children,
# regardless of whether those children are block-level themselves. This
# prevents structural containers from collapsing into single lines.
ALWAYS_EXPAND = frozenset({
    'html', 'head', 'body',
    'nav', 'header', 'footer', 'main', 'article', 'section', 'aside',
    'form', 'figure', 'fieldset',
    'ul', 'ol', 'dl', 'menu',
    'table', 'thead', 'tbody', 'tfoot', 'tr',
})

# Tags whose inner content is preserved verbatim — no whitespace stripping,
# no recursive reformatting. Required for <script>/<style> where whitespace
# is significant, and for <pre>/<textarea> where it's user-facing.
VERBATIM_TAGS = frozenset({
    'pre', 'script', 'style', 'textarea',
})

VOID_TAGS = frozenset({
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr',
})


def _attr_value(v):
    if isinstance(v, list):
        v = " ".join(v)
    return html.escape(str(v), quote=True)


def _open_tag(tag):
    if not tag.attrs:
        return f"<{tag.name}>"
    attrs = " ".join(f'{k}="{_attr_value(v)}"' for k, v in tag.attrs.items())
    return f"<{tag.name} {attrs}>"


def _has_block_descendant(tag):
    for d in tag.descendants:
        if isinstance(d, Tag) and d.name in BLOCK_TAGS:
            return True
    return False


def _has_nonempty_children(tag):
    """True if `tag` has any child that's not pure whitespace."""
    for child in tag.children:
        if isinstance(child, (Comment, Doctype)):
            return True
        if isinstance(child, NavigableString):
            if str(child).strip():
                return True
        else:
            return True
    return False


def _render_verbatim(tag, level):
    """Preserve the tag's content as-is, with the open/close on their own
    lines if the content spans multiple lines."""
    pad = INDENT * level
    open_str = _open_tag(tag)
    close_str = f"</{tag.name}>"
    content = tag.decode_contents()

    # Empty body: collapse.
    if not content.strip():
        return pad + open_str + close_str

    # Single-line body: collapse.
    if "\n" not in content.strip():
        return pad + open_str + content.strip() + close_str

    # Multi-line: drop blank leading/trailing lines, preserve internal indent.
    lines = content.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    inner = "\n".join(lines)
    return pad + open_str + "\n" + inner + "\n" + pad + close_str


def _render_inline(node):
    if isinstance(node, Doctype):
        return f"<!DOCTYPE {str(node)}>"
    if isinstance(node, Comment):
        return f"<!--{str(node)}-->"
    if isinstance(node, NavigableString):
        # Collapse whitespace runs to single spaces but DON'T strip — outer
        # whitespace is stripped at the parent tag's boundary so that a
        # single inter-sibling space survives concatenation.
        return re.sub(r'\s+', ' ', str(node))
    if node.name in VOID_TAGS:
        return _open_tag(node)
    inner_parts = [_render_inline(child) for child in node.children]
    inner = ''.join(inner_parts).strip()
    return _open_tag(node) + inner + f"</{node.name}>"


def _render(node, level):
    pad = INDENT * level

    if isinstance(node, Doctype):
        return pad + f"<!DOCTYPE {str(node)}>"
    if isinstance(node, Comment):
        return pad + f"<!--{str(node)}-->"
    if isinstance(node, NavigableString):
        text = str(node).strip()
        return pad + text if text else ""

    if node.name in VERBATIM_TAGS:
        return _render_verbatim(node, level)

    if node.name in VOID_TAGS:
        return pad + _open_tag(node)

    # Decide whether to expand:
    #  - Tags in ALWAYS_EXPAND expand if they have any non-empty children.
    #  - Other block-level tags expand only if they have block descendants.
    #  - Inline tags never expand.
    if node.name in ALWAYS_EXPAND:
        expand = _has_nonempty_children(node)
    else:
        expand = _has_block_descendant(node)

    if not expand:
        return pad + _render_inline(node)

    lines = [pad + _open_tag(node)]
    for child in node.children:
        rendered = _render(child, level + 1)
        if rendered:
            lines.append(rendered)
    lines.append(pad + f"</{node.name}>")
    return "\n".join(lines)


def reformat(html_or_tag, level=0):
    """
    Reformat HTML to a readable form.

    Args:
        html_or_tag: an HTML string or a bs4 Tag.
        level: starting indentation level (useful when inserting the result
               into an already-indented context).

    Returns:
        Reformatted HTML string with no trailing newline.
    """
    if isinstance(html_or_tag, Tag):
        return _render(html_or_tag, level)

    soup = BeautifulSoup(html_or_tag, 'html.parser')
    pieces = []
    for child in soup.children:
        rendered = _render(child, level)
        if rendered:
            pieces.append(rendered)
    return "\n".join(pieces)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding='utf-8') as f:
            source = f.read()
    else:
        source = sys.stdin.read()
    print(reformat(source))
