import json

from django.db import migrations


FTS_SQL = """
CREATE VIRTUAL TABLE core_search_fts USING fts5(
    title, opening, body, claims, sources,
    content='core_searchdocument',
    content_rowid='id',
    tokenize='unicode61 remove_diacritics 2'
);
CREATE TRIGGER core_searchdocument_ai AFTER INSERT ON core_searchdocument BEGIN
    INSERT INTO core_search_fts(rowid, title, opening, body, claims, sources)
    VALUES (new.id, new.title, new.opening, new.body, new.claims, new.sources);
END;
CREATE TRIGGER core_searchdocument_ad AFTER DELETE ON core_searchdocument BEGIN
    INSERT INTO core_search_fts(core_search_fts, rowid, title, opening, body, claims, sources)
    VALUES ('delete', old.id, old.title, old.opening, old.body, old.claims, old.sources);
END;
CREATE TRIGGER core_searchdocument_au AFTER UPDATE ON core_searchdocument BEGIN
    INSERT INTO core_search_fts(core_search_fts, rowid, title, opening, body, claims, sources)
    VALUES ('delete', old.id, old.title, old.opening, old.body, old.claims, old.sources);
    INSERT INTO core_search_fts(rowid, title, opening, body, claims, sources)
    VALUES (new.id, new.title, new.opening, new.body, new.claims, new.sources);
END;
"""

DROP_SQL = """
DROP TRIGGER IF EXISTS core_searchdocument_au;
DROP TRIGGER IF EXISTS core_searchdocument_ad;
DROP TRIGGER IF EXISTS core_searchdocument_ai;
DROP TABLE IF EXISTS core_search_fts;
"""


def _text_of(block):
    data = block.data or {}
    if block.kind == 'markdown':
        return data.get('text', '')
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def build_search_documents(apps, schema_editor):
    Article = apps.get_model('core', 'Article')
    SearchDocument = apps.get_model('core', 'SearchDocument')
    PublicationEvent = apps.get_model('core', 'PublicationEvent')

    # Year-long licence snapshots: a published copy keeps the licence that applied then.
    for event in PublicationEvent.objects.filter(license='').select_related('article').iterator():
        event.license = event.article.license
        event.save(update_fields=['license'])

    for article in Article.objects.filter(published__isnull=False).select_related('published').iterator():
        revision = article.published
        blocks = revision.blocks.order_by('position')
        body = '\n\n'.join(_text_of(block) for block in blocks)
        claims = '\n'.join(claim.text for claim in revision.claims.order_by('position'))
        titles = []
        for citation in revision.citations.select_related('source'):
            if citation.source.title not in titles:
                titles.append(citation.source.title)
        SearchDocument.objects.update_or_create(
            article=article,
            defaults={
                'revision': revision,
                'title': revision.title or article.title,
                'opening': revision.opening or article.opening,
                'body': body,
                'claims': claims,
                'sources': '\n'.join(titles),
                'content_hash': revision.content_hash,
            },
        )


def rebuild_fts(apps, schema_editor):
    schema_editor.execute("INSERT INTO core_search_fts(core_search_fts) VALUES ('rebuild');")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_article_attribution_article_license_and_more'),
    ]

    operations = [
        migrations.RunSQL(FTS_SQL, reverse_sql=DROP_SQL),
        migrations.RunPython(build_search_documents, migrations.RunPython.noop),
        migrations.RunPython(rebuild_fts, migrations.RunPython.noop),
    ]
