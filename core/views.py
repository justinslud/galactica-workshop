import json
from functools import wraps

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Q
from django.template.loader import render_to_string
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import blocks as block_rules
from . import configs, editorial, jobs
from .markup import render_block, word_diff_html
from .models import (
    Agent, AgentRun, Article, AuditEvent, Block, ConfigVersion, EvalCase, EvalResult, Job, Proposal, Review,
    Revision, Source, SourceSnapshot,
)
from .editorial import EditorialError, PermissionDeniedError, ConflictError
from .runners import RunnerError


def staff_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied('Staff account required.')
        return view(request, *args, **kwargs)
    return wrapper


def _flash_error(request, exc):
    if isinstance(exc, PermissionDeniedError):
        raise PermissionDenied(str(exc))
    messages.error(request, ' '.join(getattr(exc, 'messages', [str(exc)])))


def _published_blocks(revision):
    """Shared by the reading view and historical views. Same renderer as the editor preview."""
    if revision is None:
        return []
    block_citations = {}
    for c in revision.citations.select_related('source'):
        block_citations.setdefault(str(c.block_id), []).append({
            'title': c.source.title, 'url': c.source.url, 'check': c.source.get_check_status_display(),
            'supports': c.supports,
        })
    claims_by_block = {}
    for claim in revision.claims.prefetch_related('citations__source'):
        citations = []
        for c in claim.citations.all():
            snap = c.source.snapshots.order_by('-created_at').first()
            citations.append({
                'title': c.source.title, 'url': c.source.url, 'supports': c.supports, 'quote': c.quote,
                'stance': c.get_stance_display(), 'strength': c.get_strength_display(),
                'sha256': snap.sha256 if snap else '', 'fetched_at': snap.fetched_at if snap else None,
                'check': c.source.get_check_status_display(),
            })
        claims_by_block.setdefault(str(claim.block_id), []).append({
            'claim': claim, 'citations': citations,
        })
    return [
        {'kind': block.kind, 'html': render_block(block.kind, block.data),
         'citations': block_citations.get(str(block.block_id), []),
         'claims': claims_by_block.get(str(block.block_id), [])}
        for block in revision.blocks.order_by('position')
    ]


def _editor_payload(draft):
    return {
        'title': draft.title,
        'opening': draft.opening,
        'version': draft.version,
        'blocks': [
            {'block_id': str(b.block_id), 'kind': b.kind, 'data': b.data}
            for b in draft.blocks.order_by('position')
        ],
        'citations': [
            {'block_id': str(c.block_id), 'source_id': str(c.source_id), 'source_title': c.source.title,
             'supports': c.supports, 'quote': c.quote}
            for c in draft.citations.select_related('source')
        ],
    }


# ----- Dashboard and library -----------------------------------------------------------------------

def dashboard(request):
    articles = Article.objects.select_related('published')
    pending = Proposal.objects.filter(status__in=['pending', 'approved', 'revision_requested']).select_related('article', 'article__published', 'base')
    active_jobs = Job.objects.filter(status__in=['queued', 'running']).order_by('-created_at')[:6]
    failed_jobs = Job.objects.filter(status__in=['failed', 'interrupted']).order_by('-created_at')[:4]
    return render(request, 'core/dashboard.html', {
        'article_count': articles.count(),
        'published_count': articles.filter(published__isnull=False).count(),
        'pending_count': pending.count(),
        'active_jobs': active_jobs,
        'failed_jobs': failed_jobs,
        'pending': pending[:6],
        'recent': AuditEvent.objects.select_related('article', 'actor', 'revision')[:12],
        'recent_articles': articles.order_by('-updated_at')[:6],
    })


