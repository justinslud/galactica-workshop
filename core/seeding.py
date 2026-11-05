"""Repeatable demonstration data. Runs through the same services and job path as the app.

Running it twice changes nothing: the demo articles are created once; sources, presets and test cases are get-or-create.
All demo content is labelled as a demonstration draft. Simulated runs are labelled SIMULATED.
"""
import os
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from . import configs, demo_content as dc, editorial, jobs
from .models import Agent, Article, EvalCase, Job, Proposal, Source, Topic


def ensure_users():
    admin_pw = os.environ.get('GALACTICA_DEMO_PASSWORD', 'admin')
    admin, created = User.objects.get_or_create(username='admin')
    if created:
        admin.set_password(admin_pw)
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    editor, created = User.objects.get_or_create(username='editor')
    if created:
        editor.set_password(os.environ.get('GALACTICA_EDITOR_PASSWORD', 'editor'))
    editor.is_staff = False
    editor.save()
    return admin, editor


def ensure_agent(admin):
    agent, _ = Agent.objects.get_or_create(
        name='galactica-agent',
        defaults={
            'operator': admin, 'kind': 'agent', 'scopes': ['read', 'research', 'propose', 'review'],
            'description': 'Default local editorial agent. No credential is issued by seeding.',
        },
    )
    return agent


def ensure_sources():
    out = {}
    for key, spec in dc.SOURCES.items():
        source = Source.objects.filter(title=spec['title']).first()
        if source is None:
            source = Source.objects.create(
                title=spec['title'], url=spec.get('url', ''), kind=spec.get('kind', 'other'),
                authors=spec.get('authors', ''), publisher=spec.get('publisher', ''),
                published_on=spec.get('published_on', ''), check_status=spec.get('check_status', 'unchecked'),
                retrieved_on=dc.RETRIEVED, retrieval_note=spec.get('retrieval_note', ''),
            )
        out[key] = source
    return out


def ensure_cases():
    for spec in dc.EVAL_CASES:
        article = Article.objects.get(slug=spec['article'])
        EvalCase.objects.get_or_create(
            slug=spec['slug'],
            defaults=dict(
                category=spec['category'], name=spec['name'], description=spec['description'],
                article=article, scenario=spec['scenario'], expected=spec['expected'],
                label_source=spec['label_source'],
            ),
        )


DEMO_TOPICS = [
    ('subvocal-interfaces', 'Subvocal interfaces',
     'Silent-speech interfaces and the sensors used to read speech without audible sound.'),
    ('quadratic-funding', 'Quadratic funding',
     'Matching-fund mechanisms for public goods, including quadratic voting and related designs.'),
    ('encyclopedia-galactica', 'Encyclopedia Galactica',
     'The fictional reference work and its literary and cultural afterlives.'),
]


def ensure_topics(admin):
    """Get-or-create the demonstration topic graph and attach existing demo articles once."""
    topics = {}
    for slug, title, scope in DEMO_TOPICS:
        topic, _ = Topic.objects.get_or_create(
            slug=slug, defaults={'title': title, 'scope_statement': scope, 'created_by': admin},
        )
        topics[slug] = topic
    for slug, topic in topics.items():
        article = Article.objects.filter(slug=slug, topic__isnull=True).first()
        if article is not None:
            article.topic = topic
            article.save(update_fields=['topic'])
    return topics


def _create_demo_article(spec, admin, sources, topic=None):
    slug = spec['slug']
    article = Article.objects.create(slug=slug, title=spec['title'], opening=spec['opening'],
                                     provenance='demonstration', topic=topic)
    items = [{'block_id': dc.bid(slug, i), 'kind': b['kind'], 'data': b['data']}
             for i, b in enumerate(spec['blocks'])]
    citations = [
        {'block_id': dc.bid(slug, pos), 'source_id': str(sources[key].pk), 'supports': supports, 'quote': quote}
        for pos, key, supports, quote in spec['citations']
    ]
    editorial.create_published_revision(
        article, admin, items=items, citations=citations,
        summary='Initial demonstration draft (r1). Not a verified reference article.',
        title=spec['title'], opening=spec['opening'],
    )
    return article


def _run(job):
    job = jobs.run_now(job)
    return job


def _propose(article, user, scenario, request, review=True):
    job = jobs.enqueue(
        'propose_edit', user=user, runner_name='simulated',
        input={'request': request, 'run_review': review, 'scenario': scenario},
        label=f'SIMULATED proposal: {article.title}', article=article,
    )
    job = _run(job)
    if job.status != 'succeeded':
        raise RuntimeError(f'Demo proposal failed: {job.error}')
    proposal = Proposal.objects.get(pk=job.output['proposal'])
    if review and job.output.get('review_job'):
        review_job = Job.objects.get(pk=job.output['review_job'])
        _run(review_job)
    return proposal


def _decide(proposal, admin, decision, note=''):
    editorial.decide(proposal, admin, decision, note)


