from django.urls import reverse

from core import configs, jobs
from core.markup import render_block
from core.models import Job, Proposal

from .support import WorkshopTestCase


class ReadingAndControlsTests(WorkshopTestCase):

    def test_anonymous_reader_sees_article_without_editorial_controls(self):
        response = self.client.get(reverse('article', args=[self.article.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The sky is blue.')
        self.assertNotContains(response, 'staff-bar')
        self.assertNotContains(response, 'Edit draft')
        self.assertNotContains(response, 'Suggest an edit')

    def test_staff_sees_contextual_controls(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('article', args=[self.article.slug]))
        self.assertContains(response, 'staff-bar')
        self.assertContains(response, 'History and revert')

    def test_old_revision_view_is_labelled(self):
        proposal = self.review_all(self.propose('Newer wording for the revision selector test, with a hedge.'))
        self.client.force_login(self.admin)
        from core import editorial
        editorial.decide(proposal, self.admin, 'approve')
        editorial.publish(proposal, self.admin)
        response = self.client.get(reverse('article', args=[self.article.slug]), {'rev': self.r1.number})
        self.assertContains(response, 'not the current revision')

    def test_preview_uses_the_same_renderer_as_reading_view(self):
        self.client.force_login(self.editor)
        block = render_block('markdown', {'text': 'Shared **renderer** check, with a hedge.'})
        import json
        payload = {'title': 'Test article', 'opening': 'An opening.', 'citations': [],
                   'blocks': [{'block_id': None, 'kind': 'markdown', 'data': {'text': 'Shared **renderer** check, with a hedge.'}}]}
        response = self.client.post(reverse('editor_preview', args=[self.article.slug]), data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(str(block), response.json()['html'])

    def test_preview_escapes_title(self):
        self.client.force_login(self.editor)
        import json
        payload = {'title': '<script>alert(1)</script>', 'opening': '', 'citations': [],
                   'blocks': [{'block_id': None, 'kind': 'markdown', 'data': {'text': 'x'}}]}
        response = self.client.post(reverse('editor_preview', args=[self.article.slug]), data=json.dumps(payload),
                                    content_type='application/json')
        self.assertNotIn('<script>alert', response.json()['html'])

    def test_draft_preview_is_hidden_from_anonymous(self):
        self.draft_with_text('Unpublished text.')
        response = self.client.get(reverse('article', args=[self.article.slug]), {'draft': '1'})
        self.assertNotContains(response, 'Unpublished text.')


class PermissionViewTests(WorkshopTestCase):

    def test_anonymous_cannot_open_editor_or_publish(self):
        response = self.client.get(reverse('editor', args=[self.article.slug]))
        self.assertEqual(response.status_code, 302)
        proposal = self.review_all(self.propose('Permission view test wording, with a hedge.'))
        response = self.client.post(reverse('proposal_publish', args=[proposal.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_editor_gets_403_on_staff_actions(self):
        configs.ensure_presets()
        self.client.force_login(self.editor)
        proposal = self.review_all(self.propose('Editor cannot decide this wording, with a hedge.'))
        for name, args in [('proposal_decide', [proposal.pk]), ('proposal_publish', [proposal.pk]),
                           ('workshop_run', ['research']), ('config_default', [configs.default_version('policy').pk])]:
            response = self.client.post(reverse(name, args=args), {'decision': 'approve', 'topic': 'x'})
            self.assertEqual(response.status_code, 403, name)
        response = self.client.post(reverse('article_revert', args=[self.article.slug]),
                                    {'target': str(self.r1.pk), 'expected_current': str(self.r1.pk), 'reason': 'try it'})
        self.assertEqual(response.status_code, 403)

    def test_editor_can_save_and_submit_a_draft(self):
        self.client.force_login(self.editor)
        from core.editorial import ensure_draft
        draft = ensure_draft(self.article, self.editor)
        import json
        payload = {'title': 'Test article', 'opening': 'An opening.', 'version': draft.version,
                   'blocks': [{'block_id': str(draft.blocks.get().block_id), 'kind': 'markdown',
                               'data': {'text': 'An editor sentence, with a hedge that is kept.'}}],
                   'citations': []}
        response = self.client.post(reverse('editor_save', args=[self.article.slug]),
                                    {'payload': json.dumps(payload), 'action': 'submit',
                                     'rationale': 'Editor submits a clearer sentence for review.'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Proposal.objects.filter(article=self.article, origin='human', created_by=self.editor).exists())
        self.article.refresh_from_db()
        self.assertEqual(self.article.published_id, self.r1.pk, 'submitting never publishes')

    def test_staff_publish_through_view_and_stale_refusal_message(self):
        self.client.force_login(self.admin)
        first = self.review_all(self.propose('First view wording, with a hedge kept.'))
        second = self.review_all(self.propose('Second view wording, with a hedge kept.',
                                              rationale='A second competing edit on the same revision.'))
        self.client.post(reverse('proposal_decide', args=[first.pk]), {'decision': 'approve'})
        self.client.post(reverse('proposal_decide', args=[second.pk]), {'decision': 'approve'})
        self.client.post(reverse('proposal_publish', args=[first.pk]))
        response = self.client.post(reverse('proposal_publish', args=[second.pk]), follow=True)
        self.assertContains(response, 'Refused')
        second.refresh_from_db()
        self.assertEqual(second.status, 'approved')

    def test_revert_through_view_creates_revision(self):
        self.client.force_login(self.admin)
        proposal = self.review_all(self.propose('Something that will be reverted through the view.'))
        self.client.post(reverse('proposal_decide', args=[proposal.pk]), {'decision': 'approve'})
        self.client.post(reverse('proposal_publish', args=[proposal.pk]))
        self.article.refresh_from_db()
        r2 = self.article.published
        response = self.client.post(reverse('article_revert', args=[self.article.slug]),
                                    {'target': str(self.r1.pk), 'expected_current': str(r2.pk),
                                     'reason': 'Restore the original wording for the record.'}, follow=True)
        self.assertContains(response, 'Reverted')
        self.article.refresh_from_db()
        self.assertEqual(self.article.published.reverts_id, self.r1.pk)


class WorkshopViewTests(WorkshopTestCase):

    def test_workshop_queues_a_job_and_redirects_to_it(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('workshop_run', args=['research']), {'topic': 'View topic'})
        job = Job.objects.get(label__contains='View topic')
        self.assertRedirects(response, reverse('job_detail', args=[job.pk]))
        self.assertEqual(job.status, 'queued')

    def test_cancel_and_retry_controls_through_views(self):
        self.client.force_login(self.admin)
        job = jobs.enqueue('research_draft', user=self.admin, runner_name='simulated', input={'topic': 'Cancel me'},
                           label='Cancel me')
        self.client.post(reverse('job_cancel', args=[job.pk]))
        job.refresh_from_db()
        self.assertEqual(job.status, 'cancelled')
        response = self.client.post(reverse('job_retry', args=[job.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Job.objects.filter(retry_of=job).count(), 1)

    def test_config_edit_creates_new_version_and_keeps_old(self):
        self.client.force_login(self.admin)
        configs.ensure_presets()
        version = configs.default_version('limits')
        original = dict(version.data)
        data = {'max_model_calls': '12', 'job_timeout_seconds': '600', 'description': 'Tuned for a small panel.'}
        response = self.client.post(reverse('config_edit', args=[version.pk]), data)
        self.assertEqual(response.status_code, 302)
        version.refresh_from_db()
        self.assertEqual(version.data, original, 'the old version is not overwritten')
        from core.models import ConfigVersion
        newest = ConfigVersion.objects.filter(kind='limits', family=version.family).order_by('-version').first()
        self.assertEqual(newest.version, version.version + 1)
        self.assertEqual(newest.data['max_model_calls'], 12)

    def test_config_form_rejects_out_of_range_values(self):
        self.client.force_login(self.admin)
        configs.ensure_presets()
        version = configs.default_version('limits')
        response = self.client.post(reverse('config_edit', args=[version.pk]),
                                    {'max_model_calls': '999', 'job_timeout_seconds': '600'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nothing was saved')

    def test_library_search_filters(self):
        response = self.client.get(reverse('library'), {'q': 'Test'})
        self.assertContains(response, 'Test article')
        response = self.client.get(reverse('library'), {'q': 'nomatchhere'})
        self.assertContains(response, 'No articles match')
