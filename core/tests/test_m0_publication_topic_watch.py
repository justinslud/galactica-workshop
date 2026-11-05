"""M0 regression tests: publication events, topics, contributor bylines, and watchlist.

These tests pin the public contract of the M0 slice. They deliberately assert
observable behaviour (rows written, pages rendered, redirects, timestamps) rather
than private helpers, except where the contract names a model field explicitly.
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone

from core import editorial
from core.editorial import PermissionDeniedError, StaleProposalError
from core.models import Article, PublicationEvent, Topic, Watch

from .support import WorkshopTestCase, md


class M0TestBase(WorkshopTestCase):

    def make_second_article(self):
        article = Article.objects.create(
            slug='second-article', title='Second article', opening='A second opening.', provenance='workshop',
        )
        revision = editorial.create_published_revision(
            article, self.admin, items=[md('Second body text.')], citations=[], summary='initial',
            title='Second article', opening='A second opening.',
        )
        return article, revision

    def approve_and_publish(self, text):
        proposal = self.review_all(self.propose(text))
        editorial.decide(proposal, self.admin, 'approve')
        return editorial.publish(proposal, self.admin)


class PublicationEventTests(M0TestBase):

    def test_initial_published_revision_records_one_publication_event(self):
        events = PublicationEvent.objects.filter(article=self.article)

        self.assertEqual(events.count(), 1)
        event = events.get()
        self.assertEqual(event.sequence, 1)
        self.assertEqual(event.revision_id, self.r1.pk)
        self.assertIsNone(event.previous_revision)
        self.assertIsNotNone(event.published_at)

    def test_publish_appends_second_event_with_previous_revision_and_content_hash(self):
        published = self.approve_and_publish('The sky is blue. It may look grey at dusk, depending on haze.')

        events = list(PublicationEvent.objects.filter(article=self.article).order_by('sequence'))
        self.assertEqual(len(events), 2)
        initial, second = events
        self.assertEqual(initial.sequence, 1)
        self.assertEqual(initial.revision_id, self.r1.pk)

        self.assertEqual(second.sequence, 2)
        self.assertEqual(second.previous_revision_id, self.r1.pk)
        self.assertEqual(second.revision_id, published.pk)
        self.assertEqual(second.kind, 'publish')
        self.assertEqual(second.published_by, self.admin)
        self.assertEqual(second.content_hash, published.content_hash)

    def test_publishing_does_not_rewrite_the_initial_event(self):
        initial = PublicationEvent.objects.get(article=self.article, sequence=1)
        snapshot = {
            'revision_id': initial.revision_id,
            'previous_revision_id': initial.previous_revision_id,
            'published_by_id': initial.published_by_id,
            'published_at': initial.published_at,
            'content_hash': initial.content_hash,
            'kind': initial.kind,
        }

        self.approve_and_publish('The sky is blue. It may look grey at dusk, depending on haze.')

        initial.refresh_from_db()
        self.assertEqual(initial.revision_id, snapshot['revision_id'])
        self.assertEqual(initial.previous_revision_id, snapshot['previous_revision_id'])
        self.assertEqual(initial.published_by_id, snapshot['published_by_id'])
        self.assertEqual(initial.published_at, snapshot['published_at'])
        self.assertEqual(initial.content_hash, snapshot['content_hash'])
        self.assertEqual(initial.kind, snapshot['kind'])

    def test_stale_publish_creates_no_event_and_keeps_proposal_approved(self):
        first = self.review_all(self.propose('First change to the sky sentence, kept for later.'))
        editorial.decide(first, self.admin, 'approve')

        second = self.review_all(self.propose('Second change to the sky sentence, published first.'))
        editorial.decide(second, self.admin, 'approve')
        editorial.publish(second, self.admin)

        count_before = PublicationEvent.objects.filter(article=self.article).count()
        first.refresh_from_db()
        self.assertEqual(first.status, 'approved')

        with self.assertRaises(StaleProposalError):
            editorial.publish(first, self.admin)

        self.assertEqual(PublicationEvent.objects.filter(article=self.article).count(), count_before)
        first.refresh_from_db()
        self.assertEqual(first.status, 'approved')

    def test_revert_appends_revert_event_pointing_at_new_revision(self):
        r2 = self.approve_and_publish('A different sky sentence for the revert test, with a hedge.')

        r3 = editorial.revert(
            self.article, self.r1, self.admin, reason='Restore the original wording.',
            expected_current_id=r2.pk,
        )

        events = list(PublicationEvent.objects.filter(article=self.article).order_by('sequence'))
        self.assertEqual(len(events), 3)
        self.assertEqual([event.sequence for event in events], [1, 2, 3])
        revert_event = events[-1]
        self.assertEqual(revert_event.kind, 'revert')
        self.assertEqual(revert_event.previous_revision_id, r2.pk)
        self.assertEqual(revert_event.revision_id, r3.pk)

    def test_non_staff_cannot_publish_and_no_event_is_written(self):
        proposal = self.review_all(self.propose('A change the editor must not publish alone.'))
        editorial.decide(proposal, self.admin, 'approve')
        count_before = PublicationEvent.objects.filter(article=self.article).count()

        with self.assertRaises(PermissionDeniedError):
            editorial.publish(proposal, self.editor)

        self.assertEqual(PublicationEvent.objects.filter(article=self.article).count(), count_before)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'approved')


class ContributorBylineTests(M0TestBase):

    def test_article_page_shows_byline_and_links_to_contributor_page(self):
        response = self.client.get(reverse('article', args=[self.article.slug]))

        self.assertEqual(response.status_code, 200)
        # The byline is link text ("Written by <a>admin</a>"), so assert the rendered pieces.
        self.assertContains(response, 'Written by')
        self.assertContains(response, '/contributors/admin/')
        self.assertContains(response, '>admin</a>')

    def test_contributor_page_lists_public_revision_and_article_without_email(self):
        self.admin.email = 'admin@example.org'
        self.admin.save(update_fields=['email'])

        response = self.client.get(reverse('contributor', args=['admin']))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test article')
        self.assertContains(response, self.r1.label)
        self.assertNotContains(response, 'admin@example.org')

    def test_contributor_with_no_public_work_is_404(self):
        User.objects.create_user('quietcontributor', password='pw-quiet-test')

        response = self.client.get(reverse('contributor', args=['quietcontributor']))

        self.assertEqual(response.status_code, 404)


class TopicPageTests(M0TestBase):

    def setUp(self):
        super().setUp()
        self.topic = Topic.objects.create(
            slug='sky', title='Sky', scope_statement='What the sky is and is not.',
            created_by=self.admin,
        )
        self.empty_topic = Topic.objects.create(
            slug='empty-topic', title='Empty topic', scope_statement='Nothing published here yet.',
            created_by=self.admin,
        )
        self.article.topic = self.topic
        self.article.save(update_fields=['topic'])

    def test_topic_index_lists_topics(self):
        response = self.client.get(reverse('topics'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sky')
        self.assertContains(response, 'Empty topic')

    def test_topic_page_lists_only_published_articles(self):
        Article.objects.create(slug='unpublished-article', title='Unpublished article', topic=self.topic,
                               provenance='workshop')

        response = self.client.get(reverse('topic', args=[self.topic.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test article')
        self.assertNotContains(response, 'Unpublished article')

    def test_topic_page_with_no_published_articles_still_renders(self):
        response = self.client.get(reverse('topic', args=[self.empty_topic.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Empty topic')

    def test_article_page_links_its_topic(self):
        response = self.client.get(reverse('article', args=[self.article.slug]))

        self.assertContains(response, reverse('topic', args=[self.topic.slug]))


class WatchlistTests(M0TestBase):

    def test_anonymous_watch_post_redirects_to_login_and_creates_no_watch(self):
        response = self.client.post(reverse('article_watch', args=[self.article.slug]))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])
        self.assertEqual(Watch.objects.count(), 0)

    def test_logged_in_watch_toggle_creates_then_removes_watch(self):
        self.client.force_login(self.editor)

        self.client.post(reverse('article_watch', args=[self.article.slug]))
        self.assertTrue(Watch.objects.filter(user=self.editor, article=self.article).exists())

        self.client.post(reverse('article_watch', args=[self.article.slug]))
        self.assertFalse(Watch.objects.filter(user=self.editor, article=self.article).exists())

    def test_watchlist_shows_only_the_readers_own_rows(self):
        second_article, _ = self.make_second_article()
        Watch.objects.create(user=self.admin, article=self.article)
        Watch.objects.create(user=self.editor, article=second_article)

        self.client.force_login(self.editor)
        response = self.client.get(reverse('watchlist'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Second article')
        self.assertNotContains(response, 'Test article')

    def test_publication_after_last_seen_at_shows_a_new_count(self):
        watch = Watch.objects.create(user=self.editor, article=self.article)
        # Mark the setUp initial publication as seen, then publish exactly one new revision.
        seen_at = timezone.now()
        watch.last_seen_at = seen_at
        watch.save(update_fields=['last_seen_at'])

        self.approve_and_publish('A newer sky sentence so the watch has something new to report.')

        self.client.force_login(self.editor)
        response = self.client.get(reverse('watchlist'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1 new')
        watch.refresh_from_db()
        self.assertEqual(watch.last_seen_at, seen_at)

    def test_watchlist_seen_advances_last_seen_at(self):
        watch = Watch.objects.create(user=self.editor, article=self.article)
        before = timezone.now() - timedelta(days=1)
        watch.last_seen_at = before
        watch.save(update_fields=['last_seen_at'])

        self.client.force_login(self.editor)
        response = self.client.post(reverse('watchlist_seen'))

        self.assertEqual(response.status_code, 302)
        watch.refresh_from_db()
        self.assertIsNotNone(watch.last_seen_at)
        self.assertGreater(watch.last_seen_at, before)

    def test_watchlist_requires_login(self):
        response = self.client.get(reverse('watchlist'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_watchlist_page_contains_explicit_no_email_copy(self):
        self.client.force_login(self.editor)

        response = self.client.get(reverse('watchlist'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('no email', response.content.decode().lower())

    def test_watch_is_unique_per_user_and_article(self):
        Watch.objects.create(user=self.editor, article=self.article)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Watch.objects.create(user=self.editor, article=self.article)