def library(request):
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', 'all')
    provenance = request.GET.get('provenance', 'all')
    arts = Article.objects.select_related('published').annotate(
        open_proposals=Count('proposals', filter=Q(proposals__status__in=['pending', 'approved', 'revision_requested']))
    )
    if q:
        arts = arts.filter(Q(title__icontains=q) | Q(opening__icontains=q))
    if status == 'published':
        arts = arts.filter(published__isnull=False)
    elif status == 'unpublished':
        arts = arts.filter(published__isnull=True)
    elif status == 'pending':
        arts = arts.filter(open_proposals__gt=0)
    if provenance != 'all':
        arts = arts.filter(provenance=provenance)
    return render(request, 'core/library.html', {
        'articles': arts, 'q': q, 'status': status, 'provenance': provenance,
        'provenance_choices': Article.PROVENANCE,
        'status_choices': [('all', 'All'), ('published', 'Published'), ('unpublished', 'Not published'),
                           ('pending', 'Has open proposals')],
    })


class NewArticleForm(forms.Form):
    title = forms.CharField(max_length=200, label='Working title')
    opening = forms.CharField(max_length=600, required=False, widget=forms.Textarea(attrs={'rows': 2}),
                              label='Short opening (optional)')


@login_required
def article_new(request):
    if request.method == 'POST':
        form = NewArticleForm(request.POST)
        if form.is_valid():
            try:
                article = editorial.create_article(
                    title=form.cleaned_data['title'], opening=form.cleaned_data['opening'], user=request.user)
            except block_rules.ValidationError as exc:
                messages.error(request, ' '.join(exc.messages))
            else:
                messages.success(request, f'Created "{article.title}" with an open draft. Edit it below.')
                return redirect('editor', slug=article.slug)
    else:
        form = NewArticleForm()
    return render(request, 'core/article_new.html', {'form': form})


# ----- Article reading -----------------------------------------------------------------------------

def article_detail(request, slug):
    article = get_object_or_404(Article.objects.select_related('published'), slug=slug)
    rev_number = request.GET.get('rev')
    show_draft = request.GET.get('draft') == '1' and request.user.is_authenticated
    revision = article.published
    viewing_old = False
    draft = None
    if rev_number and rev_number.isdigit():
        revision = get_object_or_404(Revision, article=article, number=int(rev_number))
        if revision.state == 'draft' or revision.state == 'proposed':
            if not request.user.is_authenticated:
                raise Http404()
        viewing_old = revision.pk != article.published_id
    if show_draft:
        draft = article.revisions.filter(state='draft').first()
        if draft is not None:
            revision = draft
    if revision is None and draft is None:
        return render(request, 'core/article.html', {'article': article, 'revision': None, 'items': [],
                                                     'open_proposals': [], 'viewing_old': False, 'draft': None,
                                                     'draft_banner': False})
    open_proposals = []
    if request.user.is_authenticated:
        open_proposals = article.proposals.filter(status__in=['pending', 'approved', 'revision_requested']).select_related('base')
    return render(request, 'core/article.html', {
        'article': article,
        'revision': revision,
        'items': _published_blocks(revision),
        'viewing_old': viewing_old,
        'draft_banner': revision is not None and revision.state == 'draft',
        'open_proposals': open_proposals,
        'draft': draft,
    })


@login_required
def article_history(request, slug):
    article = get_object_or_404(Article.objects.select_related('published'), slug=slug)
    revisions = article.revisions.select_related('created_by', 'reverts').all()
    events = article.audit_events.select_related('actor', 'revision', 'proposal').all()[:60]
    return render(request, 'core/history.html', {
        'article': article, 'revisions': revisions, 'events': events,
    })


# ----- Editor -----------------------------------------------------------------------------------------

@login_required
def editor(request, slug):
    article = get_object_or_404(Article.objects.select_related('published'), slug=slug)
    try:
        draft = editorial.ensure_draft(article, request.user)
    except EditorialError as exc:
        _flash_error(request, exc)
        return redirect('article', slug=slug)
    last_submitted = article.proposals.filter(origin='human').select_related('candidate').first()
    return render(request, 'core/editor.html', {
        'article': article,
        'draft': draft,
        'payload': _editor_payload(draft),
        'sources': [
            {'id': str(s.pk), 'title': s.title, 'check': s.get_check_status_display(), 'url': s.url}
            for s in Source.objects.all()
        ],
        'last_submitted': last_submitted,
    })


