from django.contrib.auth.models import User
from django.test import TestCase

from core import editorial
from core.models import Article, Source


def md(text):
    return {'block_id': None, 'kind': 'markdown', 'data': {'text': text}}


class WorkshopTestCase(TestCase):
    """An article at r1 with two sources, one staff account and one editor account."""

    def setUp(self):
        self.admin = User.objects.create_user('admin', password='pw-admin-test', is_staff=True, is_superuser=True)
        self.editor = User.objects.create_user('editor', password='pw-editor-test')
        self.source = Source.objects.create(title='Test source', url='https://example.org/source', kind='paper',
                                            check_status='opened')
        self.other_source = Source.objects.create(title='Other source', kind='paper', check_status='metadata')
        self.article = Article.objects.create(slug='test-article', title='Test article', opening='An opening.',
                                              provenance='workshop')
        self.r1 = editorial.create_published_revision(
            self.article, self.admin, items=[md('The sky is blue. It may look grey at dusk.')],
            citations=[], summary='initial', title='Test article', opening='An opening.')

    def draft_with_text(self, text, user=None):
        user = user or self.editor
        draft = editorial.ensure_draft(self.article, user)
        block = draft.blocks.order_by('position').first()
        items = [{'block_id': str(block.block_id), 'kind': 'markdown', 'data': {'text': text}}]
        draft = editorial.save_draft(draft, user, title=draft.title, opening=draft.opening, items=items,
                                     citations=[], expected_version=draft.version)
        return draft

    def propose(self, text, rationale='Clarify the sky claim so readers see the hedge clearly.', user=None):
        draft = self.draft_with_text(text, user=user)
        return editorial.submit_draft(draft, user or self.editor, rationale)

    def review_all(self, proposal, verdicts=None):
        verdicts = verdicts or {'fact_check': 'support', 'skeptic': 'support'}
        for role, verdict in verdicts.items():
            editorial.record_review(proposal, role=role, verdict=verdict, comment='test', origin='test',
                                    declared_model='test')
        return proposal
