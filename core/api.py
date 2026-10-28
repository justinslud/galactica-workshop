"""Small token-authenticated JSON API for non-human actors.

Read endpoints plus bounded research and review writes. There is deliberately no publish endpoint and no automatic
publication, regardless of scope.
"""
import json
from functools import wraps

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from . import configs, editorial, jobs
from .agent_auth import AgentAuthError, authenticate
from .blocks import ValidationError as BlockValidationError
from .models import Agent, Article, Job, Proposal, Review, Revision, SourceSnapshot


def _body(request):
    try:
        return json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return None


def _snapshot_brief(snapshot):
    return {
        'id': str(snapshot.id), 'url': snapshot.url, 'final_url': snapshot.final_url,
        'fetched_at': snapshot.fetched_at.isoformat(), 'sha256': snapshot.sha256,
        'byte_count': snapshot.byte_count, 'title': snapshot.title, 'excerpt': snapshot.excerpt,
        'extraction_notes': snapshot.extraction_notes, 'error': snapshot.error,
    }


def _source_payload(source):
    snap = source.snapshots.order_by('-created_at').first()
    return {
        'id': str(source.id), 'title': source.title, 'url': source.url, 'kind': source.kind,
        'check_status': source.check_status, 'retrieval_note': source.retrieval_note,
        'publisher': source.publisher, 'retrieved_on': source.retrieved_on.isoformat() if source.retrieved_on else None,
        'snapshot': _snapshot_brief(snap) if snap else None,
    }


def revision_payload(revision):
    return {
        'id': str(revision.id), 'number': revision.number, 'state': revision.state,
        'title': revision.title, 'opening': revision.opening, 'summary': revision.summary,
        'created_at': revision.created_at.isoformat(),
        'published_at': revision.published_at.isoformat() if revision.published_at else None,
        'blocks': [
            {'block_id': str(b.block_id), 'position': b.position, 'kind': b.kind, 'data': b.data}
            for b in revision.blocks.order_by('position')
        ],
        'citations': [
            {'block_id': str(c.block_id), 'source': _source_payload(c.source), 'supports': c.supports, 'quote': c.quote}
            for c in revision.citations.select_related('source')
        ],
    }


def article_payload(article):
    return {
        'id': str(article.id), 'slug': article.slug, 'title': article.title, 'opening': article.opening,
        'provenance': article.provenance, 'updated_at': article.updated_at.isoformat(),
        'published_revision': (revision_payload(article.published) if article.published else None),
        'revision_count': article.revisions.count(),
    }


def proposal_payload(proposal):
    return {
        'id': str(proposal.id), 'status': proposal.status, 'origin': proposal.origin,
        'rationale': proposal.rationale, 'is_stale': proposal.is_stale,
        'agent': proposal.agent.name if proposal.agent else None,
        'operator': proposal.created_by.username if proposal.created_by else None,
        'origin_model': proposal.origin_model, 'origin_job': str(proposal.origin_job_id) if proposal.origin_job_id else None,
        'base': (revision_payload(proposal.base) if proposal.base else None),
        'candidate': revision_payload(proposal.candidate),
        'reviews': [
            {'role': r.role, 'verdict': r.verdict, 'comment': r.comment, 'evidence_notes': r.evidence_notes,
             'origin': r.origin, 'declared_model': r.declared_model, 'agent': r.agent.name if r.agent else None}
            for r in proposal.reviews.select_related('agent')
        ],
        'jobs': [str(j.pk) for j in proposal.jobs.all()],
    }


def job_payload(job):
    return {
        'id': str(job.id), 'kind': job.kind, 'status': job.status, 'runner': job.runner,
        'created_at': job.created_at.isoformat(), 'finished_at': job.finished_at.isoformat() if job.finished_at else None,
        'error': job.error, 'output': job.output, 'usage': job.usage,
        'model_calls': job.model_calls, 'max_model_calls': job.max_model_calls,
        'agent_runs': [
            {'profile': r.profile, 'role': r.role, 'model': r.model, 'status': r.status,
             'agent': r.agent.name if r.agent else None, 'config_versions': r.config_versions}
            for r in job.agent_runs.select_related('agent')
        ],
        'events': [{'at': e.created_at.isoformat(), 'level': e.level, 'message': e.message} for e in job.events.all()],
    }


def _api_view(scope):
    def decorate(view):
        @wraps(view)
        @csrf_exempt
        @require_http_methods(['GET', 'POST'])
        def wrapper(request, *args, **kwargs):
            try:
                agent, credential = authenticate(request, scope)
            except AgentAuthError as exc:
                return JsonResponse({'error': str(exc)}, status=401)
            request.agent = agent
            request.credential = credential
            return view(request, *args, **kwargs)
        return wrapper
    return decorate


@_api_view('read')
def articles(request):
    items = Article.objects.select_related('published').all()
    return JsonResponse({'articles': [article_payload(a) for a in items]})


@_api_view('read')
def article_detail(request, slug):
    article = get_object_or_404(Article.objects.select_related('published'), slug=slug)
    data = article_payload(article)
    data['open_proposals'] = [
        {'id': str(p.id), 'status': p.status, 'origin': p.origin, 'is_stale': p.is_stale}
        for p in article.proposals.filter(status__in=['pending', 'approved', 'revision_requested'])
    ]
    return JsonResponse(data)


@_api_view('read')
def revision_detail(request, pk):
    return JsonResponse(revision_payload(get_object_or_404(Revision, pk=pk)))


@_api_view('read')
def proposal_detail(request, pk):
    return JsonResponse(proposal_payload(get_object_or_404(Proposal, pk=pk)))


