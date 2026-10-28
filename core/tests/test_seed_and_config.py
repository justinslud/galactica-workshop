from django.core.management import call_command
from io import StringIO

from core import configs, seeding
from core.models import Article, EvalCase, Job, Proposal, Revision, Source

from .support import WorkshopTestCase


class SeedTests(WorkshopTestCase):

    def counts(self):
        return {
            'articles': Article.objects.count(), 'revisions': Revision.objects.count(),
            'proposals': Proposal.objects.count(), 'jobs': Job.objects.count(),
            'cases': EvalCase.objects.count(), 'sources': Source.objects.count(),
            'configs': configs.ConfigVersion.objects.count() if hasattr(configs, 'ConfigVersion') else 0,
        }

    def test_seed_twice_does_not_duplicate(self):
        from core.models import ConfigVersion
        logs = []
        seeding.seed(log=logs.append)
        first = self.counts()
        first_config = ConfigVersion.objects.count()
        seeding.seed(log=logs.append)
        second = self.counts()
        self.assertEqual(first, second)
        self.assertEqual(ConfigVersion.objects.count(), first_config)
        self.assertTrue(any('already present' in line for line in logs))

    def test_seeded_demo_covers_every_workflow_state(self):
        seeding.seed(log=lambda *_: None)
        statuses = set(Job.objects.values_list('status', flat=True))
        self.assertTrue({'succeeded', 'failed', 'cancelled', 'interrupted', 'queued'} <= statuses, statuses)
        self.assertTrue(Proposal.objects.filter(status='rejected').exists())
        self.assertTrue(Proposal.objects.filter(status='pending').exclude(origin='evaluation').exists())
        self.assertTrue(Revision.objects.filter(state='published').exists())
        demo = Article.objects.get(slug='subvocal-interfaces')
        self.assertEqual(demo.provenance, 'demonstration')
        self.assertGreaterEqual(demo.revisions.count(), 2)
        self.assertGreaterEqual(len(EvalCase.objects.all()), 6)

    def test_demo_articles_are_labelled_and_long_enough(self):
        seeding.seed(log=lambda *_: None)
        import re
        for slug in ['subvocal-interfaces', 'quadratic-funding', 'encyclopedia-galactica']:
            article = Article.objects.get(slug=slug)
            text = ' '.join(b.data.get('text', '') for b in article.published.blocks.all() if b.kind == 'markdown')
            words = len(re.findall(r'\w+', text))
            self.assertGreaterEqual(words, 450, slug)
            self.assertEqual(article.provenance, 'demonstration')

    def test_seeded_stale_proposal_is_detected(self):
        seeding.seed(log=lambda *_: None)
        stale = Proposal.objects.filter(article__slug='quadratic-funding', status='pending').exclude(origin='evaluation')
        self.assertTrue(any(p.is_stale for p in stale))

    def test_presets_are_idempotent_and_provisional(self):
        n = configs.ensure_presets()
        self.assertEqual(configs.ensure_presets(), 0)
        for kind in configs.PRESETS:
            default = configs.default_version(kind)
            self.assertIsNotNone(default)
            self.assertTrue(default.provisional)

    def test_panel_respects_size_and_enabled_roles(self):
        data = dict(configs.DEFAULTS['reviewers'])
        data['panel_size'] = 2
        roles = configs.panel_roles(data)
        self.assertEqual([r['key'] for r in roles], ['fact_check', 'citation'])
        data['citation__enabled'] = False
        # Panel size 2 caps the remaining enabled roles in fixed order.
        self.assertEqual([r['key'] for r in configs.panel_roles(data)], ['fact_check', 'readability'])

    def test_simulated_runner_is_default_and_labelled(self):
        configs.ensure_presets()
        self.assertEqual(configs.default_version('runner').data['runner'], 'simulated')
        self.assertEqual(configs.default_version('runner').data['model'], configs.SIMULATED_MODEL)
