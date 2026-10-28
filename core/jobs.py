"""Job queue. Web requests enqueue rows; a separate worker process claims and runs them.

- Claiming is a single short write transaction (SQLite IMMEDIATE), so two workers cannot take one job.
- Every running job heartbeats. A job whose heartbeat is stale is marked INTERRUPTED, never silently retried.
- Cancel and retry are explicit user actions. Closing the browser changes nothing.
"""
import logging
import time
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from . import configs, reviewing
from .blocks import ValidationError as BlockValidationError
from .editorial import EditorialError
from .models import Job, JobEvent
from .runners import BudgetExceeded, JobCancelled, RunnerError, get_runner

log = logging.getLogger('galactica.jobs')


class JobContext:
    """Handed to handlers and runners. The only way work reports progress, spends budget, or checks cancellation."""

    def __init__(self, job):
        self.job = job
        self.runner = None
        self.deadline = time.monotonic() + job.timeout_seconds

    def check(self):
        Job.objects.filter(pk=self.job.pk).update(heartbeat_at=timezone.now())
        if Job.objects.filter(pk=self.job.pk, cancel_requested=True).exists():
            raise JobCancelled()

    def heartbeat(self):
        Job.objects.filter(pk=self.job.pk).update(heartbeat_at=timezone.now())

    def log(self, message, level='info'):
        JobEvent.objects.create(job_id=self.job.pk, message=message[:500], level=level)

    def seconds_left(self):
        return self.deadline - time.monotonic()

    def spend_call(self):
        if self.seconds_left() <= 0:
            raise RunnerError('The job time limit was reached before the next model call.')
        updated = Job.objects.filter(
            pk=self.job.pk, model_calls__lt=F('max_model_calls')
        ).update(model_calls=F('model_calls') + 1)
        if not updated:
            raise BudgetExceeded(
                f'Model call budget of {self.job.max_model_calls} reached for this job. '
                'Retry with a larger limits version if the work needs more calls.'
            )
        self.job.model_calls += 1

    def record_usage(self, usage):
        """Add measured usage. Estimates are never written here; absent values stay absent."""
        job = Job.objects.get(pk=self.job.pk)
        merged = dict(job.usage or {})
        for key, value in usage.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool) and key in merged:
                if key == 'reported_cost' and (merged[key] is None or value is None):
                    merged[key] = value if merged[key] is None else merged[key]
                else:
                    merged[key] = merged[key] + value
            elif key not in merged:
                merged[key] = value
        merged['source'] = usage.get('source', merged.get('source'))
        Job.objects.filter(pk=self.job.pk).update(usage=merged)


def enqueue(kind, *, user, runner_name, input, label, article=None, proposal=None, selection=None, retry_of=None,
            config_snapshot=None):
    snapshot = config_snapshot or configs.resolve_snapshot(selection or {})
    limits = snapshot['limits']['data']
    job = Job.objects.create(
        kind=kind, runner=runner_name, label=label[:200], article=article, proposal=proposal,
        input=input, config_snapshot=snapshot,
        max_model_calls=int(limits.get('max_model_calls', 8)),
        timeout_seconds=int(limits.get('job_timeout_seconds', 900)),
        created_by=user, retry_of=retry_of,
    )
    JobEvent.objects.create(job=job, message=f'Queued ({job.get_kind_display()}, runner {runner_name}).')
    return job


def enqueue_review(proposal, *, user, runner, config_snapshot):
    return enqueue(
        'review_proposal', user=user, runner_name=runner, input={}, label=f'Review panel for {proposal.article.title}',
        article=proposal.article, proposal=proposal, config_snapshot=config_snapshot,
    )


def request_cancel(job):
    with transaction.atomic():
        job = Job.objects.select_for_update().get(pk=job.pk)
        if job.status == 'queued':
            job.status = 'cancelled'
            job.finished_at = timezone.now()
            job.error = 'Cancelled before the worker started it.'
            job.save(update_fields=['status', 'finished_at', 'error'])
            JobEvent.objects.create(job=job, message='Cancelled while queued.')
        elif job.status == 'running' and not job.cancel_requested:
            job.cancel_requested = True
            job.save(update_fields=['cancel_requested'])
            JobEvent.objects.create(job=job, message='Cancel requested. The worker stops at its next check.')
        else:
            raise EditorialError(f'This job is already {job.get_status_display().lower()}.')
    return job