@_api_view('read')
def job_detail(request, pk):
    return JsonResponse(job_payload(get_object_or_404(Job, pk=pk)))


@_api_view('read')
def snapshots(request):
    qs = SourceSnapshot.objects.order_by('-created_at')[:50]
    return JsonResponse({'snapshots': [_snapshot_brief(s) for s in qs]})


@_api_view('research')
@require_http_methods(['POST'])
def start_research(request):
    body = _body(request)
    if body is None:
        return JsonResponse({'error': 'Body must be JSON.'}, status=400)
    topic = str(body.get('topic', '')).strip()
    question = str(body.get('question', '')).strip()
    if not 3 <= len(topic) <= 200 or not 3 <= len(question) <= 500:
        return JsonResponse({'error': 'topic (3-200) and question (3-500) are required.'}, status=400)
    runner_version = (configs.ConfigVersion.objects.filter(kind='runner', data__runner='opencode').order_by('-is_default', 'family').first())
    if runner_version is None:
        return JsonResponse({'error': 'No OpenCode runner version is configured. No paid fallback is attempted.'}, status=409)
    job = jobs.enqueue(
        'agent_cycle', user=request.agent.operator, runner_name='opencode',
        input={'topic': topic, 'question': question, 'agent_id': str(request.agent.pk)},
        label=f'Agent cycle: {topic}', selection={'runner': runner_version},
    )
    return JsonResponse({'job': str(job.pk), 'status': job.status}, status=202)


@_api_view('review')
@require_http_methods(['POST'])
def record_review_api(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    body = _body(request)
    if body is None:
        return JsonResponse({'error': 'Body must be JSON.'}, status=400)
    role = str(body.get('role', '')).strip()
    verdict = str(body.get('verdict', '')).strip()
    if role not in {key for key, _label, _instr in configs.REVIEW_ROLES}:
        return JsonResponse({'error': 'Unknown review role.'}, status=400)
    try:
        review = editorial.record_review(
            proposal, role=role, verdict=verdict, comment=str(body.get('comment', ''))[:1200],
            evidence_notes=str(body.get('evidence_notes', ''))[:1200], origin='agent',
            declared_model=str(body.get('model', ''))[:120], agent=request.agent,
            operator=request.agent.operator,
        )
    except (editorial.EditorialError, BlockValidationError) as exc:
        return JsonResponse({'error': ' '.join(getattr(exc, 'messages', [str(exc)]))}, status=409)
    return JsonResponse({'review': {'role': review.role, 'verdict': review.verdict}}, status=201)


@_api_view('propose')
@require_http_methods(['POST'])
def submit_proposal(request, slug):
    """Submit a markdown-only candidate with claim-level citations to preserved evidence."""
    import uuid

    from .blocks import validate_blocks
    from .models import Source

    article = get_object_or_404(Article, slug=slug)
    body = _body(request)
    if body is None:
        return JsonResponse({'error': 'Body must be JSON.'}, status=400)
    blocks = body.get('blocks')
    if not isinstance(blocks, list) or not blocks:
        return JsonResponse({'error': 'blocks must be a non-empty list.'}, status=400)
    items = []
    for block in blocks:
        if not isinstance(block, dict) or block.get('kind') != 'markdown':
            return JsonResponse({'error': 'Agent proposals may only contain markdown blocks.'}, status=400)
        items.append({'block_id': str(uuid.uuid4()), 'kind': 'markdown', 'data': block.get('data', {})})
    try:
        validate_blocks(items)
    except Exception as exc:
        return JsonResponse({'error': ' '.join(getattr(exc, 'messages', [str(exc)]))}, status=400)
    raw_claims = body.get('claims')
    if not isinstance(raw_claims, list) or not raw_claims:
        return JsonResponse({'error': 'claims are required; agent proposals must be claim-level.'}, status=400)
    claims = []
    source_ids = set()
    for index, claim in enumerate(raw_claims, start=1):
        if not isinstance(claim, dict):
            return JsonResponse({'error': f'Claim {index} is malformed.'}, status=400)
        citations = []
        for c_index, citation in enumerate(claim.get('citations') or [], start=1):
            if not isinstance(citation, dict):
                return JsonResponse({'error': f'Claim {index} citation {c_index} is malformed.'}, status=400)
            source = Source.objects.filter(pk=citation.get('source_id')).first()
            if source is None or not source.snapshots.exists():
                return JsonResponse({'error': f'Claim {index} citation {c_index} needs a preserved snapshot source.'}, status=400)
            source_ids.add(source.pk)
            citations.append({
                'source_id': str(source.pk), 'supports': str(citation.get('supports', '')),
                'quote': str(citation.get('quote', '')), 'stance': citation.get('stance', 'supports'),
                'strength': citation.get('strength', 'direct'),
            })
        claims.append({'block_index': claim.get('block_index'), 'text': claim.get('text'), 'citations': citations})
    try:
        candidate = editorial.create_candidate(
            article, title=str(body.get('title', article.title)), opening=str(body.get('opening', '')),
            items=items, citations=[], claims=claims, origin='agent', user=request.agent.operator,
            allowed_source_ids=source_ids,
        )
        proposal = editorial.open_proposal(
            candidate, rationale=str(body.get('rationale', '')), origin='agent', user=request.agent.operator,
            agent=request.agent, origin_model=str(body.get('model', ''))[:160],
        )
    except (editorial.EditorialError, BlockValidationError) as exc:
        return JsonResponse({'error': ' '.join(getattr(exc, 'messages', [str(exc)]))}, status=409)
    return JsonResponse({'proposal': str(proposal.pk), 'status': proposal.status,
                         'candidate': proposal.candidate.label}, status=201)
