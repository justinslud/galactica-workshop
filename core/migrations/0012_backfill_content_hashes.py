import hashlib
import json

from django.db import migrations


def _content_hash(revision):
    """Same canonical snapshot as core.editorial.content_hash, inlined for a data migration."""
    snapshot = {
        'title': revision.title,
        'opening': revision.opening,
        'blocks': [
            {'block_id': str(block.block_id), 'kind': block.kind, 'data': block.data}
            for block in revision.blocks.order_by('position')
        ],
        'citations': sorted(
            [
                {'block_id': str(citation.block_id), 'source': str(citation.source_id),
                 'supports': citation.supports, 'quote': citation.quote,
                 'stance': citation.stance, 'strength': citation.strength}
                for citation in revision.citations.all()
            ],
            key=lambda item: json.dumps(item, sort_keys=True),
        ),
        'claims': sorted(
            [
                {
                    'block_id': str(claim.block_id), 'position': claim.position, 'text': claim.text,
                    'start': claim.start, 'end': claim.end,
                    'citations': sorted(
                        [
                            {'source': str(citation.source_id), 'supports': citation.supports,
                             'quote': citation.quote, 'stance': citation.stance,
                             'strength': citation.strength}
                            for citation in claim.citations.all()
                        ],
                        key=lambda item: json.dumps(item, sort_keys=True),
                    ),
                }
                for claim in revision.claims.all()
            ],
            key=lambda item: json.dumps(item, sort_keys=True),
        ),
    }
    return hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()


def backfill(apps, schema_editor):
    Revision = apps.get_model('core', 'Revision')
    PublicationEvent = apps.get_model('core', 'PublicationEvent')
    SearchDocument = apps.get_model('core', 'SearchDocument')

    for revision in Revision.objects.filter(content_hash='').iterator():
        revision.content_hash = _content_hash(revision)
        revision.save(update_fields=['content_hash'])

    for event in PublicationEvent.objects.filter(content_hash='').select_related('revision').iterator():
        event.content_hash = event.revision.content_hash
        event.save(update_fields=['content_hash'])

    for document in SearchDocument.objects.filter(content_hash='').select_related('revision').iterator():
        if document.revision_id:
            document.content_hash = document.revision.content_hash
            document.save(update_fields=['content_hash'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_search_fts_and_license_backfill'),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
