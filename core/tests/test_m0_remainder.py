import json
import uuid
from io import StringIO

from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from core import agent_auth, configs, editorial
from core.models import Agent, Article, IdempotencyRecord, Job, Proposal, SearchDocument, Source, SourceSnapshot
from core.tests.support import WorkshopTestCase, md


class PermalinkAndClaimTests(WorkshopTestCase):

    def _article_with_claim(self):
        article = Article.objects.create(slug='claim-sky', title='Claim sky', opening='A claim article.',
                                         provenance='workshop')
        source = Source.objects.create(title='Sky source', url='https://example.org/sky', kind='web',
                                       check_status='opened', license='CC-BY-4.0', attribution='Example')
        editorial.create_published_revision(
            article, self.admin,
            items=[md('The sky is blue during the day. It can look grey at dusk.')],
            citations=[],
            claims=[{
                'block_index': 0, 'text': 'The sky is blue during the day.',
                'citations': [{'source_id': str(source.pk), 'supports': 'States the daytime colour of the sky.'}],
            }],
            summary='Initial claim article.', title='Claim sky', opening='A claim article.',
        )
        article.refresh_from_db()
        return article, article.published.claims.get()

    def test_revision_permalink_is_public_and_canonical(self):
        article, _claim = self._article_with_claim()
        url = reverse('article_revision', args=[article.slug, article.published.number])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'<link rel="canonical" href="{url}">', html=True)
        self.assertContains(response, 'Cite this revision')
        self.assertContains(response, 'CC BY-SA 4.0')

    def test_anonymous_cannot_read_a_draft_permalink(self):
        draft = editorial.ensure_draft(self.article, self.editor)
        response = self.client.get(reverse('article_revision', args=[self.article.slug, draft.number]))
        self.assertEqual(response.status_code, 404)

    def test_claim_resolver_html_and_json(self):
        article, claim = self._article_with_claim()
        url = reverse('claim', args=[claim.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, claim.text)
        self.assertContains(response, 'current revision')
        payload = self.client.get(url + '?format=json').json()
        self.assertEqual(payload['id'], str(claim.pk))
        self.assertEqual(payload['resolution'], 'current')
        self.assertEqual(payload['article']['slug'], article.slug)
        self.assertEqual(payload['citations'][0]['source']['license'], 'CC-BY-4.0')
        self.assertIsNone(payload['valid_to'])

    def test_claim_resolver_marks_a_superseded_occurrence(self):
        article, claim = self._article_with_claim()
        editorial.create_published_revision(
            article, self.admin, items=[md('A corrected sentence without the old claim.')],
            citations=[], summary='Correct the claim.', title='Claim sky', opening='A claim article.',
        )
        payload = self.client.get(reverse('claim', args=[claim.pk]) + '?format=json').json()
        self.assertEqual(payload['resolution'], 'superseded')
        self.assertIsNotNone(payload['valid_to'])
        self.assertNotEqual(payload['current_revision']['id'], payload['revision']['id'])

    def test_claim_api_requires_read_scope_and_returns_etag(self):
        article, claim = self._article_with_claim()
        agent = Agent.objects.create(name='claim-reader', operator=self.admin, kind='agent', scopes=['read'])
        token, _ = agent_auth.create_credential(agent, ['read'])
        url = reverse('api_claim', args=[claim.pk])
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('ETag', response)
        self.assertEqual(response.json()['id'], str(claim.pk))
        cached = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}',
                                 HTTP_IF_NONE_MATCH=response['ETag'])
        self.assertEqual(cached.status_code, 304)


