"""Small token-authenticated JSON API for non-human actors.

Read endpoints plus bounded research and review writes. There is deliberately no publish endpoint and no automatic
publication, regardless of scope.
"""
import json
from functools import wraps

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from . import configs, editorial, idempotency, jobs, licensing
from .agent_auth import AgentAuthError, authenticate
from .blocks import ValidationError as BlockValidationError
from .models import Agent, Article, Claim, Job, Proposal, PublicationEvent, Review, Revision, SourceSnapshot


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
        'license': source.license, 'attribution': source.attribution,
        'snapshot': _snapshot_brief(snap) if snap else None,
    }


def _revision_permalink(revision):
    return reverse('article_revision', args=[revision.article.slug, revision.number])


def revision_payload(revision):
    permalink = _revision_permalink(revision)
    return {
        'id': str(revision.id), 'number': revision.number, 'state': revision.state,
        'title': revision.title, 'opening': revision.opening, 'summary': revision.summary,
        'content_hash': revision.content_hash,
        'permalink': permalink,
        'citation': licensing.citation(revision.article, revision, permalink),
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
        'topic': ({'slug': article.topic.slug, 'title': article.topic.title} if article.topic else None),
        'provenance': article.provenance, 'license': licensing.license_info(article.license),
        'attribution': article.attribution, 'permalink': reverse('article', args=[article.slug]),
        'updated_at': article.updated_at.isoformat(),
        'published_revision': (revision_payload(article.published) if article.published else None),
        'revision_count': article.revisions.count(),
    }


def _claim_valid_to(claim):
    event = PublicationEvent.objects.filter(article_id=claim.revision.article_id, revision_id=claim.revision_id).first()
    if event is None:
        return None
    later = PublicationEvent.objects.filter(
        article_id=claim.revision.article_id, sequence__gt=event.sequence,
    ).order_by('sequence').first()
    return later.published_at.isoformat() if later else None


def claim_payload(claim):
    revision = claim.revision
    article = revision.article
    current = article.published
    if current is None or revision.state not in ('published', 'superseded'):
        resolution = 'unpublished'
    elif current.pk == revision.pk:
        resolution = 'current'
    else:
        resolution = 'superseded'
    citations = []
    for citation in claim.citations.select_related('source'):
        citations.append({
            'source': _source_payload(citation.source), 'supports': citation.supports, 'quote': citation.quote,
            'stance': citation.stance, 'strength': citation.strength,
        })
    return {
        'id': str(claim.pk), 'text': claim.text, 'support_status': claim.support_status,
        'support_note': claim.support_note, 'block_id': str(claim.block_id), 'position': claim.position,
        'permalink': reverse('claim', args=[claim.pk]),
        'resolution': resolution, 'valid_to': _claim_valid_to(claim),
        'article': {
            'slug': article.slug, 'title': article.title,
            'license': licensing.license_info(article.license), 'permalink': reverse('article', args=[article.slug]),
        },
        'revision': {
            'id': str(revision.pk), 'number': revision.number, 'label': revision.label,
            'state': revision.state, 'content_hash': revision.content_hash,
            'permalink': _revision_permalink(revision),
        },
        'current_revision': (
            {'id': str(current.pk), 'number': current.number, 'label': current.label,
             'permalink': _revision_permalink(current)}
            if current else None
        ),
        'citations': citations,
        'note': (
            'This claim id is bound to one revision in M0. It always resolves to that occurrence; '
            'follow current_revision to see whether the article still says this.'
        ),
    }


def _etag_json(request, payload, content_hash):
    etag = f'"{content_hash}"' if content_hash else ''
    if etag and request.headers.get('If-None-Match') == etag:
        return HttpResponse(status=304, headers={'ETag': etag})
    response = JsonResponse(payload)
    if etag:
        response['ETag'] = etag
    return response


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
             'origin': r.origin, 'declared_model': r.declared_model,
             'reviewer': r.reviewer.username if r.reviewer else None,
             'agent': r.agent.name if r.agent else None}
            for r in proposal.reviews.select_related('agent', 'reviewer')
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
    items = Article.objects.select_related('published', 'topic').all()
    return JsonResponse({'articles': [article_payload(a) for a in items]})


@_api_view('read')
def article_detail(request, slug):
    article = get_object_or_404(Article.objects.select_related('published', 'topic'), slug=slug)
    data = article_payload(article)
    data['open_proposals'] = [
        {'id': str(p.id), 'status': p.status, 'origin': p.origin, 'is_stale': p.is_stale}
        for p in article.proposals.filter(status__in=['pending', 'approved', 'revision_requested'])
    ]
    return _etag_json(request, data, article.published.content_hash if article.published else '')


@_api_view('read')
def revision_detail(request, pk):
    revision = get_object_or_404(Revision.objects.select_related('article'), pk=pk)
    return _etag_json(request, revision_payload(revision), revision.content_hash)


@_api_view('read')
def claim_detail(request, pk):
    claim = get_object_or_404(
        Claim.objects.select_related('revision', 'revision__article', 'revision__article__published'), pk=pk,
    )
    if claim.revision.state not in ('published', 'superseded'):
        raise Http404()
    return _etag_json(request, claim_payload(claim), claim.revision.content_hash)


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


def _idempotent_write(resource_type):
    """Wrap a write view with key handling. Only successful responses are replayed."""
    def decorate(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            try:
                record, replay = idempotency.begin(request, request.agent)
            except idempotency.ApiProblem as exc:
                return idempotency.problem(exc.status, exc.code, exc.detail, exc.headers)
            if replay is not None:
                return replay
            try:
                response = view(request, *args, **kwargs)
            except idempotency.ApiProblem as exc:
                idempotency.abandon(record)
                return idempotency.problem(exc.status, exc.code, exc.detail, exc.headers)
            except Exception:
                idempotency.abandon(record)
                raise
            if 200 <= response.status_code < 300:
                resource_id = ''
                try:
                    payload = json.loads(response.content or b'{}')
                    resource_id = payload.get('proposal') or payload.get('job') or payload.get('review', {}).get('id') or ''
                except (ValueError, AttributeError):
                    pass
                if not resource_id:
                    resource_id = kwargs.get('pk') or kwargs.get('slug') or ''
                idempotency.complete(record, response, resource_type=resource_type, resource_id=resource_id)
            else:
                idempotency.abandon(record)
            return response
        return wrapper
    return decorate


@_api_view('research')
@require_http_methods(['POST'])
@_idempotent_write('research_job')
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
@_idempotent_write('review')
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
@_idempotent_write('proposal')
def submit_proposal(request, slug):
    """Submit a markdown-only candidate with claim-level citations to preserved evidence."""
    import uuid

    from .blocks import validate_blocks
    from .models import Source

    article = get_object_or_404(Article.objects.select_related('published'), slug=slug)
    base = idempotency.check_if_match(request, article)
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
            expected_base_id=base.pk,
        )
    except (editorial.EditorialError, BlockValidationError) as exc:
        return JsonResponse({'error': ' '.join(getattr(exc, 'messages', [str(exc)]))}, status=409)
    return JsonResponse({'proposal': str(proposal.pk), 'status': proposal.status,
                         'candidate': proposal.candidate.label}, status=201)


def claim_payload_response(request, claim):
    """Shared by the token API and the public resolver's JSON representation."""
    return _etag_json(request, claim_payload(claim), claim.revision.content_hash)
