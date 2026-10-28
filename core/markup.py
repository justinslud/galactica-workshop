"""The one renderer for article content. Editor preview and the reading view both call render_block."""
import difflib
import re

import markdown as markdown_lib
import nh3
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

ALLOWED_TAGS = {
    'p', 'br', 'hr', 'h2', 'h3', 'h4', 'strong', 'em', 'code', 'pre', 'blockquote',
    'ul', 'ol', 'li', 'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'details', 'summary', 'img',
    'sup', 'sub',
}
ALLOWED_ATTRIBUTES = {
    'a': {'href', 'title'},
    'img': {'src', 'alt'},
    'th': {'align'},
    'td': {'align'},
}


def render_markdown(text):
    html = markdown_lib.markdown(text or '', extensions=['tables', 'fenced_code', 'sane_lists'])
    return mark_safe(nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes={'http', 'https', 'mailto'},
        link_rel='noopener noreferrer nofollow',
    ))


def render_block(kind, data):
    """Return safe HTML for one block. Used by the editor preview and the article page."""
    if kind == 'markdown':
        return format_html('<div class="block block-markdown">{}</div>', render_markdown(data.get('text', '')))
    if kind == 'image':
        return format_html(
            '<figure class="block block-image"><img src="{}" alt="{}" loading="lazy">'
            '<figcaption>{}<span class="credit">Image credit: {}</span></figcaption></figure>',
            data.get('src', ''), data.get('alt', ''), data.get('caption', ''), data.get('credit', ''),
        )
    if kind == 'table':
        head = ''.join(format_html('<th scope="col">{}</th>', h) for h in data.get('headers', []))
        body = ''.join(
            '<tr>' + ''.join(format_html('<td>{}</td>', c) for c in row) + '</tr>'
            for row in data.get('rows', [])
        )
        return format_html(
            '<figure class="block block-table"><table><caption>{}</caption>'
            '<thead><tr>{}</tr></thead><tbody>{}</tbody></table></figure>',
            data.get('caption', ''), mark_safe(head), mark_safe(body),
        )
    if kind == 'timeline':
        items = ''.join(
            format_html('<li><time>{}</time><span>{}</span></li>', e.get('date', ''), e.get('text', ''))
            for e in data.get('events', [])
        )
        return format_html(
            '<section class="block block-timeline"><h3>{}</h3><ol>{}</ol></section>',
            data.get('title', ''), mark_safe(items),
        )
    return format_html('<div class="block block-unknown">Unsupported block type: {}</div>', kind)


TOKEN = re.compile(r'\s+|[^\s]+')


def word_diff_html(before, after):
    """Word-level diff. All text is escaped; only <del> and <ins> wrappers are added."""
    a_tokens = TOKEN.findall(before or '')
    b_tokens = TOKEN.findall(after or '')
    matcher = difflib.SequenceMatcher(None, a_tokens, b_tokens, autojunk=False)
    parts = []
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        old = escape(''.join(a_tokens[i1:i2]))
        new = escape(''.join(b_tokens[j1:j2]))
        if op == 'equal':
            parts.append(new)
        else:
            if old:
                parts.append(f'<del>{old}</del>')
            if new:
                parts.append(f'<ins>{new}</ins>')
    return mark_safe(''.join(parts))


def sentence_lengths(text):
    sentences = [s for s in re.split(r'(?<=[.!?])\s+', text or '') if s.strip()]
    return [len(s.split()) for s in sentences]
