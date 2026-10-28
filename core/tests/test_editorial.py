from core import editorial
from core.editorial import ConflictError, EditorialError, PermissionDeniedError, StaleProposalError
from core.models import AuditEvent, Proposal, Revision

from .support import WorkshopTestCase, md


class PublicationAndRevertTests(WorkshopTestCase):

    def test_publish_supersedes_previous_and_keeps_history(self):
        proposal = self.review_all(self.propose('The sky is blue. It may look grey at dusk, depending on haze.'))
        editorial.decide(proposal, self.admin, 'approve')
        published = editorial.publish(proposal, self.admin)

        self.article.refresh_from_db()
        self.r1.refresh_from_db()
        self.assertEqual(self.article.published_id, published.pk)
        self.assertEqual(published.state, 'published')
        self.assertEqual(self.r1.state, 'superseded')
        self.assertIn('haze', published.blocks.get().data['text'])
        self.assertIn('may look grey', self.r1.blocks.get().data['text'])
        self.assertTrue(AuditEvent.objects.filter(article=self.article, action='published', revision=published).exists())

    def test_block_ids_survive_into_published_revision(self):
        draft = self.draft_with_text('Edited sky sentence.')
        block_id = draft.blocks.get().block_id
        proposal = self.review_all(editorial.submit_draft(draft, self.editor, 'Edit the sky sentence for clarity.'))
        editorial.decide(proposal, self.admin, 'approve')
        published = editorial.publish(proposal, self.admin)
        self.assertEqual(published.blocks.get().block_id, block_id)

    def test_revert_creates_new_revision_and_leaves_history(self):
        proposal = self.review_all(self.propose('A completely different claim for the record, with a hedge.'))
        editorial.decide(proposal, self.admin, 'approve')
        r2 = editorial.publish(proposal, self.admin)

        r3 = editorial.revert(self.article, self.r1, self.admin, reason='Restore the original wording.',
                              expected_current_id=r2.pk)

        self.article.refresh_from_db()
        self.assertEqual(self.article.published_id, r3.pk)
        self.assertEqual(r3.number, r2.number + 1)
        self.assertEqual(r3.reverts_id, self.r1.pk)
        self.assertEqual(r3.blocks.get().data['text'], self.r1.blocks.get().data['text'])
        self.r1.refresh_from_db(); r2.refresh_from_db()
        self.assertEqual(self.r1.state, 'superseded')
        self.assertEqual(r2.state, 'superseded')
        self.assertEqual(Revision.objects.filter(article=self.article).count(), 3)
        event = AuditEvent.objects.get(article=self.article, action='reverted')
        self.assertEqual(event.reason, 'Restore the original wording.')
        self.assertEqual(event.actor, self.admin)
        self.assertEqual(event.revision, r3)

    def test_revert_refused_when_current_revision_moved(self):
        proposal = self.review_all(self.propose('Another wording that the reviewers saw, with a hedge.'))
        editorial.decide(proposal, self.admin, 'approve')
        r2 = editorial.publish(proposal, self.admin)
        before = Revision.objects.count()
        with self.assertRaises(StaleProposalError):
            editorial.revert(self.article, self.r1, self.admin, reason='Restore old text.',
                             expected_current_id=self.r1.pk)
        self.assertEqual(Revision.objects.count(), before)
        self.article.refresh_from_db()
        self.assertEqual(self.article.published_id, r2.pk)
        self.assertTrue(AuditEvent.objects.filter(action='revert_refused_stale').exists())

    def test_stale_proposal_publication_is_refused(self):
        first = self.review_all(self.propose('First proposed wording, which lands first.'))
        second = self.review_all(self.propose('Second proposed wording, based on the same revision.',
                                              rationale='A competing edit based on the same published revision.'))
        editorial.decide(first, self.admin, 'approve')
        editorial.decide(second, self.admin, 'approve')
        editorial.publish(first, self.admin)

        with self.assertRaises(StaleProposalError) as ctx:
            editorial.publish(second, self.admin)
        self.assertIn('now at', str(ctx.exception))
        second.refresh_from_db()
        self.assertEqual(second.status, 'approved', 'a refused publication must not change proposal status')
        self.assertIsNone(second.result_id)
        self.assertTrue(AuditEvent.objects.filter(action='publish_refused_stale', proposal=second).exists())
        self.assertTrue(second.is_stale)

    def test_published_revision_cannot_be_edited_through_services(self):
        with self.assertRaises(EditorialError):
            editorial.save_draft(self.r1, self.admin, title='x', opening='', items=[md('x')], citations=[],
                                 expected_version=self.r1.version)

    def test_draft_save_with_stale_version_is_a_conflict(self):
        draft = editorial.ensure_draft(self.article, self.editor)
        items = [{'block_id': None, 'kind': 'markdown', 'data': {'text': 'First save.'}}]
        editorial.save_draft(draft, self.editor, title=draft.title, opening='', items=items, citations=[],
                             expected_version=draft.version)
        with self.assertRaises(ConflictError):
            editorial.save_draft(draft, self.editor, title=draft.title, opening='', items=items, citations=[],
                                 expected_version=draft.version)

    def test_no_change_proposal_is_refused(self):
        draft = editorial.ensure_draft(self.article, self.editor)
        with self.assertRaises(Exception) as ctx:
            editorial.submit_draft(draft, self.editor, 'Changing nothing but claiming it helps readers.')
        self.assertIn('no changes', str(ctx.exception).lower())