@login_required
@require_POST
def editor_save(request, slug):
    article = get_object_or_404(Article, slug=slug)
    raw = request.POST.get('payload', '')
    action = request.POST.get('action', 'save')
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        messages.error(request, 'The editor sent unreadable content. Nothing was saved; reload and try again.')
        return redirect('editor', slug=slug)
    draft = article.revisions.filter(state='draft').first()
    if draft is None:
        messages.error(request, 'There is no open draft. Reopen the editor to start one.')
        return redirect('editor', slug=slug)
    try:
        draft = editorial.save_draft(
            draft, request.user, title=payload.get('title', ''), opening=payload.get('opening', ''),
            items=payload.get('blocks', []), citations=payload.get('citations', []),
            expected_version=payload.get('version', -1),
        )
    except (block_rules.ValidationError, EditorialError) as exc:
        _flash_error(request, exc)
        return redirect('editor', slug=slug)
    if action == 'submit':
        rationale = request.POST.get('rationale', '')
        try:
            proposal = editorial.submit_draft(draft, request.user, rationale)
        except (block_rules.ValidationError, EditorialError) as exc:
            _flash_error(request, exc)
            messages.info(request, 'Your edits were saved as a draft.')
            return redirect('editor', slug=slug)
        messages.success(request, f'Proposal submitted against {proposal.base.label if proposal.base else "a new article"}. '
                                  'Run the review panel or wait for a staff decision.')
        return redirect('proposal', pk=proposal.pk)
    messages.success(request, 'Draft saved.')
    return redirect('editor', slug=slug)


@login_required
@require_POST
def editor_preview(request, slug):
    article = get_object_or_404(Article, slug=slug)
    try:
        payload = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return JsonResponse({'errors': ['Preview input was not valid JSON.']}, status=400)
    try:
        items = block_rules.validate_blocks(payload.get('blocks', []))
        title, opening = (payload.get('title') or '').strip(), (payload.get('opening') or '').strip()
        if not title:
            title = '(untitled)'
    except block_rules.ValidationError as exc:
        return JsonResponse({'errors': exc.messages, 'html': ''}, status=200)
    sources = {str(s.pk): s for s in Source.objects.filter(pk__in=[c.get('source_id') for c in payload.get('citations', []) if c.get('source_id')])} if payload.get('citations') else {}
    by_block = {}
    for c in payload.get('citations', []):
        source = sources.get(str(c.get('source_id')))
        if source is not None:
            by_block.setdefault(str(c.get('block_id')), []).append({'title': source.title, 'url': source.url, 'check': source.get_check_status_display(), 'supports': str(c.get('supports', ''))[:400]})
    rendered = []
    for item in items:
        rendered.append({'html': render_block(item['kind'], item['data']), 'citations': by_block.get(str(item.get('block_id')), [])})
    html = render_to_string('core/_article_body.html', {'title': title, 'opening': opening, 'items': rendered,
                                                         'preview': True})
    return JsonResponse({'html': html, 'errors': [], 'slug': article.slug})


class SourceForm(forms.Form):
    title = forms.CharField(max_length=300)
    url = forms.URLField(required=False)
    kind = forms.ChoiceField(choices=Source.KINDS)
    authors = forms.CharField(max_length=300, required=False)
    publisher = forms.CharField(max_length=200, required=False)
    published_on = forms.CharField(max_length=60, required=False, help_text='As published, e.g. 2018 or 17 Sep 2018.')
    check_status = forms.ChoiceField(choices=Source.CHECK, initial='unchecked',
                                     help_text='Only choose "opened" if you actually opened and checked the source.')
    retrieval_note = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}),
                                     help_text='How and when this was checked.')


