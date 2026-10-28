from datetime import timedelta
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from core import configs, editorial, jobs, reviewing
from core.models import EvalResult, Job, JobEvent, Proposal

from .support import WorkshopTestCase


class JobTransitionTests(WorkshopTestCase):

    def enqueue_research(self, topic='Test topic'):
        return jobs.enqueue('research_draft', user=self.admin, runner_name='simulated',
                            input={'topic': topic}, label=f'Research {topic}')

    def test_queued_job_runs_to_succeeded_with_outputs(self):
        job = self.enqueue_research('Sample topic')
        self.assertEqual(job.status, 'queued')
        job = jobs.run_now(job)
        self.assertEqual(job.status, 'succeeded')
        self.assertIsNotNone(job.started_at)
        self.assertIsNotNone(job.finished_at)
        self.assertIn('article', job.output)
        self.assertTrue(job.article.revisions.filter(state='draft').exists())
        self.assertEqual(job.article.provenance, 'simulated')
        self.assertEqual(job.usage, {}, 'simulated runs record no measured usage')
        self.assertTrue(job.events.filter(message__startswith='Finished: succeeded').exists())

    def test_claim_is_exclusive(self):
        a = self.enqueue_research('A')
        b = self.enqueue_research('B')
        first = jobs.claim_next('worker-1')
        second = jobs.claim_next('worker-2')
        third = jobs.claim_next('worker-3')
        self.assertEqual({first.pk, second.pk}, {a.pk, b.pk})
        self.assertIsNone(third)
        self.assertEqual(Job.objects.filter(status='running').count(), 2)

    def test_cancel_queued_job_is_immediate(self):
        job = self.enqueue_research()
        jobs.request_cancel(job)
        job.refresh_from_db()
        self.assertEqual(job.status, 'cancelled')
        with self.assertRaises(Exception):
            jobs.request_cancel(job)

    def test_cancel_running_job_stops_at_next_check(self):
        job = jobs.enqueue('run_eval', user=self.admin, runner_name='simulated', input={'case_ids': []},
                           label='Cancel me')
        claimed = jobs.claim_next('worker-x')
        self.assertEqual(claimed.pk, job.pk)
        jobs.request_cancel(job)
        job.refresh_from_db()
        self.assertTrue(job.cancel_requested)
        jobs.execute(claimed)
        job.refresh_from_db()
        self.assertEqual(job.status, 'cancelled')
        self.assertEqual(job.eval_results.count(), 0)

    def test_stale_heartbeat_marks_interrupted_not_silently_retried(self):
        job = self.enqueue_research()
        jobs.claim_next('worker-dead')
        old = timezone.now() - timedelta(hours=1)
        Job.objects.filter(pk=job.pk).update(heartbeat_at=old)
        self.assertEqual(jobs.recover_stale(), 1)
        job.refresh_from_db()
        self.assertEqual(job.status, 'interrupted')
        self.assertIn('no heartbeat', job.error)
        self.assertEqual(jobs.recover_stale(), 0, 'recovery is idempotent')
        self.assertEqual(Job.objects.filter(status='queued').count(), 0, 'no automatic re-queue')

    def test_fresh_heartbeat_is_left_alone(self):
        job = self.enqueue_research()
        jobs.claim_next('worker-alive')
        self.assertEqual(jobs.recover_stale(), 0)
        job.refresh_from_db()
        self.assertEqual(job.status, 'running')

    def test_keyboard_interrupt_marks_job_interrupted_and_reraises(self):
        job = self.enqueue_research()
        claimed = jobs.claim_next('worker-ctrl-c')
        with mock.patch.dict(reviewing.HANDLERS, {'research_draft': mock.Mock(side_effect=KeyboardInterrupt)}):
            with self.assertRaises(KeyboardInterrupt):
                jobs.execute(claimed)
        job.refresh_from_db()
        self.assertEqual(job.status, 'interrupted')

    def test_retry_creates_new_job_with_same_snapshot(self):
        failed = jobs.enqueue('propose_edit', user=self.admin, runner_name='simulated',
                              input={'request': 'x', 'run_review': False,
                                     'scenario': {'replacements': [{'find': 'NOT PRESENT', 'with': 'y'}]}},
                              label='Will fail', article=self.article)
        failed = jobs.run_now(failed)
        self.assertEqual(failed.status, 'failed')
        self.assertIn('does not apply', failed.error)
        retry = jobs.retry(failed, self.admin)
        self.assertEqual(retry.status, 'queued')
        self.assertEqual(retry.retry_of_id, failed.pk)
        self.assertEqual(retry.config_snapshot, failed.config_snapshot)
        with self.assertRaises(Exception):
            jobs.retry(jobs.run_now(self.enqueue_research()), self.admin)

    def test_model_call_budget_is_enforced(self):
        job = jobs.enqueue('run_eval', user=self.admin, runner_name='simulated', input={'case_ids': []},
                           label='Budget test', selection={})
        Job.objects.filter(pk=job.pk).update(max_model_calls=1)
        from core.models import EvalCase
        EvalCase.objects.create(slug='t', name='t', category='supported_correction', article=self.article,
                                scenario={'candidates': [{'label': 'A', 'rationale': 'A rationale of sufficient length here.',
                                                          'replacements': [{'find': 'It may look grey', 'with': 'It looks grey'}]}]},
                                expected='unknown', label_source='unknown')
        job = jobs.run_now(job)
        self.assertEqual(job.status, 'failed')
        self.assertIn('budget', job.error.lower())
        self.assertLessEqual(job.model_calls, 1)

    def test_unexpected_exception_fails_job_without_leaking_traceback(self):
        job = self.enqueue_research()
        with mock.patch.dict(reviewing.HANDLERS, {'research_draft': mock.Mock(side_effect=RuntimeError('secret detail'))}):
            job = jobs.run_now(job)
        self.assertEqual(job.status, 'failed')
        self.assertNotIn('secret detail', job.error)
        self.assertIn('RuntimeError', job.error)

    def test_worker_command_runs_one_queued_job(self):
        self.enqueue_research('Worker topic')
        out = StringIO()
        call_command('run_worker', '--once', stdout=out)
        self.assertIn('succeeded', out.getvalue())
        self.assertEqual(Job.objects.filter(status='succeeded').count(), 1)


