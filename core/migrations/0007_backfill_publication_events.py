"""Backfill the append-only publication history from the old Article.published pointer.

Before M0 the database kept only the current pointer and the revision rows. Published and
superseded revisions are enough to reconstruct the linear publication chain for existing data.
"""

from django.db import migrations


def backfill(apps, schema_editor):
    Article = apps.get_model('core', 'Article')
    Revision = apps.get_model('core', 'Revision')
    PublicationEvent = apps.get_model('core', 'PublicationEvent')

    for article in Article.objects.all().iterator():
        revisions = list(
            Revision.objects.filter(
                article_id=article.pk, state__in=('published', 'superseded'),
            ).order_by('number')
        )
        if article.published_id and all(rev.pk != article.published_id for rev in revisions):
            current = Revision.objects.filter(pk=article.published_id).first()
            if current is not None:
                revisions.append(current)
        previous = None
        for sequence, revision in enumerate(revisions, start=1):
            if revision.reverts_id:
                kind = 'revert'
                decision = 'revert'
            elif sequence == 1:
                kind = 'initial'
                decision = 'direct'
            else:
                kind = 'publish'
                decision = 'approve'
            PublicationEvent.objects.create(
                article_id=article.pk,
                revision_id=revision.pk,
                sequence=sequence,
                kind=kind,
                published_at=revision.published_at or revision.created_at,
                published_by_id=revision.created_by_id,
                previous_revision_id=previous.pk if previous is not None else None,
                policy_version='',
                decision=decision,
                reason=revision.summary or '',
                content_hash=revision.content_hash or '',
            )
            previous = revision


def remove_backfill(apps, schema_editor):
    PublicationEvent = apps.get_model('core', 'PublicationEvent')
    PublicationEvent.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_m0_publication_topics_watch'),
    ]

    operations = [
        migrations.RunPython(backfill, remove_backfill),
    ]