@login_required
def source_new(request):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('library')
    if request.method == 'POST':
        form = SourceForm(request.POST)
        if form.is_valid():
            try:
                source = editorial.create_source(user=request.user, **form.cleaned_data)
            except block_rules.ValidationError as exc:
                messages.error(request, ' '.join(exc.messages))
            else:
                messages.success(request, f'Source added: {source.title}. Attach it to a block in the editor.')
                return redirect(next_url)
    else:
        form = SourceForm()
    return render(request, 'core/source_form.html', {'form': form, 'next': next_url})


@staff_required
@require_POST
def article_revert(request, slug):
    article = get_object_or_404(Article, slug=slug)
    target = get_object_or_404(Revision, article=article, pk=request.POST.get('target'))
    try:
        new = editorial.revert(
            article, target, request.user, reason=request.POST.get('reason', ''),
            expected_current_id=request.POST.get('expected_current', ''),
        )
    except (EditorialError, block_rules.ValidationError) as exc:
        _flash_error(request, exc)
        return redirect('history', slug=slug)
    messages.success(request, f'Reverted: {target.label} restored as new revision {new.label}. History is kept.')
    return redirect('history', slug=slug)


# ----- Proposals --------------------------------------------------------------------------------------

@login_required
def proposals(request):
    status = request.GET.get('status', 'open')
    qs = Proposal.objects.select_related('article', 'article__published', 'base', 'candidate')
    if status == 'open':
        qs = qs.filter(status__in=['pending', 'approved', 'revision_requested'])
    elif status != 'all':
        qs = qs.filter(status=status)
    show_eval = request.GET.get('origin') == 'evaluation'
    qs = qs.filter(origin='evaluation') if show_eval else qs.exclude(origin='evaluation')
    return render(request, 'core/proposals.html', {
        'proposals': qs, 'status': status, 'show_eval': show_eval,
        'status_choices': Proposal.STATUS,
    })


def _review_rows(proposal):
    roles = {key: label for key, label, _ in configs.REVIEW_ROLES}
    rows = []
    for review in proposal.reviews.select_related('job').all():
        rows.append({'review': review, 'label': roles.get(review.role, review.role)})
    return rows


@login_required
def proposal_detail(request, pk):
    proposal = get_object_or_404(
        Proposal.objects.select_related('article', 'article__published', 'base', 'candidate', 'repeat_of'), pk=pk)
    base_blocks = {str(b.block_id): b for b in proposal.base.blocks.all()} if proposal.base else {}
    cand_blocks = list(proposal.candidate.blocks.order_by('position'))
    diffs = []
    for block in cand_blocks:
        before = base_blocks.get(str(block.block_id))
        if before is None:
            diffs.append({'status': 'added', 'after_html': render_block(block.kind, block.data), 'block': block})
        elif before.kind == block.kind and before.data == block.data:
            diffs.append({'status': 'unchanged', 'after_html': render_block(block.kind, block.data), 'block': block})
        elif block.kind == 'markdown' and before.kind == 'markdown':
            diffs.append({'status': 'changed', 'text_diff': word_diff_html(before.data.get('text', ''), block.data.get('text', '')), 'block': block})
        else:
            diffs.append({'status': 'changed', 'before_html': render_block(before.kind, before.data),
                          'after_html': render_block(block.kind, block.data), 'block': block})
    cand_ids = {str(b.block_id) for b in cand_blocks}
    for bid, before in base_blocks.items():
        if bid not in cand_ids:
            diffs.append({'status': 'removed', 'before_html': render_block(before.kind, before.data), 'block': before})
    title_diff = word_diff_html(proposal.base.title if proposal.base else '', proposal.candidate.title)
    cand_citations = proposal.candidate.citations.select_related('source')
    reviews = _review_rows(proposal)
    policy = configs.active_policy()
    open_for_decision = proposal.status in ('pending', 'approved')
    reviewer_count = len(reviews)
    roles_available = configs.REVIEW_ROLES
    reviews_list = list(proposal.reviews.all())
    claim_rows = []
    for claim in proposal.candidate.claims.prefetch_related('citations__source'):
        citations = []
        for c in claim.citations.all():
            snap = c.source.snapshots.order_by('-created_at').first()
            citations.append({
                'source': c.source, 'supports': c.supports, 'quote': c.quote, 'stance': c.stance,
                'strength': c.strength, 'sha256': snap.sha256 if snap else '',
            })
        objections = []
        for review in reviews_list:
            entry = (review.claim_verdicts or {}).get(str(claim.pk))
            if entry:
                objections.append({'review': review, 'entry': entry})
        claim_rows.append({'claim': claim, 'citations': citations, 'objections': objections})
    return render(request, 'core/proposal.html', {
        'proposal': proposal,
        'diffs': diffs,
        'title_diff': title_diff,
        'citations': cand_citations,
        'reviews': reviews,
        'claim_rows': claim_rows,
        'outcome': editorial.panel_outcome(list(proposal.reviews.all()), policy),
        'policy': policy,
        'can_publish': proposal.status == 'approved' and not proposal.is_stale and proposal.origin != 'evaluation',
        'open_for_decision': open_for_decision,
        'reviewer_count': reviewer_count,
        'roles_available': roles_available,
        'selection_form': _selection_context(),
        'jobs': proposal.jobs.order_by('-created_at')[:5],
    })