def retry(job, user):
    if not job.can_retry:
        raise EditorialError('Only failed, cancelled or interrupted jobs can be retried.')
    new = enqueue(
        job.kind, user=user, runner_name=job.runner, input=job.input, label=job.label,
        article=job.article, proposal=None, config_snapshot=job.config_snapshot, retry_of=job,
    )
    JobEvent.objects.create(job=job, message=f'Retried as job {str(new.pk)[:8]}.')
    return new


def recover_stale(now=None):
    """Mark running jobs whose worker stopped heartbeating as interrupted. Returns the count."""
    now = now or timezone.now()
    cutoff = now - timedelta(seconds=settings.GALACTICA['HEARTBEAT_STALE_SECONDS'])
    stale = list(Job.objects.filter(status='running').filter(heartbeat_at__lt=cutoff))
    for job in stale:
        message = ('The worker stopped or lost contact while this job ran (no heartbeat). '
                   'Work already recorded is kept. Retry to run the job again.')
        with transaction.atomic():
            updated = Job.objects.filter(pk=job.pk, status='running').update(
                status='interrupted', finished_at=now, error=message)
            if updated:
                JobEvent.objects.create(job=job, level='warn', message=f'Interrupted: {message}')
    return len(stale)


def claim_next(worker_id):
    with transaction.atomic():
        candidate = Job.objects.filter(status='queued').order_by('created_at').first()
        if candidate is None:
            return None
        now = timezone.now()
        claimed = Job.objects.filter(pk=candidate.pk, status='queued').update(
            status='running', started_at=now, heartbeat_at=now, worker_id=worker_id)
        if not claimed:
            return None
        JobEvent.objects.create(job_id=candidate.pk, message=f'Started by worker {worker_id}.')
    return Job.objects.get(pk=candidate.pk)


def finish(job, status, *, output=None, error=''):
    Job.objects.filter(pk=job.pk).update(
        status=status, finished_at=timezone.now(), error=error[:2000], output=output or {},
    )
    level = 'info' if status == 'succeeded' else 'warn' if status in ('cancelled', 'interrupted') else 'error'
    message = f'Finished: {status}.' + (f' {error}' if error else '')
    JobEvent.objects.create(job_id=job.pk, level=level, message=message[:500])


def execute(job):
    """Run one claimed job to a terminal state. Never leaves a job in 'running' on a handled error."""
    ctx = JobContext(job)
    try:
        runner = get_runner(job.runner)
        if job.runner == 'opencode':
            ok, message = runner.available()
            if not ok:
                raise RunnerError(message)
        ctx.runner = runner
        ctx.log(f'Runner: {runner.label}. Limits: {job.max_model_calls} model calls, {job.timeout_seconds}s.')
        ctx.check()
        handler = reviewing.HANDLERS[job.kind]
        output = handler(ctx)
        finish(job, 'succeeded', output=output)
    except JobCancelled:
        finish(job, 'cancelled', error='Cancelled by user.')
    except KeyboardInterrupt:
        finish(job, 'interrupted', error='Worker was stopped while this job ran. Retry to run it again.')
        raise
    except BudgetExceeded as exc:
        finish(job, 'failed', error=str(exc))
    except RunnerError as exc:
        finish(job, 'failed', error=str(exc))
    except EditorialError as exc:
        finish(job, 'failed', error=str(exc))
    except BlockValidationError as exc:
        finish(job, 'failed', error=' '.join(exc.messages))
    except Exception as exc:
        log.exception('Unexpected error in job %s', job.pk)
        finish(job, 'failed', error=f'Unexpected error ({type(exc).__name__}). See the worker log.')


def run_one(worker_id):
    """Claim and run one job. Returns the job or None."""
    job = claim_next(worker_id)
    if job is not None:
        execute(job)
    return job


def run_now(job, worker_id='local'):
    """Claim a specific queued job and execute it exactly as the worker would. Used by seeding and tests."""
    with transaction.atomic():
        now = timezone.now()
        claimed = Job.objects.filter(pk=job.pk, status='queued').update(
            status='running', started_at=now, heartbeat_at=now, worker_id=worker_id)
        if not claimed:
            raise EditorialError('Only queued jobs can be run.')
        JobEvent.objects.create(job_id=job.pk, message=f'Started by worker {worker_id}.')
    job = Job.objects.get(pk=job.pk)
    execute(job)
    return Job.objects.get(pk=job.pk)
