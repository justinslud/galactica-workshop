from io import StringIO

from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.utils import timezone

from core import editorial
from core.models import Article, Citation, Claim, Source, SourceSnapshot

from .support import WorkshopTestCase, md


def source_with_snapshot(title, text):
    source = Source.objects.create(title=title, kind='web', check_status='fetched')
    SourceSnapshot.objects.create(
        url='https://en.wikipedia.org/wiki/' + title.replace(' ', '_'), final_url='https://en.wikipedia.org/wiki/X',
        domain='en.wikipedia.org', fetched_at=timezone.now(), http_status=200, content_type='text/html',
        sha256='a' * 64, byte_count=len(text), title=title, raw_text=text, excerpt=text, source=source,
    )
    return source


class ClaimCreationTests(WorkshopTestCase):

    def test_direct_conflicting_and_absent_statuses(self):
        block_text = 'The sky is blue. The sky is green. Nobody checked.'
        items = [{'block_id': None, 'kind': 'markdown', 'data': {'text': block_text}}]
        candidate = editorial.create_candidate(
            self.article, title='Claims', opening='', items=items, citations=[], origin='agent',
            user=self.admin, claims=[
                {'block_index': 0, 'text': 'The sky is blue.', 'citations': [
                    {'source_id': str(self.source.pk), 'supports': 'States the sky is blue.', 'quote': '',
                     'stance': 'supports', 'strength': 'direct'}]},
                {'block_index': 0, 'text': 'The sky is green.', 'citations': [
                    {'source_id': str(self.other_source.pk), 'supports': 'States a conflicting colour.',
                     'quote': '', 'stance': 'conflicts', 'strength': 'direct'}]},
                {'block_index': 0, 'text': 'Nobody checked.', 'citations': []},
            ],
        )
        claims = list(candidate.claims.order_by('position'))
        self.assertEqual([c.support_status for c in claims], ['direct', 'conflicting', 'absent'])
        self.assertEqual(claims[0].start, 0)
        self.assertEqual(candidate.citations.filter(claim=claims[0]).count(), 1)
        self.assertEqual(candidate.citations.filter(claim=claims[2]).count(), 0)

    def test_claim_text_must_be_exact_substring(self):
        items = [{'block_id': None, 'kind': 'markdown', 'data': {'text': 'Exact sentence.'}}]
        with self.assertRaisesRegex(Exception, 'exact substring'):
            editorial.create_candidate(
                self.article, title='Claims', opening='', items=items, citations=[], origin='agent',
                claims=[{'block_index': 0, 'text': 'Different sentence.', 'citations': []}],
            )

    def test_quote_absent_from_snapshot_is_rejected(self):
        source = source_with_snapshot('Snapshot source', 'The preserved passage says otherwise.')
        items = [{'block_id': None, 'kind': 'markdown', 'data': {'text': 'A quoted claim.'}}]
        with self.assertRaisesRegex(Exception, 'quote is absent'):
            editorial.create_candidate(
                self.article, title='Claims', opening='', items=items, citations=[], origin='agent',
                claims=[{'block_index': 0, 'text': 'A quoted claim.', 'citations': [
                    {'source_id': str(source.pk), 'supports': 'Supports it.', 'quote': 'Not in the snapshot.',
                     'stance': 'supports', 'strength': 'direct'}]}],
            )

    def test_source_not_preserved_for_job_is_rejected(self):
        items = [{'block_id': None, 'kind': 'markdown', 'data': {'text': 'A claim.'}}]
        with self.assertRaisesRegex(Exception, 'not preserved'):
            editorial.create_candidate(
                self.article, title='Claims', opening='', items=items, citations=[], origin='agent',
                allowed_source_ids={self.other_source.pk},
                claims=[{'block_index': 0, 'text': 'A claim.', 'citations': [
                    {'source_id': str(self.source.pk), 'supports': 'Supports it.', 'quote': '',
                     'stance': 'supports', 'strength': 'direct'}]}],
            )


class ClaimArticleUITests(WorkshopTestCase):

    def test_article_expansion_shows_claim_level_evidence(self):
        source = source_with_snapshot('Claim UI source', 'The sky is blue during the day.')
        block_text = 'The sky is blue during the day. Nobody checked this sentence.'
        rev = editorial.create_published_revision(
            self.article, self.admin, items=[md(block_text)], citations=[], summary='claims',
            title=self.article.title, opening=self.article.opening,
            claims=[
                {'block_index': 0, 'text': 'The sky is blue during the day.', 'citations': [
                    {'source_id': str(source.pk), 'supports': 'States the sky colour.', 'quote': 'The sky is blue during the day.',
                     'stance': 'supports', 'strength': 'direct'}]},
                {'block_index': 0, 'text': 'Nobody checked this sentence.', 'citations': []},
            ],
        )
        claim = rev.claims.get(text='Nobody checked this sentence.')
        response = self.client.get(f'/article/{self.article.slug}/')
        self.assertContains(response, 'Claims and evidence (2)')
        self.assertContains(response, str(claim.pk))
        self.assertContains(response, 'No preserved citation is attached to this claim.')


class BackfillClaimTests(WorkshopTestCase):

    def test_backfill_is_idempotent_and_assigns_existing_citation(self):
        self.article.provenance = 'agent'
        self.article.save(update_fields=['provenance'])
        block = self.r1.blocks.get()
        block.data = {'text': 'First claim sentence. Second claim sentence.'}
        block.save(update_fields=['data'])
        Citation.objects.create(revision=self.r1, block_id=block.block_id, source=self.source,
                                supports='Second claim sentence is supported here.', quote='')
        out = StringIO()
        call_command('backfill_claims', article=self.article.slug, stdout=out)
        self.assertEqual(self.r1.claims.count(), 2)
        second = self.r1.claims.order_by('position').last()
        self.assertEqual(second.citations.count(), 1)
        call_command('backfill_claims', article=self.article.slug, stdout=out)
        self.assertEqual(self.r1.claims.count(), 2, 'backfill must be idempotent')
