"""Deterministic capability, state and quota rules plus the human review queue."""
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from core import authorization, editorial
from core.authorization import CAP_DECIDE, CAP_PUBLISH, CAP_PROPOSE, CAP_REVERT, CAP_VIEW_QUEUE
from core.models import Agent, ContributorProfile, Proposal, Review

from .support import WorkshopTestCase


class AuthorizationDecisionTests(WorkshopTestCase):

    def new_user(self, username='reviewer'):
        return User.objects.create_user(username, password='pw-reviewer-test')

    def test_default_profiles_are_standard_and_staff_are_steward(self):
        self.assertEqual(authorization.profile_for(self.editor).trust_level, 'standard')
        self.assertEqual(authorization.profile_for(self.admin).trust_level, 'steward')

    def test_new_account_cannot_review_or_view_queue(self):
        new = self.new_user()
        profile = authorization.profile_for(new)
        profile.trust_level = 'new'
        profile.save(update_fields=['trust_level'])
        proposal = self.propose('A proposal for the new-account capability test, with a hedge.')

        review = authorization.can(new, 'review', proposal=proposal, role='fact_check')
        queue = authorization.can(new, CAP_VIEW_QUEUE)

        self.assertFalse(review.allowed)
        self.assertEqual(review.code, 'missing_capability')
        self.assertFalse(queue.allowed)
        self.assertEqual(queue.code, 'missing_capability')

    def test_standard_reviewer_can_review_but_not_decide(self):
        reviewer = self.new_user()
        proposal = self.propose('A proposal for the standard reviewer capability test, with a hedge.')
        review = authorization.can(reviewer, 'review', proposal=proposal, role='fact_check')
        decide = authorization.can(reviewer, 'approve', proposal=proposal)
        publish = authorization.can(reviewer, CAP_PUBLISH, proposal=proposal)

        self.assertTrue(review.allowed, review.message)
        self.assertFalse(decide.allowed)
        self.assertEqual(decide.code, 'missing_capability')
        self.assertFalse(publish.allowed)
        self.assertEqual(publish.code, 'missing_capability')

    def test_self_review_and_self_decision_are_blocked(self):
        proposal = self.propose('A proposal for the self-review guard test, with a hedge.')

        self_review = authorization.can(self.editor, 'review', proposal=proposal, role='fact_check')
        self.assertEqual(self_review.code, 'self_review')

        # A staff author can write a human proposal; a different steward must decide it.
        author = User.objects.create_user('steward2', password='pw-steward-test', is_staff=True)
        draft = editorial.ensure_draft(self.article, author)
        block = draft.blocks.order_by('position').first()
        draft = editorial.save_draft(
            draft, author, title=draft.title, opening=draft.opening,
            items=[{'block_id': str(block.block_id), 'kind': 'markdown', 'data': {'text': 'A staff-authored sentence, with a hedge.'}}],
            citations=[], expected_version=draft.version,
        )
        staff_proposal = editorial.submit_draft(draft, author, 'A staff-authored proposal for the self-decision test.')
        approve = authorization.can(author, 'approve', proposal=staff_proposal)
        self.assertFalse(approve.allowed)
        self.assertEqual(approve.code, 'self_decision')

    def test_publish_guard_blocks_self_publication_and_requires_approval(self):
        proposal = self.propose('A proposal for the publish guard test, with a hedge.')
        self.review_all(proposal, {'fact_check': 'support', 'skeptic': 'support', 'readability': 'support'})
        editorial.decide(proposal, self.admin, 'approve')
        proposal.refresh_from_db()
        allowed = authorization.can(self.admin, CAP_PUBLISH, proposal=proposal)
        self.assertTrue(allowed.allowed, allowed.message)

        second = self.propose('A second proposal for the stale state test, with a hedge.')
        self.review_all(second, {'fact_check': 'support', 'skeptic': 'support', 'readability': 'support'})
        editorial.decide(second, self.admin, 'approve')
        second.refresh_from_db()
        # Simulate a staff-authored human proposal; the operator must not publish it.
        second.created_by = self.admin
        second.save(update_fields=['created_by'])
        blocked = authorization.can(self.admin, CAP_PUBLISH, proposal=second)
        self.assertEqual(blocked.code, 'self_decision')

    def test_agent_cannot_decide_or_publish(self):
        agent = Agent.objects.create(name='review-agent', operator=self.admin, scopes=['review'])
        proposal = self.propose('A proposal for the agent publish guard, with a hedge.')
        decision = authorization.can(None, 'publish', proposal=proposal, agent=agent)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.code, 'missing_capability')

    def test_workflow_state_is_derived_from_reviews(self):
        proposal = self.propose('A proposal for the workflow state test, with a hedge.')
        self.assertEqual(authorization.proposal_state(proposal), 'submitted')
        self.review_all(proposal, {'fact_check': 'support', 'skeptic': 'support'})
        proposal.refresh_from_db()
        self.assertEqual(authorization.proposal_state(proposal), 'under_review')

    def test_draft_edit_is_limited_to_author_or_steward(self):
        other = self.new_user('other-editor')
        draft = editorial.ensure_draft(self.article, self.editor)
        denied = authorization.can(other, 'edit_draft', draft)
        allowed = authorization.can(self.admin, 'edit_draft', draft)
        self.assertEqual(denied.code, 'not_author')
        self.assertTrue(allowed.allowed, allowed.message)

    def test_quota_blocks_second_new_account_proposal(self):
        newcomer = self.new_user('newcomer')
        profile = authorization.profile_for(newcomer)
        profile.trust_level = 'new'
        profile.save(update_fields=['trust_level'])

        self.propose('First proposal from the new account, with a hedge.', user=newcomer)
        with self.assertRaisesRegex(editorial.EditorialError, 'limit'):
            self.propose('Second proposal from the new account, with a hedge.', user=newcomer)

    def test_revert_requires_a_steward(self):
        self.assertFalse(authorization.can(self.editor, CAP_REVERT).allowed)
        self.assertTrue(authorization.can(self.admin, CAP_REVERT).allowed)