@staff_required
@require_POST
def proposal_decide(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    decision = request.POST.get('decision', '')
    try:
        editorial.decide(proposal, request.user, decision, request.POST.get('note', ''))
    except (EditorialError, block_rules.ValidationError) as exc:
        _flash_error(request, exc)
    else:
        messages.success(request, {
            'approve': 'Approved. Publishing is a separate step and checks the base again.',
            'reject': 'Rejected. The candidate is kept for the record.',
            'request_revision': 'Revision requested. The author can open a new draft and propose again.',
        }.get(decision, 'Decision recorded.'))
    return redirect('proposal', pk=pk)


@staff_required
@require_POST
def proposal_publish(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    try:
        revision = editorial.publish(proposal, request.user)
    except ConflictError as exc:
        messages.error(request, str(exc))
    except (EditorialError, block_rules.ValidationError) as exc:
        _flash_error(request, exc)
    else:
        messages.success(request, f'Published {revision.label}. The previous revision stays in history.')
        return redirect('article', slug=proposal.article.slug)
    return redirect('proposal', pk=pk)


# ----- Workshop -------------------------------------------------------------------------------------

def _selection_context():
    """Choices for the five configuration selectors, defaults first."""
    result = {}
    for kind, _label in ConfigVersion.KINDS:
        versions = ConfigVersion.objects.filter(kind=kind).order_by('family', '-version')
        default = configs.default_version(kind)
        result[kind] = {
            'choices': [(str(v.pk), f'{v.name} · v{v.version}' + (' · default' if v.is_default else '')) for v in versions],
            'initial': str(default.pk) if default else '',
        }
    return result


def _selection_from_post(post):
    selection = {}
    for kind, _label in ConfigVersion.KINDS:
        raw = post.get(f'sel_{kind}', '')
        if raw:
            version = ConfigVersion.objects.filter(pk=raw, kind=kind).first()
            if version is None:
                raise block_rules.ValidationError(f'Unknown {kind} version.')
            selection[kind] = version
    return selection


@login_required
def workshop(request):
    configs.ensure_presets()
    versions = ConfigVersion.objects.all().select_related('parent')
    grouped = []
    for kind, label in ConfigVersion.KINDS:
        grouped.append({'kind': kind, 'label': label, 'versions': [v for v in versions if v.kind == kind]})
    cases = EvalCase.objects.select_related('article').all()
    latest_results = {}
    for result in EvalResult.objects.select_related('case').order_by('case_id', '-id'):
        latest_results.setdefault(result.case_id, result)
    case_rows = [{'case': c, 'result': latest_results.get(c.pk)} for c in cases]
    model_list, model_error = configs.discover_models()
    effective = {kind: configs.default_version(kind) for kind, _ in ConfigVersion.KINDS}
    return render(request, 'core/workshop.html', {
        'grouped': grouped,
        'selection': _selection_context(),
        'articles': Article.objects.filter(published__isnull=False).order_by('title'),
        'proposals': Proposal.objects.filter(status='pending').exclude(origin='evaluation').select_related('article'),
        'case_rows': case_rows,
        'recent_jobs': Job.objects.order_by('-created_at')[:6],
        'model_error': model_error,
        'model_count': len(model_list),
        'effective': effective,
        'simulated_cases': EvalCase.objects.exclude(scenario={}),
        'role_labels': configs.REVIEW_ROLES,
        'agents': Agent.objects.filter(is_active=True).order_by('name'),
        'agent_count': Agent.objects.filter(is_active=True).count(),
    })


@staff_required
@require_POST
def workshop_run(request, op):
    try:
        selection = _selection_from_post(request.POST)
        snapshot = configs.resolve_snapshot(selection)
        runner_name = snapshot['runner']['data'].get('runner', 'simulated')
        if op == 'research':
            topic = request.POST.get('topic', '').strip()
            if not topic:
                raise block_rules.ValidationError('Give the topic to research.')
            job = jobs.enqueue('research_draft', user=request.user, runner_name=runner_name,
                               input={'topic': topic, 'notes': request.POST.get('notes', '')[:2000]},
                               label=f'Research and draft: {topic}', selection=selection)
        elif op == 'propose':
            article = get_object_or_404(Article, pk=request.POST.get('article'))
            if article.published_id is None:
                raise block_rules.ValidationError('Publish a first revision before proposing an improvement.')
            request_text = request.POST.get('request', '').strip()
            if not request_text:
                raise block_rules.ValidationError('Describe the improvement you want.')
            case_id = request.POST.get('scenario_case', '')
            if runner_name == 'simulated' and not case_id:
                raise block_rules.ValidationError('The SIMULATED runner needs a scripted scenario. Pick one.')
            job = jobs.enqueue('propose_edit', user=request.user, runner_name=runner_name,
                               input={'request': request_text, 'run_review': bool(request.POST.get('run_review')),
                                      'scenario_case': case_id},
                               label=f'Propose improvement: {article.title}', article=article, selection=selection)
        elif op == 'review':
            proposal = get_object_or_404(Proposal, pk=request.POST.get('proposal'))
            if proposal.status != 'pending':
                raise block_rules.ValidationError('Only proposals awaiting a decision can be reviewed.')
            job = jobs.enqueue('review_proposal', user=request.user, runner_name=runner_name, input={},
                               label=f'Review panel: {proposal.article.title}', article=proposal.article,
                               proposal=proposal, selection=selection)
        elif op == 'agent_cycle':
            if runner_name != 'opencode':
                raise block_rules.ValidationError('The agent cycle needs the OpenCode runner. SIMULATED output is not evidence.')
            topic = request.POST.get('topic', '').strip()
            question = request.POST.get('question', '').strip()
            if not 3 <= len(topic) <= 200 or not 3 <= len(question) <= 500:
                raise block_rules.ValidationError('Give a topic (3-200) and a narrow question (3-500).')
            agent = Agent.objects.filter(pk=request.POST.get('agent'), is_active=True).first()
            if agent is None:
                raise block_rules.ValidationError('Choose an active agent identity. Create one with manage.py create_agent.')
            job = jobs.enqueue('agent_cycle', user=agent.operator, runner_name='opencode',
                               input={'topic': topic, 'question': question, 'agent_id': str(agent.pk)},
                               label=f'Agent cycle: {topic}', selection=selection)
        elif op == 'eval':
            case_ids = request.POST.getlist('case_ids')
            if not case_ids:
                raise block_rules.ValidationError('Select at least one test case.')
            job = jobs.enqueue('run_eval', user=request.user, runner_name=runner_name,
                               input={'case_ids': case_ids}, label=f'Editorial test run ({len(case_ids)} cases)',
                               selection=selection)
        else:
            raise Http404()
    except (block_rules.ValidationError, EditorialError) as exc:
        _flash_error(request, exc)
        return redirect('workshop')
    messages.success(request, f'Queued: {job.label}. The worker will start it. Closing this page will not stop it.')
    return redirect('job_detail', pk=job.pk)


@staff_required
@require_POST
def config_new(request):
    """Create a new family from defaults or duplicate an existing one."""
    source = get_object_or_404(ConfigVersion, pk=request.POST.get('source'))
    count = ConfigVersion.objects.filter(kind=source.kind, family__startswith=f'{source.family}-copy').count()
    family = f'{source.family}-copy' + (f'-{count + 1}' if count else '')
    ConfigVersion.objects.create(
        kind=source.kind, family=family, name=f'{source.name} (copy)', version=1, data=dict(source.data),
        description=f'Duplicate of {source.name} v{source.version}. Edit and save as a new version.',
        provisional=True, parent=source, created_by=request.user,
    )
    messages.success(request, f'Duplicated "{source.name}" as {family}.')
    return redirect('workshop')


@staff_required
def config_edit(request, pk):
    version = get_object_or_404(ConfigVersion, pk=pk)
    if version.proposal_only:
        messages.error(request, 'This is a policy proposal, not an accepted configuration. Duplicate it to experiment.')
        return redirect('workshop')
    if request.method == 'POST':
        form = configs.build_form(version.kind, data=request.POST, initial_data=version.data)
        if form.is_valid():
            cleaned = dict(form.cleaned_data)
            if version.kind == 'reviewers':
                cleaned = _coerce_reviewers(cleaned)
            warning = configs.validate_runner_data(cleaned) if version.kind == 'runner' else ''
            with transaction.atomic():
                next_version = ConfigVersion.objects.filter(kind=version.kind, family=version.family).order_by('-version').first().version + 1
                ConfigVersion.objects.create(
                    kind=version.kind, family=version.family, name=version.name, version=next_version, data=cleaned,
                    description=request.POST.get('description', version.description)[:2000], provisional=True,
                    parent=version, created_by=request.user,
                )
            messages.success(request, f'Saved as {version.name} v{next_version}. Earlier versions are kept.')
            if warning:
                messages.warning(request, warning)
            return redirect('workshop')
        messages.error(request, 'Fix the highlighted fields. Nothing was saved.')
    else:
        form = configs.build_form(version.kind, initial_data=version.data)
    return render(request, 'core/config_form.html', {
        'version': version, 'form': form, 'kind_label': dict(ConfigVersion.KINDS)[version.kind],
        'role_labels': configs.REVIEW_ROLES,
        'versions': ConfigVersion.objects.filter(kind=version.kind, family=version.family).order_by('-version'),
    })


def _coerce_reviewers(cleaned):
    out = {'panel_size': cleaned['panel_size']}
    for key in configs.ROLE_KEYS:
        out[f'{key}__enabled'] = bool(cleaned.get(f'{key}__enabled'))
        out[f'{key}__model'] = cleaned.get(f'{key}__model')
        out[f'{key}__instructions'] = cleaned.get(f'{key}__instructions')
    return out


@staff_required
@require_POST
def config_default(request, pk):
    version = get_object_or_404(ConfigVersion, pk=pk)
    if version.proposal_only:
        messages.error(request, 'A policy proposal cannot be made the default. Duplicate it to experiment.')
        return redirect('workshop')
    with transaction.atomic():
        ConfigVersion.objects.filter(kind=version.kind, is_default=True).update(is_default=False)
        version.is_default = True
        version.save(update_fields=['is_default'])
    messages.success(request, f'{version.name} v{version.version} is now the default for {version.get_kind_display()}.')
    return redirect('workshop')


# ----- Jobs -----------------------------------------------------------------------------------------

@login_required
def job_list(request):
    status = request.GET.get('status', 'all')
    qs = Job.objects.select_related('article', 'proposal')
    if status != 'all':
        qs = qs.filter(status=status)
    return render(request, 'core/jobs.html', {'jobs': qs[:200], 'status': status, 'statuses': Job.STATUS})


@login_required
def job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related('article', 'proposal', 'retry_of'), pk=pk)
    events = job.events.all()
    eval_results = job.eval_results.select_related('case', 'proposal') if job.kind == 'run_eval' else []
    reviews = job.reviews.select_related('proposal') if job.kind == 'review_proposal' else []
    agent_runs = job.agent_runs.select_related('agent')
    return render(request, 'core/job_detail.html', {
        'job': job,
        'events': events,
        'eval_results': eval_results,
        'reviews': reviews,
        'active': job.status in ('queued', 'running'),
        'config': job.config_snapshot,
        'usage_measured': bool(job.usage),
        'agent_runs': agent_runs,
    })


@staff_required
@require_POST
def job_cancel(request, pk):
    job = get_object_or_404(Job, pk=pk)
    try:
        jobs.request_cancel(job)
        messages.success(request, 'Cancellation requested.' if job.status == 'running' else 'Job cancelled.')
    except EditorialError as exc:
        messages.error(request, str(exc))
    return redirect('job_detail', pk=pk)


@staff_required
@require_POST
def job_retry(request, pk):
    job = get_object_or_404(Job, pk=pk)
    try:
        new = jobs.retry(job, request.user)
    except EditorialError as exc:
        messages.error(request, str(exc))
        return redirect('job_detail', pk=pk)
    messages.success(request, 'Retry queued with the same configuration snapshot as the original job.')
    return redirect('job_detail', pk=new.pk)


# ----- Evaluations ----------------------------------------------------------------------------------

@login_required
def evals(request):
    cases = list(EvalCase.objects.select_related('article').all())
    runs = list(Job.objects.filter(kind='run_eval').order_by('-created_at')[:6])
    results = EvalResult.objects.select_related('case', 'proposal').filter(job__in=runs)
    matrix = {}
    for r in results:
        matrix.setdefault(r.case_id, {}).setdefault(str(r.job_id), []).append(r)
    rows = []
    for case in cases:
        cells = []
        for run in runs:
            cells.append({'run': run, 'results': matrix.get(case.pk, {}).get(str(run.pk), [])})
        rows.append({'case': case, 'cells': cells})
    return render(request, 'core/evals.html', {'rows': rows, 'runs': runs, 'cases': cases})


# ----- Policy lab ------------------------------------------------------------------------------------

def lab_view(request):
    """Read the latest policy-lab report written by `manage.py run_policy_lab`."""
    from pathlib import Path as _Path
    from django.conf import settings as _settings
    from . import policy_lab

    path = _Path(_settings.GALACTICA['RUNTIME_DIR']) / 'lab' / 'latest.json'
    report, error = None, None
    try:
        report = json.loads(path.read_text())
    except FileNotFoundError:
        pass
    except (OSError, json.JSONDecodeError) as exc:
        error = str(exc)

    panels = []
    if report:
        for section in report.get('panels', []):
            cells = {(c['policy'], c['risk_class']): c for c in section.get('cells', [])}
            rows = [
                {
                    'policy': policy,
                    'cells': [cells.get((policy, risk)) for risk in policy_lab.RISK_CLASSES],
                }
                for policy in report.get('policies', [])
            ]
            panels.append({'section': section, 'rows': rows})
    return render(request, 'core/lab.html', {
        'report': report,
        'panels': panels,
        'error': error,
        'risk_classes': policy_lab.RISK_CLASSES,
        'report_path': str(path),
    })


# ----- Activity -------------------------------------------------------------------------------------

def health(request):
    return JsonResponse({'ok': True, 'time': timezone.now().isoformat()})