class ReviewIndependenceTests(WorkshopTestCase):

    def test_reviewers_see_only_the_proposal_not_other_verdicts(self):
        proposal = self.propose('A sentence for independent review, with a hedge.')
        seen = []

        class SpyRunner:
            name = 'simulated'
            label = 'SIMULATED'

            def call(self, ctx, task):
                seen.append(task)
                return {'verdict': 'support', 'comment': 'ok', 'evidence_notes': ''}

        job = jobs.enqueue('review_proposal', user=self.admin, runner_name='simulated', input={},
                           label='Spy', article=self.article, proposal=proposal)
        ctx = jobs.JobContext(job)
        ctx.runner = SpyRunner()
        reviewing.run_panel(ctx, proposal, configs.DEFAULTS['reviewers'], configs.DEFAULTS['instructions'])
        self.assertEqual(len(seen), 4)
        for task in seen:
            blob = repr(task.payload)
            self.assertNotIn('verdict', blob, 'a reviewer must not receive any verdict')
            self.assertNotIn('comment', blob)
            self.assertIn('candidate', task.payload)
            self.assertIn('base', task.payload)
        self.assertEqual(proposal.reviews.count(), 4)

    def test_panel_resumes_without_duplicating_reviews(self):
        proposal = self.propose('A resumable panel sentence, with a hedge.')
        editorial.record_review(proposal, role='fact_check', verdict='support', comment='earlier', origin='test')
        job = jobs.enqueue('review_proposal', user=self.admin, runner_name='simulated', input={}, label='Resume',
                           article=self.article, proposal=proposal)
        job = jobs.run_now(job)
        self.assertEqual(job.status, 'succeeded')
        self.assertEqual(proposal.reviews.count(), 4)
        self.assertEqual(proposal.reviews.get(role='fact_check').comment, 'earlier')


@override_settings(GALACTICA={'RUNTIME_DIR': '/tmp/galactica-test-runtime', 'OPENCODE_BIN': 'opencode',
                              'HEARTBEAT_STALE_SECONDS': 90})
class EvalRunTests(WorkshopTestCase):

    def test_eval_run_records_per_case_outcomes(self):
        from core.models import EvalCase
        EvalCase.objects.create(
            slug='t-qual', name='Qualification removed', category='removed_qualification', article=self.article,
            scenario={'candidates': [{'label': 'A', 'rationale': 'Drop the hedge from the sentence for the test.',
                                      'replacements': [{'find': 'It may look grey', 'with': 'It looks grey'}]}]},
            expected='objected', label_source='simulated')
        job = jobs.run_now(jobs.enqueue('run_eval', user=self.admin, runner_name='simulated', input={'case_ids': []},
                                        label='Eval test'))
        self.assertEqual(job.status, 'succeeded')
        result = EvalResult.objects.get(job=job)
        self.assertEqual(result.outcome, 'objected')
        self.assertTrue(result.matches)
        self.assertEqual(result.verdicts['skeptic'], 'object')
        self.assertTrue(Proposal.objects.filter(pk=result.proposal_id, origin='evaluation').exists())

    def test_stale_case_is_reported_not_forced(self):
        from core.models import EvalCase
        EvalCase.objects.create(
            slug='t-stale', name='Stale case', category='supported_correction', article=self.article,
            scenario={'candidates': [{'label': 'A', 'rationale': 'Edits text that no longer exists in the revision.',
                                      'replacements': [{'find': 'Text not in this revision', 'with': 'x'}]}]},
            expected='supported', label_source='simulated')
        job = jobs.run_now(jobs.enqueue('run_eval', user=self.admin, runner_name='simulated', input={'case_ids': []},
                                        label='Stale eval'))
        self.assertEqual(job.status, 'succeeded')
        self.assertEqual(EvalResult.objects.filter(job=job).count(), 0)
        self.assertTrue(job.events.filter(level='warn', message__contains='skipped').exists())