class LicenseTests(WorkshopTestCase):

    def test_default_license_and_event_snapshot_are_recorded(self):
        self.article.refresh_from_db()
        event = self.article.publication_events.get()
        self.assertEqual(self.article.license, 'CC-BY-SA-4.0')
        self.assertEqual(event.license, 'CC-BY-SA-4.0')

    def test_relicensing_does_not_rewrite_history(self):
        self.article.license = 'CC-BY-4.0'
        self.article.save(update_fields=['license'])
        editorial.create_published_revision(
            self.article, self.admin, items=[md('A new sentence for the new license.')],
            citations=[], summary='Publish under a new license.',
        )
        events = list(self.article.publication_events.order_by('sequence'))
        self.assertEqual(events[0].license, 'CC-BY-SA-4.0')
        self.assertEqual(events[1].license, 'CC-BY-4.0')

    def test_article_api_exposes_license_and_citation(self):
        agent = Agent.objects.create(name='license-reader', operator=self.admin, kind='agent', scopes=['read'])
        token, _ = agent_auth.create_credential(agent, ['read'])
        response = self.client.get(
            reverse('api_article', args=[self.article.slug]), HTTP_AUTHORIZATION=f'Bearer {token}',
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['license']['code'], 'CC-BY-SA-4.0')
        self.assertIn('content_hash', payload['published_revision'])
        self.assertIn('citation', payload['published_revision'])
        self.assertIn('/r/1/', payload['published_revision']['permalink'])