class HumanReviewAndDashboardTests(WorkshopTestCase):

    def new_user(self, username='reviewer'):
        return User.objects.create_user(username, password='pw-reviewer-test')

    def test_human_review_is_recorded_and_moves_state_to_under_review(self):
        proposal = self.propose('A proposal for the human review form test, with a hedge.')
        reviewer = self.new_user()
        self.client.force_login(reviewer)

        response = self.client.post(
            reverse('proposal_review', args=[proposal.pk]),
            {'role': 'fact_check', 'verdict': 'support', 'comment': 'Checked the base and candidate.'},
        )

        self.assertEqual(response.status_code, 302)
        review = Review.objects.get(proposal=proposal, role='fact_check')
        self.assertEqual(review.reviewer, reviewer)
        self.assertEqual(review.origin, 'human')
        proposal.refresh_from_db()
        self.assertEqual(authorization.proposal_state(proposal), 'under_review')

    def test_author_cannot_review_own_proposal_through_the_form(self):
        proposal = self.propose('A proposal for the author self-review test, with a hedge.')
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse('proposal_review', args=[proposal.pk]),
            {'role': 'fact_check', 'verdict': 'support', 'comment': 'I wrote this.'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Review.objects.filter(proposal=proposal, role='fact_check').exists())

    def test_review_dashboard_requires_review_capability(self):
        anonymous = self.client.get(reverse('review_dashboard'))
        self.assertEqual(anonymous.status_code, 302)
        self.assertIn('/accounts/login/', anonymous['Location'])

        newcomer = self.new_user('new-dashboard-user')
        profile = authorization.profile_for(newcomer)
        profile.trust_level = 'new'
        profile.save(update_fields=['trust_level'])
        self.client.force_login(newcomer)
        self.assertEqual(self.client.get(reverse('review_dashboard')).status_code, 403)

    def test_review_dashboard_shows_open_proposals_and_coverage(self):
        proposal = self.propose('A proposal for the dashboard coverage test, with a hedge.')
        self.client.force_login(self.editor)
        response = self.client.get(reverse('review_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
        row = response.context['rows'][0]
        self.assertEqual(row.state, 'submitted')
        self.assertIn('Fact checker', row.missing)

    def test_standard_reviewer_sees_form_but_not_decision_controls(self):
        proposal = self.propose('A proposal for the review form visibility test, with a hedge.')
        reviewer = self.new_user()
        self.client.force_login(reviewer)
        response = self.client.get(reverse('proposal', args=[proposal.pk]))

        self.assertContains(response, 'Record a human review')
        self.assertNotContains(response, 'Approve</button>')
        self.assertNotContains(response, 'Publish</button>')

    def test_steward_sees_decision_controls(self):
        proposal = self.propose('A proposal for the steward decision visibility test, with a hedge.')
        self.client.force_login(self.admin)
        response = self.client.get(reverse('proposal', args=[proposal.pk]))

        self.assertContains(response, 'Approve</button>')
        self.assertContains(response, 'Decision')

    def test_approved_proposal_keeps_publish_control_after_decision_is_closed(self):
        proposal = self.propose('A proposal for the approved publish-control test, with a hedge.')
        self.review_all(proposal, {'fact_check': 'support', 'skeptic': 'support', 'readability': 'support'})
        editorial.decide(proposal, self.admin, 'approve')
        self.client.force_login(self.admin)

        response = self.client.get(reverse('proposal', args=[proposal.pk]))

        self.assertContains(response, 'Publish</button>')
        self.assertNotContains(response, 'Approve</button>')
