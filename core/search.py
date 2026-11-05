"""FTS5 search over published articles.

The index is deliberately derived: `SearchDocument` is the materialised text, and the FTS5
table is an external-content index over it (migration 0011). Publishing or reverting refreshes
the document, so search never shows an unpublished revision. If the index drifts, the repair is
`manage.py rebuild_search`, not a silent query-time fallback.
"""
import json
import re

from django.db import OperationalError, connection

from .models import Article, SearchDocument

MAX_QUERY = 200
SNIPPET_RADIUS = 140


def _block_text(block):
    data = block.data or {}
    if block.kind == 'markdown':
        return data.get('text', '') or ''
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def build_document(article, revision):
    blocks = list(revision.blocks.order_by('position'))
    body = '\n\n'.join(_block_text(block) for block in blocks)
    claims = '\n'.join(claim.text for claim in revision.claims.order_by('position'))
    titles = []
    for citation in revision.citations.select_related('source'):
        if citation.source.title not in titles:
            titles.append(citation.source.title)
    return {
        'revision': revision,
        'title': revision.title or article.title,
        'opening': revision.opening or article.opening,
        'body': body,
        'claims': claims,
        'sources': '\n'.join(titles),
        'content_hash': revision.content_hash,
    }


def index_article(article):
    """Upsert or remove one article's search document. Safe to call inside the publish transaction."""
    fresh = Article.objects.select_related('published').filter(pk=article.pk).first()
    if fresh is None:
        return None
    if fresh.published_id is None:
        SearchDocument.objects.filter(article=fresh).delete()
        return None
    document, _ = SearchDocument.objects.update_or_create(
        article=fresh, defaults=build_document(fresh, fresh.published),
    )
    return document


def query_terms(query):
    query = (query or '').strip()[:MAX_QUERY]
    terms = [term for term in re.split(r'\s+', query) if term]
    # Strip characters that are FTS5 operators; the user gets a literal-term search, not a query language.
    terms = [re.sub(r'["*():^\-]', ' ', term).strip() for term in terms]
    return [term for term in terms if term][:12]


def fts_match_expression(query):
    terms = query_terms(query)
    if not terms:
        return ''
    return ' AND '.join('"' + term.replace('"', '""') + '"' for term in terms)


def _snippet(text, terms):
    text = ' '.join((text or '').split())
    if not text:
        return ''
    lower = text.lower()
    positions = [lower.find(term.lower()) for term in terms]
    positions = [pos for pos in positions if pos >= 0]
    if not positions:
        return text[:SNIPPET_RADIUS * 2].strip()
    start = max(0, min(positions) - SNIPPET_RADIUS // 2)
    end = min(len(text), start + SNIPPET_RADIUS * 2)
    prefix = '…' if start else ''
    suffix = '…' if end < len(text) else ''
    return f'{prefix}{text[start:end].strip()}{suffix}'


def _match_reasons(document, terms):
    fields = {
        'title': document.title, 'opening': document.opening, 'body': document.body,
        'claims': document.claims, 'sources': document.sources,
    }
    reasons = []
    for name, value in fields.items():
        haystack = (value or '').lower()
        if any(term.lower() in haystack for term in terms):
            reasons.append(name)
    return reasons


def search(query, limit=40):
    """Return ranked search hits, or an empty list for a blank query."""
    expression = fts_match_expression(query)
    if not expression:
        return []
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT rowid, bm25(core_search_fts) AS rank FROM core_search_fts '
                'WHERE core_search_fts MATCH %s ORDER BY rank LIMIT %s',
                [expression, max(1, min(int(limit), 100))],
            )
            rows = cursor.fetchall()
    except OperationalError:
        # A missing/old index should not take the page down; the health check reports the drift.
        return []
    if not rows:
        return []
    ranks = {rowid: rank for rowid, rank in rows}
    documents = {doc.pk: doc for doc in SearchDocument.objects.filter(pk__in=ranks).select_related('article')}
    terms = query_terms(query)
    results = []
    for rowid, rank in rows:
        document = documents.get(rowid)
        if document is None:
            continue
        results.append({
            'document': document,
            'article': document.article,
            'rank': rank,
            'reasons': _match_reasons(document, terms),
            'snippet': _snippet(document.body or document.opening, terms),
        })
    return results


def check_index():
    """Return a small integrity report. Does not repair anything."""
    report = {'documents': SearchDocument.objects.count(), 'indexed': 0, 'ok': True, 'errors': []}
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT count(*) FROM core_search_fts')
            report['indexed'] = cursor.fetchone()[0]
            cursor.execute("INSERT INTO core_search_fts(core_search_fts) VALUES ('integrity-check')")
    except OperationalError as exc:
        report['ok'] = False
        report['errors'].append(str(exc))
        return report
    if report['documents'] != report['indexed']:
        report['ok'] = False
        report['errors'].append(
            f'SearchDocument has {report["documents"]} rows but the FTS index has {report["indexed"]}.'
        )
    return report