def seed(log=print):
    admin, _editor = ensure_users()
    ensure_agent(admin)
    configs.ensure_presets()
    sources = ensure_sources()
    topics = ensure_topics(admin)
    if Article.objects.filter(slug=dc.SUBVOCAL['slug']).exists():
        ensure_cases()
        log('Demo content already present. Nothing duplicated; presets, sources and test cases are up to date.')
        return
    with transaction.atomic():
        _build(admin, sources, topics, log)


def _build(admin, sources, topics, log):
    articles = {
        spec['slug']: _create_demo_article(spec, admin, sources, topics.get(spec['slug']))
        for spec in dc.ARTICLES
    }
    ensure_cases()
    subvocal, quadratic, encyclopedia = articles['subvocal-interfaces'], articles['quadratic-funding'], articles['encyclopedia-galactica']
    log('Created 3 demonstration articles at r1 (published).')

    research = jobs.enqueue('research_draft', user=admin, runner_name='simulated',
                            input={'topic': 'How a wiki records corrections (example topic)', 'notes': 'Seeded example.'},
                            label='SIMULATED research and draft: how a wiki records corrections')
    _run(research)
    log(f'Completed SIMULATED research job: {research.label}.')

    rejected = _propose(
        encyclopedia, admin, dc.SCENARIOS['unsupported-date'],
        'Add a first-publication date to the editorial note (deliberately unsupported; for demonstration).',
    )
    _decide(rejected, admin, 'reject', 'No source for the 1931 date. The cited story is dated May 1942 and no 1931 edition is cited.')
    log(f'Rejected unsupported proposal {str(rejected.pk)[:8]} (SIMULATED reviews recorded).')

    pending = _propose(
        quadratic, admin, dc.SCENARIOS['qf-rule-rewrite'],
        'Restate the rule in plainer words. Pending example with contrasting reviewer judgments.',
    )
    log(f'Pending proposal {str(pending.pk)[:8]} with a review panel (contrasting verdicts expected).')

    accepted = _propose(
        quadratic, admin, dc.SCENARIOS['qf-accepted-change'],
        'Name the original scheme explicitly. Completed publication, later reverted.',
    )
    _decide(accepted, admin, 'approve', 'Panel reviewed; change is narrow and cited.')
    published = editorial.publish(accepted, admin)
    log(f'Published {published.label} for quadratic funding.')
    r1 = quadratic.revisions.get(number=1)
    editorial.revert(
        quadratic, r1, admin, reason='Demonstration of a reversible change: restore r1 wording after review.',
        expected_current_id=published.pk,
    )
    log('Reverted quadratic funding to r1 content as a new revision.')

    eval_all = jobs.enqueue('run_eval', user=admin, runner_name='simulated', input={'case_ids': []},
                            label='SIMULATED editorial test run (all cases)')
    _run(eval_all)
    log(f'Completed SIMULATED test run: {eval_all.eval_results.count()} candidate results.')

    correction = _propose(
        subvocal, admin, dc.SCENARIOS['supported-correction'],
        'Correct the AlterEgo year to 2018 to match the DOI record.',
    )
    _decide(correction, admin, 'approve', 'Supported by the DOI record; reviewers support.')
    editorial.publish(correction, admin)
    log('Published the AlterEgo correction for subvocal interfaces.')

    failed = jobs.enqueue('propose_edit', user=admin, runner_name='simulated',
                          input={'request': 'Example of a scripted edit written for another article.',
                                 'run_review': False, 'scenario': dc.SCENARIOS['qf-rule-rewrite']},
                          label='SIMULATED proposal (scripted edit does not apply)', article=subvocal)
    failed = _run(failed)
    log(f'Failed example: {failed.error[:80]}')

    cancelled = jobs.enqueue('run_eval', user=admin, runner_name='simulated', input={'case_ids': []},
                             label='SIMULATED test run (cancelled example)')
    jobs.request_cancel(cancelled)
    log('Cancelled example recorded.')

    stalled = jobs.enqueue('run_eval', user=admin, runner_name='simulated', input={'case_ids': []},
                           label='SIMULATED test run (interrupted example)')
    old = timezone.now() - timedelta(minutes=10)
    Job.objects.filter(pk=stalled.pk).update(status='running', started_at=old, heartbeat_at=old,
                                            worker_id='demo-worker-stopped')
    jobs.JobEvent.objects.create(job=stalled, message='Started by worker demo-worker-stopped.')
    jobs.recover_stale()
    log('Interrupted example recorded (heartbeat stale).')

    encyclopedia_cases = list(EvalCase.objects.filter(article=encyclopedia).values_list('pk', flat=True))
    queued = jobs.enqueue('run_eval', user=admin, runner_name='simulated',
                          input={'case_ids': [str(pk) for pk in encyclopedia_cases]},
                          label='SIMULATED test run (queued; waiting for the worker)')
    log(f'Queued example {str(queued.pk)[:8]} left for the worker. Run: python manage.py run_worker')
    log('Seed complete.')