class SearchTests(WorkshopTestCase):

    def _publish_searchable(self, text='A uniquequasarword appears in this sentence.', title='Search sky'):
        article = Article.objects.create(slug='search-sky', title=title, opening='Searchable opening.',
                                         provenance='workshop')
        editorial.create_published_revision(
            article, self.admin, items=[md(text)], citations=[], summary='Index this article.',
            title=title, opening='Searchable opening.',
        )
        return article

    def test_search_finds_published_body_and_claim(self):
        article = self._publish_searchable()
        self.assertTrue(SearchDocument.objects.filter(article=article).exists())
        response = self.client.get(reverse('search'), {'q': 'uniquequasarword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search sky')
        self.assertContains(response, 'matched in')

    def test_unpublished_article_is_not_indexed_or_found(self):
        article = Article.objects.create(slug='unpublished', title='Hidden nebula', opening='Not published.',
                                         provenance='workshop')
        self.assertFalse(SearchDocument.objects.filter(article=article).exists())
        response = self.client.get(reverse('search'), {'q': 'nebula'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Hidden nebula')

    def test_search_rejects_fts_operator_input_without_500(self):
        self._publish_searchable()
        for query in ('"', 'AND', 'foo OR bar', '*', '()', 'quasar -word'):
            response = self.client.get(reverse('search'), {'q': query})
            self.assertEqual(response.status_code, 200, query)

    def test_rebuild_and_integrity_commands(self):
        self._publish_searchable()
        out = StringIO()
        call_command('check_search', stdout=out)
        self.assertIn('"ok": true', out.getvalue())
        call_command('rebuild_search', stdout=out)
        self.assertEqual(SearchDocument.objects.count(), Article.objects.filter(published__isnull=False).count())


class IdempotencyAndPreconditionTests(WorkshopTestCase):

    def setUp(self):
        super().setUp()
        configs.ensure_presets()
        self.agent = Agent.objects.create(name='api-writer', operator=self.admin, kind='agent',
                                          scopes=['read', 'research', 'propose', 'review'])
        self.token, _ = agent_auth.create_credential(
            self.agent, ['read', 'research', 'propose', 'review'],
        )
        self.article.refresh_from_db()
        self.snapshot = SourceSnapshot.objects.create(
            url='https://example.org/sky', final_url='https://example.org/sky', domain='example.org',
            fetched_at=timezone.now(), http_status=200, content_type='text/html', sha256='b' * 64,
            byte_count=40, title='Sky source', raw_text='The sky is blue during the day.',
            excerpt='The sky is blue during the day.', source=self.source,
        )
        self.body = {
            'title': 'Test article', 'opening': 'An opening.',
            'blocks': [{'kind': 'markdown', 'data': {'text': 'The sky is blue during the day.'}}],
            'claims': [{
                'block_index': 0, 'text': 'The sky is blue during the day.',
                'citations': [{
                    'source_id': str(self.source.pk), 'quote': 'The sky is blue during the day.',
                    'supports': 'States the colour of the sky.', 'stance': 'supports', 'strength': 'direct',
                }],
            }],
            'rationale': 'Adds one sentence supported by the preserved snapshot.',
            'model': 'declared/propose-model',
        }

    def _post(self, path, body=None, key=None, if_match=None, token=None):
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token or self.token}'}
        if key is not None:
            headers['HTTP_IDEMPOTENCY_KEY'] = key
        if if_match is not None:
            headers['HTTP_IF_MATCH'] = if_match
        return self.client.post(path, data=json.dumps(body or self.body), content_type='application/json', **headers)

    def test_missing_key_is_refused(self):
        response = self._post(reverse('api_submit_proposal', args=[self.article.slug]),
                              if_match=self.article.published.content_hash)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['code'], 'idempotency_key_required')

    def test_missing_if_match_is_refused(self):
        response = self._post(reverse('api_submit_proposal', args=[self.article.slug]), key=uuid.uuid4().hex)
        self.assertEqual(response.status_code, 428)
        self.assertEqual(response.json()['code'], 'precondition_required')

    def test_completed_duplicate_replays_without_a_second_proposal(self):
        path = reverse('api_submit_proposal', args=[self.article.slug])
        key = uuid.uuid4().hex
        if_match = self.article.published.content_hash
        first = self._post(path, key=key, if_match=if_match)
        self.assertEqual(first.status_code, 201, first.content)
        second = self._post(path, key=key, if_match=if_match)
        self.assertEqual(second.status_code, 201)
        self.assertEqual(second['Idempotent-Replayed'], 'true')
        self.assertEqual(Proposal.objects.count(), 1)
        self.assertEqual(IdempotencyRecord.objects.count(), 1)

    def test_same_key_with_different_payload_is_refused(self):
        path = reverse('api_submit_proposal', args=[self.article.slug])
        key = uuid.uuid4().hex
        if_match = self.article.published.content_hash
        self.assertEqual(self._post(path, key=key, if_match=if_match).status_code, 201)
        changed = dict(self.body, rationale='A different rationale that changes the payload.')
        response = self._post(path, body=changed, key=key, if_match=if_match)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()['code'], 'payload_mismatch')

    def test_stale_if_match_returns_current_revision(self):
        path = reverse('api_submit_proposal', args=[self.article.slug])
        old_hash = self.article.published.content_hash
        editorial.create_published_revision(
            self.article, self.admin, items=[md('The article moved on.')], citations=[],
            summary='Move the base revision.',
        )
        response = self._post(path, key=uuid.uuid4().hex, if_match=old_hash)
        self.assertEqual(response.status_code, 412)
        self.assertEqual(response.json()['code'], 'stale_base')
        self.assertIn('ETag', response)

    def test_matching_if_match_succeeds_and_records_base(self):
        response = self._post(
            reverse('api_submit_proposal', args=[self.article.slug]), key=uuid.uuid4().hex,
            if_match=self.article.published.content_hash,
        )
        self.assertEqual(response.status_code, 201, response.content)
        proposal = Proposal.objects.get()
        self.assertEqual(proposal.base_id, self.article.published_id)

    def test_review_and_research_writes_are_idempotent(self):
        proposal = self.propose('A candidate sentence for review.')
        path = reverse('api_review', args=[proposal.pk])
        key = uuid.uuid4().hex
        body = {'role': 'citation', 'verdict': 'concern', 'comment': 'Check the quote.', 'model': 'declared/model'}
        first = self._post(path, body=body, key=key, token=self.token)
        self.assertEqual(first.status_code, 201, first.content)
        second = self._post(path, body=body, key=key, token=self.token)
        self.assertEqual(second.status_code, 201)
        self.assertEqual(second['Idempotent-Replayed'], 'true')
        self.assertEqual(proposal.reviews.count(), 1)

        research = reverse('api_research')
        research_body = {'topic': 'AlterEgo paper', 'question': 'When was it presented?'}
        key = uuid.uuid4().hex
        first = self._post(research, body=research_body, key=key)
        self.assertEqual(first.status_code, 202, first.content)
        second = self._post(research, body=research_body, key=key)
        self.assertEqual(second.status_code, 202)
        self.assertEqual(second['Idempotent-Replayed'], 'true')
        self.assertEqual(Job.objects.count(), 1)