class DecisionRuleTests(WorkshopTestCase):

    def test_editor_cannot_decide_publish_or_revert(self):
        proposal = self.review_all(self.propose('Wording for the permissions test, with a hedge.'))
        with self.assertRaises(PermissionDeniedError):
            editorial.decide(proposal, self.editor, 'approve')
        editorial.decide(proposal, self.admin, 'approve')
        with self.assertRaises(PermissionDeniedError):
            editorial.publish(proposal, self.editor)
        with self.assertRaises(PermissionDeniedError):
            editorial.revert(self.article, self.r1, self.editor, reason='Try to restore.', expected_current_id=self.r1.pk)

    def test_anonymous_cannot_draft(self):
        from django.contrib.auth.models import AnonymousUser
        with self.assertRaises(PermissionDeniedError):
            editorial.ensure_draft(self.article, AnonymousUser())

    def test_approval_needs_minimum_reviews(self):
        proposal = self.propose('Wording that has no reviews yet, with a hedge.')
        with self.assertRaisesRegex(EditorialError, 'at least 2 reviews'):
            editorial.decide(proposal, self.admin, 'approve')

    def test_policy_blocks_approval_while_reviewer_objects(self):
        proposal = self.review_all(self.propose('Wording with an objection on record, with a hedge.'),
                                   {'fact_check': 'object', 'skeptic': 'support'})
        with self.assertRaisesRegex(EditorialError, 'objects'):
            editorial.decide(proposal, self.admin, 'approve')
        editorial.decide(proposal, self.admin, 'reject', 'Blocking objection on record.')
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'rejected')

    def test_reject_requires_reason(self):
        proposal = self.review_all(self.propose('Wording that will be rejected, with a hedge.'))
        with self.assertRaises(Exception):
            editorial.decide(proposal, self.admin, 'reject', '')

    def test_evaluation_proposals_are_never_publishable(self):
        draft = self.draft_with_text('Evaluation-only candidate text, with a hedge.')
        candidate = editorial.create_candidate(
            self.article, title=draft.title, opening=draft.opening,
            items=[{'block_id': str(draft.blocks.get().block_id), 'kind': 'markdown', 'data': {'text': 'Evaluation-only candidate text, with a hedge.'}}],
            citations=[], origin='evaluation')
        proposal = editorial.open_proposal(candidate, rationale='Evaluation candidate for a test case run.',
                                           origin='evaluation')
        self.review_all(proposal)
        with self.assertRaises(EditorialError):
            editorial.decide(proposal, self.admin, 'approve')
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'pending')

    def test_repeat_of_rejected_candidate_is_flagged(self):
        first = self.propose('The same repeated text, with a hedge.')
        editorial.decide(first, self.admin, 'reject', 'Not supported by the sources.')
        second = self.propose('The same repeated text, with a hedge.', rationale='Trying again with identical text.')
        self.assertEqual(second.repeat_of_id, first.pk)


class ValidationTests(WorkshopTestCase):

    def test_source_url_must_be_http(self):
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            editorial.create_source(title='Bad', url='javascript:alert(1)', user=self.admin)

    def test_citation_needs_registered_source_and_note(self):
        from django.core.exceptions import ValidationError
        draft = editorial.ensure_draft(self.article, self.editor)
        block_id = str(draft.blocks.get().block_id)
        items = [{'block_id': block_id, 'kind': 'markdown', 'data': {'text': 'Cited sentence.'}}]
        with self.assertRaises(ValidationError):
            editorial.save_draft(draft, self.editor, title=draft.title, opening='', items=items,
                                 citations=[{'block_id': block_id, 'source_id': 'nope', 'supports': 'x'}],
                                 expected_version=draft.version)
        with self.assertRaises(ValidationError):
            editorial.save_draft(draft, self.editor, title=draft.title, opening='', items=items,
                                 citations=[{'block_id': block_id, 'source_id': str(self.source.pk), 'supports': ''}],
                                 expected_version=draft.version)
