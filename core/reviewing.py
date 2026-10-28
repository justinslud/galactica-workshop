"""Job handlers: research/draft, propose an edit, review a proposal, run editorial test cases.

Every handler changes content only through core.editorial. The runner supplies JSON; this module validates it and turns
it into revisions, proposals and reviews. Reviewers receive only the proposal and base, never each other's verdicts.
"""
from django.utils import timezone

from . import blocks as block_rules
from . import configs, editorial
from .models import Article, EvalCase, EvalResult, Proposal, Review, Revision, Source
from .runners import RunnerError, Task
from .scenarios import ScenarioError, apply_scenario


def snap_side(revision):
    return {
        'title': revision.title,
        'opening': revision.opening,
        'blocks': [
            {'block_id': str(b.block_id), 'kind': b.kind, 'data': dict(b.data)}
            for b in revision.blocks.order_by('position')
        ],
        'citations': [
            {'block_id': str(c.block_id), 'source_title': c.source.title, 'supports': c.supports, 'quote': c.quote}
            for c in revision.citations.select_related('source')
        ],
    }


def source_registry():
    return [
        {'title': s.title, 'url': s.url, 'kind': s.kind, 'check_status': s.check_status, 'publisher': s.publisher,
         'published_on': s.published_on}
        for s in Source.objects.order_by('title')
    ]


def _call(ctx, kind, payload, *, role='', label=''):
    task = Task(kind=kind, model=payload.pop('_model'), payload=payload, role=role, label=label)
    return ctx.runner.call(ctx, task)


def _snap(ctx, key):
    return ctx.job.config_snapshot[key]['data']


def _runner_model(ctx, role_model=None):
    runner_cfg = _snap(ctx, 'runner')
    if ctx.runner.name == 'simulated':
        return configs.SIMULATED_MODEL
    model = role_model if role_model and role_model != configs.SIMULATED_MODEL else runner_cfg.get('model')
    if not model or model == configs.SIMULATED_MODEL:
        raise RunnerError('The runner configuration names no real model. Pick one in a runner version.')
    return model


def _timeout(ctx):
    return _snap(ctx, 'runner').get('call_timeout_seconds', 180)


def run_draft(ctx):
    inst = _snap(ctx, 'instructions')
    topic = (ctx.job.input.get('topic') or '').strip()
    if not topic:
        raise block_rules.ValidationError('Topic is required.')
    result = _call(ctx, 'draft', {
        '_model': _runner_model(ctx), 'topic': topic, 'notes': ctx.job.input.get('notes', ''),
        'instructions': inst['drafting'], 'preamble': '', 'call_timeout': _timeout(ctx),
    }, label=topic)
    ctx.log(f'Draft received: {result.get("title", "")[:80]!r} ({len(result["blocks"])} blocks)')
    provenance = 'simulated' if ctx.runner.name == 'simulated' else 'workshop'
    article = editorial.create_article(
        title=result['title'], user=ctx.job.created_by, provenance=provenance,
        opening=result.get('opening', ''),
    )
    draft = article.revisions.get(state='draft')
    editorial.save_draft(
        draft, ctx.job.created_by, title=result['title'], opening=result.get('opening', ''),
        items=[{'block_id': None, 'kind': b.get('kind'), 'data': b.get('data')} for b in result['blocks']],
        citations=[], expected_version=draft.version,
    )
    ctx.job.article = article
    ctx.job.save(update_fields=['article'])
    return {'article': article.slug, 'revision': draft.label, 'draft_id': str(draft.pk),
            'runner': ctx.runner.name, 'provenance': provenance}


def _changed_ids(base_items, cand_items):
    base_map = {i['block_id']: i for i in base_items}
    changed = []
    for item in cand_items:
        old = base_map.get(item['block_id'])
        if old is None or old['kind'] != item['kind'] or old['data'] != item['data']:
            changed.append(item['block_id'])
    return changed


def _resolve_candidate(base, returned_blocks, returned_citations, runner_name, scenario_citations=None):
    """Merge a runner's edit into full candidate content. Returns (items, citations)."""
    base_items = [{'block_id': str(b.block_id), 'kind': b.kind, 'data': dict(b.data)} for b in base.blocks.order_by('position')]
    by_id = {i['block_id']: i for i in base_items}
    merged = list(base_items)
    for block in returned_blocks:
        bid = block.get('block_id')
        if bid and bid in by_id:
            for item in merged:
                if item['block_id'] == bid:
                    item['kind'] = block.get('kind', item['kind'])
                    item['data'] = block.get('data', item['data'])
        else:
            merged.append({'block_id': None, 'kind': block.get('kind'), 'data': block.get('data')})
    citations = [
        {'block_id': str(c.block_id), 'source_id': str(c.source_id), 'supports': c.supports, 'quote': c.quote}
        for c in base.citations.all()
    ]
    for entry in returned_citations:
        if 'position' in entry:
            if not 0 <= entry['position'] < len(merged):
                raise block_rules.ValidationError('A citation points at a block that does not exist.')
            bid = merged[entry['position']]['block_id']
        else:
            bid = entry.get('block_id')
        source = Source.objects.filter(title=entry.get('source_title', '')).first()
        if source is None:
            raise block_rules.ValidationError(f'Citation names an unregistered source: {entry.get("source_title", "")[:80]!r}.')
        citations.append({'block_id': bid, 'source_id': str(source.pk), 'supports': entry.get('supports', ''),
                          'quote': entry.get('quote', '')})
    return merged, citations


def _candidate_from_edit(ctx, base, result, origin):
    items, citations = _resolve_candidate(base, result['blocks'], result.get('citations', []), origin)
    candidate = editorial.create_candidate(
        base.article, title=base.title, opening=base.opening,
        items=[{'block_id': i['block_id'], 'kind': i['kind'], 'data': i['data']} for i in items],
        citations=citations, origin=origin, user=ctx.job.created_by,
    )
    return candidate, _changed_ids(
        [{'block_id': str(b.block_id), 'kind': b.kind, 'data': b.data} for b in base.blocks.all()],
        [{'block_id': i['block_id'] or '', 'kind': i['kind'], 'data': i['data']} for i in items],
    )


def run_propose(ctx):
    article = ctx.job.article
    base = article.published if article else None
    if base is None:
        raise RunnerError('Article has no published revision to improve.')
    inst = _snap(ctx, 'instructions')
    scenario = {}
    if ctx.runner.name == 'simulated':
        scenario = ctx.job.input.get('scenario')
        if not scenario:
            case_id = ctx.job.input.get('scenario_case')
            case = EvalCase.objects.filter(pk=case_id).first() if case_id else None
            if case is None:
                raise RunnerError('SIMULATED runner needs a scripted scenario. Pick a test case that defines one.')
            scenario = case.scenario['candidates'][0]
        if 'candidates' in scenario:
            scenario = scenario['candidates'][0]
        ctx.log('SIMULATED edit: applying a scripted scenario (no model is called).')
    result = _call(ctx, 'edit', {
        '_model': _runner_model(ctx), 'base': snap_side(base), 'sources': source_registry(),
        'request': ctx.job.input.get('request', ''), 'scenario': scenario,
        'instructions': inst['edit'], 'preamble': inst['review_preamble'], 'call_timeout': _timeout(ctx),
    }, label='proposal')
    ctx.log(f'Edit proposed: {result["rationale"][:120]}')
    candidate, changed = _candidate_from_edit(ctx, base, result, ctx.runner.name)
    proposal = editorial.open_proposal(
        candidate, rationale=result['rationale'], origin=ctx.runner.name, user=ctx.job.created_by,
    )
    ctx.job.proposal = proposal
    ctx.job.save(update_fields=['proposal'])
    ctx.log(f'Opened proposal {str(proposal.pk)[:8]} against {base.label}; changed blocks: {len(changed)}.')
    output = {'proposal': str(proposal.pk), 'candidate': candidate.label, 'changed_blocks': changed}
    if ctx.job.input.get('run_review'):
        from .jobs import enqueue_review
        review_job = enqueue_review(proposal, user=ctx.job.created_by, runner=ctx.runner.name,
                                    config_snapshot=ctx.job.config_snapshot)
        output['review_job'] = str(review_job.pk)
        ctx.log(f'Queued review panel job {str(review_job.pk)[:8]}.')
    return output


def run_panel(ctx, proposal, reviewers_snapshot, instructions_snapshot):
    """Run each enabled role in a fresh session. Existing reviews are kept, so a retry resumes."""
    roles = configs.panel_roles(reviewers_snapshot)
    if not roles:
        raise RunnerError('The reviewer panel has no enabled roles.')
    base = proposal.base
    if base is None:
        raise RunnerError('Proposal has no base revision.')
    candidate = proposal.candidate
    repeat_note = ''
    if proposal.repeat_of_id:
        repeat_note = (
            f'This proposal repeats a proposal that was already rejected (proposal {str(proposal.repeat_of_id)[:8]}). '
            'Object unless the author explains what is new.'
        )
    changed = _changed_ids(
        [{'block_id': str(b.block_id), 'kind': b.kind, 'data': b.data} for b in base.blocks.all()],
        [{'block_id': str(b.block_id), 'kind': b.kind, 'data': b.data} for b in candidate.blocks.all()],
    )
    for role in roles:
        ctx.check()
        if proposal.reviews.filter(role=role['key']).exists():
            ctx.log(f'Reviewer {role["label"]} already recorded; skipping (resumed run).')
            continue
        model = _runner_model(ctx, role['model'])
        result = _call(ctx, 'review', {
            '_model': model, 'instructions': role['instructions'], 'preamble': instructions_snapshot['review_preamble'],
            'base': snap_side(base), 'candidate': snap_side(candidate), 'rationale': proposal.rationale,
            'repeat_note': repeat_note, 'changed_block_ids': changed, 'sources': source_registry(),
            'call_timeout': _timeout(ctx),
        }, role=role['key'], label=role['label'])
        declared = 'simulated' if ctx.runner.name == 'simulated' else model
        editorial.record_review(
            proposal, role=role['key'], verdict=result['verdict'], comment=result.get('comment', ''),
            evidence_notes=result.get('evidence_notes', ''), origin=ctx.runner.name,
            declared_model=declared, job=ctx.job,
        )
        ctx.log(f'Reviewer {role["label"]}: {result["verdict"]}')
    return list(proposal.reviews.all())


def run_review_job(ctx):
    proposal = Proposal.objects.select_related('base', 'candidate', 'article').get(pk=ctx.job.proposal_id)
    reviews = run_panel(ctx, proposal, _snap(ctx, 'reviewers'), _snap(ctx, 'instructions'))
    policy = _snap(ctx, 'policy')
    outcome = editorial.panel_outcome(reviews, policy)
    ctx.log(f'Panel outcome: {outcome}. A staff member still decides.')
    return {'proposal': str(proposal.pk), 'reviews': len(reviews), 'outcome': outcome}


def run_eval(ctx):
    cases = EvalCase.objects.select_related('article').all()
    chosen = ctx.job.input.get('case_ids') or []
    if chosen:
        cases = cases.filter(pk__in=chosen)
    cases = list(cases)
    if not cases:
        raise RunnerError('No test cases selected.')
    reviewers, instructions = _snap(ctx, 'reviewers'), _snap(ctx, 'instructions')
    policy = _snap(ctx, 'policy')
    summary = []
    for case in cases:
        ctx.check()
        base = case.article.published
        if base is None:
            ctx.log(f'Skipping {case.name!r}: article has no published revision.', 'warn')
            continue
        for candidate_spec in case.scenario.get('candidates', []):
            ctx.check()
            label = candidate_spec.get('label', 'A')
            try:
                items = apply_scenario(
                    [{'block_id': str(b.block_id), 'kind': b.kind, 'data': dict(b.data)} for b in base.blocks.order_by('position')],
                    candidate_spec,
                )
            except ScenarioError as exc:
                ctx.log(f'{case.name} [{label}]: skipped. {exc} Rewrite this case for the current revision.', 'warn')
                summary.append({'case': case.slug, 'candidate': label, 'outcome': 'skipped', 'matches': None})
                continue
            base_citations = [
                {'block_id': str(c.block_id), 'source_id': str(c.source_id), 'supports': c.supports, 'quote': c.quote}
                for c in base.citations.all()
            ]
            new_citations = []
            for cit in candidate_spec.get('citations', []):
                source = Source.objects.filter(title=cit['source_title']).first()
                if source is None:
                    raise RunnerError(f'Case {case.name!r} cites an unregistered source.')
                new_citations.append({'block_id': items[cit['position']]['block_id'], 'source_id': str(source.pk),
                                      'supports': cit['supports'], 'quote': cit.get('quote', '')})
            candidate = editorial.create_candidate(
                case.article, title=base.title, opening=base.opening,
                items=[{'block_id': i['block_id'], 'kind': i['kind'], 'data': i['data']} for i in items],
                citations=base_citations + new_citations, origin='evaluation', user=ctx.job.created_by,
            )
            proposal = editorial.open_proposal(
                candidate, rationale=candidate_spec.get('rationale', f'Evaluation candidate {label} for {case.name}.'),
                origin='evaluation', user=None, eval_case=case,
            )
            reviews = run_panel(ctx, proposal, reviewers, instructions)
            outcome = editorial.panel_outcome(reviews, policy)
            expected = case.expected
            matches = None if expected == 'unknown' else outcome == expected
            EvalResult.objects.create(
                job=ctx.job, case=case, candidate_label=label, proposal=proposal, outcome=outcome,
                verdicts={r.role: r.verdict for r in reviews}, expected=expected, matches=matches,
            )
            ctx.log(f'{case.name} [{label}]: outcome {outcome}; expected {expected}; match {matches}.')
            summary.append({'case': case.slug, 'candidate': label, 'outcome': outcome, 'matches': matches})
    return {'results': summary, 'cases': len(cases)}




# ----- Bounded agent editorial cycle ---------------------------------------------------------------

AGENT_RESEARCH_TASK = 'research_plan'
AGENT_WRITER_TASK = 'write_evidence'
AGENT_REVIEW_TASK = 'review_evidence'


def _config_refs(snapshot):
    return {
        kind: {'id': value.get('id'), 'name': value.get('name'), 'version': value.get('version')}
        for kind, value in (snapshot or {}).items()
    }


def _resolve_agent(ctx):
    from .models import Agent

    agent_id = (ctx.job.input or {}).get('agent_id')
    agent = Agent.objects.filter(pk=agent_id, is_active=True).first() if agent_id else None
    if agent is None and agent_id:
        raise RunnerError('The requested agent identity is missing or inactive.')
    return agent


def _start_run(ctx, agent, profile, role, model):
    from .models import AgentRun

    return AgentRun.objects.create(
        job=ctx.job, agent=agent, profile=profile, role=role, model=model,
        model_variant=_snap(ctx, 'runner').get('variant', ''),
        config_versions=_config_refs(ctx.job.config_snapshot), status='running',
    )


def _finish_run(run, status, usage=None, error=''):
    from django.utils import timezone

    usage = usage or {}
    measured = bool(usage and (usage.get('calls') or usage.get('input_tokens') or usage.get('output_tokens')))
    run.status = status
    run.finished_at = timezone.now()
    run.error = (error or '')[:1000]
    run.usage = usage
    run.usage_measured = measured
    run.usage_note = (usage.get('source', '') if measured
                      else 'OpenCode reported no token usage for this call.')[:200]
    run.save(update_fields=['status', 'finished_at', 'error', 'usage', 'usage_measured', 'usage_note'])


def _run_task(ctx, run, task):
    from .models import Job

    before = Job.objects.get(pk=ctx.job.pk).usage or {}
    try:
        result = ctx.runner.call(ctx, task)
    except Exception as exc:
        _finish_run(run, 'failed', error=str(exc))
        raise
    after = Job.objects.get(pk=ctx.job.pk).usage or {}
    delta = {}
    for key, value in after.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            old = before.get(key, 0) if isinstance(before.get(key, 0), (int, float)) else 0
            if value != old:
                delta[key] = value - old
        elif key not in before:
            delta[key] = value
    _finish_run(run, 'succeeded', usage=delta)
    return result


def _agent_model(ctx, key):
    data = _snap(ctx, 'runner')
    model = data.get(key) or data.get('model')
    if not model or model == configs.SIMULATED_MODEL:
        raise RunnerError(f'The {key.replace("_", " ")} is not a real model. Agent cycles need an OpenCode model; '
                          'SIMULATED output is not evidence.')
    return model


def _evidence_packet(snapshots):
    from .models import SourceSnapshot

    packet = []
    for snap in SourceSnapshot.objects.filter(pk__in=[s.pk for s in snapshots]).select_related('source'):
        packet.append({
            'snapshot_id': str(snap.id), 'source_id': str(snap.source_id), 'title': snap.title,
            'url': snap.url, 'final_url': snap.final_url, 'fetched_at': snap.fetched_at.isoformat(),
            'sha256': snap.sha256, 'byte_count': snap.byte_count, 'excerpt': snap.excerpt,
            'extraction_notes': snap.extraction_notes,
        })
    return packet


def _normalise_for_quote(text):
    import re
    return re.sub(r'\s+', ' ', (text or '').lower()).strip()


def _agent_claims(result, snapshots):
    """Validate writer claims and map them to preserved sources. Every claim needs at least one citation."""
    by_title = {snap.source.title: snap for snap in snapshots}
    claims = result.get('claims')
    if not isinstance(claims, list) or not claims:
        raise block_rules.ValidationError('Writer must return a non-empty claims list with quote-backed citations.')
    clean = []
    blocks = result['blocks']
    for index, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            raise block_rules.ValidationError(f'Claim {index} is malformed.')
        try:
            block_index = int(claim.get('block_index'))
        except (TypeError, ValueError):
            raise block_rules.ValidationError(f'Claim {index} needs block_index.')
        if not 0 <= block_index < len(blocks):
            raise block_rules.ValidationError(f'Claim {index} points outside the candidate blocks.')
        text = str(claim.get('text', '')).strip()
        if not 1 <= len(text) <= 1200:
            raise block_rules.ValidationError(f'Claim {index} text is empty or too long.')
        raw_citations = claim.get('citations')
        if not isinstance(raw_citations, list) or not raw_citations:
            raise block_rules.ValidationError(f'Claim {index} has no citation; factual claims may not be uncited.')
        citations = []
        for c_index, citation in enumerate(raw_citations, start=1):
            if not isinstance(citation, dict):
                raise block_rules.ValidationError(f'Claim {index} citation {c_index} is malformed.')
            title = str(citation.get('source_title', '')).strip()
            snap = by_title.get(title)
            if snap is None:
                raise block_rules.ValidationError(
                    f'Claim {index} citation {c_index} names a source not preserved for this job: {title[:80]!r}.')
            quote = str(citation.get('quote', '')).strip()
            if quote and _normalise_for_quote(quote) not in _normalise_for_quote(snap.raw_text):
                raise block_rules.ValidationError(
                    f'Claim {index} citation {c_index} quote does not appear in the preserved snapshot.')
            supports = str(citation.get('supports', '')).strip()
            if not 5 <= len(supports) <= 400:
                raise block_rules.ValidationError(f'Claim {index} citation {c_index} needs a support note (5-400).')
            stance = citation.get('stance', 'supports')
            strength = citation.get('strength', 'direct')
            if stance not in ('supports', 'conflicts', 'context') or strength not in ('direct', 'partial'):
                raise block_rules.ValidationError(f'Claim {index} citation {c_index} has an invalid stance/strength.')
            citations.append({'source_id': snap.source_id, 'supports': supports, 'quote': quote,
                              'stance': stance, 'strength': strength})
        if not any(c['stance'] != 'context' for c in citations):
            raise block_rules.ValidationError(f'Claim {index} has only context citations; it needs support or conflict.')
        clean.append({'block_index': block_index, 'text': text, 'citations': citations})
    return clean


def _claims_from_candidate(proposal, extra_text=None):
    """Copy existing claim-level evidence to a new candidate, optionally adding one uncited claim."""
    claims = []
    blocks = list(proposal.candidate.blocks.order_by('position'))
    index_by_block = {str(b.block_id): i for i, b in enumerate(blocks)}
    for claim in proposal.candidate.claims.prefetch_related('citations'):
        claims.append({
            'block_index': index_by_block[str(claim.block_id)],
            'text': claim.text,
            'citations': [
                {'source_id': str(c.source_id), 'supports': c.supports, 'quote': c.quote,
                 'stance': c.stance, 'strength': c.strength}
                for c in claim.citations.all()
            ],
        })
    if extra_text:
        claims.append({'block_index': len(blocks), 'text': extra_text, 'citations': []})
    return claims


def _run_agent_reviews(ctx, proposal, packet, snapshots, agent, operator, instructions, reviewers):
    """Run one fresh reviewer session per role. No reviewer receives another verdict."""
    roles = configs.panel_roles(reviewers, only=configs.AGENT_REVIEW_ROLES)
    if {r['key'] for r in roles} != set(configs.AGENT_REVIEW_ROLES):
        raise RunnerError('The agent cycle needs fact_check, citation and readability reviewers enabled.')
    preamble = instructions['review_preamble']
    candidate_side = snap_side(proposal.candidate)
    claims = list(proposal.candidate.claims.prefetch_related('citations__source'))
    claim_payload = []
    evidence_pairs = []
    for claim in claims:
        citations = []
        for citation in claim.citations.all():
            snap = next((s for s in snapshots if s.source_id == citation.source_id), None)
            citations.append({
                'source_title': citation.source.title, 'supports': citation.supports, 'quote': citation.quote,
                'stance': citation.stance, 'strength': citation.strength,
                'snapshot_sha256': snap.sha256 if snap else '', 'preserved_excerpt': snap.excerpt if snap else '',
            })
            evidence_pairs.append({
                'claim_id': str(claim.pk), 'block_id': str(citation.block_id),
                'source_title': citation.source.title, 'supports': citation.supports, 'quote': citation.quote,
                'preserved_excerpt': snap.excerpt if snap else '', 'sha256': snap.sha256 if snap else '',
            })
        claim_payload.append({
            'claim_id': str(claim.pk), 'text': claim.text, 'support_status': claim.support_status,
            'support_note': claim.support_note, 'citations': citations,
        })
    claim_ids = {str(c.pk) for c in claims}
    reviews = []
    for role in roles:
        ctx.check()
        if role['model'] == configs.SIMULATED_MODEL:
            raise RunnerError(f'Reviewer role {role["key"]} has no real model configured.')
        reviewer_run = _start_run(ctx, agent, 'reviewer', role['key'], role['model'])
        ctx.log(f'Reviewer {role["label"]} using {role["model"]} (fresh session).')
        result = _run_task(ctx, reviewer_run, Task(
            kind=AGENT_REVIEW_TASK, model=role['model'], profile='reviewer', role=role['key'], label=role['label'],
            payload={
                'instructions': role['instructions'], 'preamble': preamble,
                'base': None,
                'candidate': candidate_side,
                'claims': claim_payload,
                'evidence': packet, 'evidence_pairs': evidence_pairs, 'rationale': proposal.rationale,
                'call_timeout': _timeout(ctx),
            },
        ))
        raw_verdicts = result.get('claim_verdicts') or {}
        if not isinstance(raw_verdicts, dict):
            raise RunnerError(f'{role["key"]} returned claim_verdicts that were not an object.')
        clean_verdicts = {}
        for claim_id, entry in raw_verdicts.items():
            if claim_id not in claim_ids:
                raise RunnerError(f'{role["key"]} returned a verdict for an unknown claim id.')
            if not isinstance(entry, dict) or entry.get('verdict') not in dict(Review.VERDICTS):
                raise RunnerError(f'{role["key"]} returned an invalid claim verdict.')
            clean_verdicts[claim_id] = {
                'verdict': entry['verdict'],
                'issue': str(entry.get('issue', ''))[:80],
                'comment': str(entry.get('comment', ''))[:600],
            }
        if role['key'] in ('fact_check', 'citation'):
            missing = claim_ids - set(clean_verdicts)
            if missing:
                raise RunnerError(
                    f'{role["key"]} did not return verdicts for {len(missing)} claim(s); claim-level review is required.')
        review = editorial.record_review(
            proposal, role=role['key'], verdict=result['verdict'], comment=result.get('comment', ''),
            evidence_notes=result.get('evidence_notes', ''), origin='agent', declared_model=role['model'],
            job=ctx.job, agent=agent, agent_run=reviewer_run, operator=operator,
            claim_verdicts=clean_verdicts,
        )
        reviews.append(review)
        objections = sum(1 for v in clean_verdicts.values() if v['verdict'] in ('object', 'concern'))
        ctx.log(f'Reviewer {role["label"]}: {result["verdict"]} ({objections} claim-level concern/objection(s))')
    return reviews, roles


def _run_evaluation_candidate(ctx, real_proposal, packet, snapshots, agent, operator, instructions, reviewers,
                              claim, writer_model):
    """Create a separate, never-publishable candidate with one planted uncited claim and run the same panel."""
    from .models import Proposal

    items = [
        {'block_id': str(b.block_id), 'kind': b.kind, 'data': dict(b.data)}
        for b in real_proposal.candidate.blocks.order_by('position')
    ]
    items.append({'block_id': None, 'kind': 'markdown', 'data': {'text': claim}})
    claims = _claims_from_candidate(real_proposal, extra_text=claim)
    allowed = {s.source_id for s in snapshots}
    candidate = editorial.create_candidate(
        real_proposal.article, title=real_proposal.candidate.title,
        opening=real_proposal.candidate.opening, items=items, citations=[], claims=claims,
        origin='evaluation', user=operator, allowed_source_ids=allowed,
    )
    eval_proposal = editorial.open_proposal(
        candidate,
        rationale=('Evaluation candidate: the real proposal plus one deliberately unsupported, overgeneralized '
                   'claim. It exists only to test reviewer judgment and can never be published.'),
        origin='evaluation', user=operator, agent=agent, origin_job=ctx.job, origin_model=writer_model,
    )
    reviews, roles = _run_agent_reviews(
        ctx, eval_proposal, packet, snapshots, agent, operator, instructions, reviewers,
    )
    policy = _snap(ctx, 'policy')
    outcome = editorial.panel_outcome(reviews, policy)
    planted = candidate.claims.order_by('-position').first()
    ctx.log(f'Adversarial evaluation outcome: {outcome}; verdicts {[r.verdict for r in reviews]}.')
    return {
        'proposal': str(eval_proposal.pk), 'candidate': candidate.label, 'claim': claim,
        'claim_id': str(planted.pk) if planted else '',
        'outcome': outcome, 'reviews': {r.role: r.verdict for r in reviews},
        'claim_verdicts': {r.role: r.claim_verdicts for r in reviews},
        'models': {r['key']: r['model'] for r in roles}, 'publishable': False,
    }


def _evaluate_existing_proposal(ctx):
    """Re-run the planted evaluation against an existing proposal without new research or writing."""
    from .models import Job, Proposal

    job = Job.objects.get(pk=ctx.job.pk)
    real = Proposal.objects.select_related('article', 'candidate').get(pk=job.input['evaluate_proposal'])
    if real.origin not in ('agent', 'human', 'simulated', 'opencode'):
        raise RunnerError('Evaluation source proposal is not a normal editorial proposal.')
    snapshots = []
    seen = set()
    for citation in real.candidate.citations.select_related('source'):
        latest = citation.source.snapshots.order_by('-created_at').first()
        if latest and latest.pk not in seen:
            seen.add(latest.pk)
            snapshots.append(latest)
    if not snapshots:
        raise RunnerError('The source proposal has no preserved snapshots to evaluate against.')
    packet = _evidence_packet(snapshots)
    agent = _resolve_agent(ctx)
    operator = job.created_by or (agent.operator if agent else None)
    evaluation = _run_evaluation_candidate(
        ctx, real, packet, snapshots, agent, operator,
        _snap(ctx, 'instructions'), _snap(ctx, 'reviewers'),
        str(job.input['claim']), real.origin_model or 'not-recorded',
    )
    return {'proposal': str(real.pk), 'evaluation': evaluation, 'status': 'pending human inspection'}


def run_agent_cycle(ctx):
    from .models import AuditEvent, Job, SourceSnapshot
    from .research import ResearchError, intake_config, preserve

    if ctx.runner.name != 'opencode':
        raise RunnerError('The agent editorial cycle needs the OpenCode runner. SIMULATED output is not research.')
    job = Job.objects.select_related('article').get(pk=ctx.job.pk)
    if job.input.get('evaluate_proposal'):
        return _evaluate_existing_proposal(ctx)
    topic = str(job.input.get('topic', '')).strip()
    question = str(job.input.get('question', '')).strip()
    if not 3 <= len(topic) <= 200 or not 3 <= len(question) <= 500:
        raise RunnerError('Agent cycle needs a topic (3-200 chars) and a question (3-500 chars).')
    agent = _resolve_agent(ctx)
    operator = job.created_by
    if operator is None and agent is not None:
        operator = agent.operator
    if operator is None:
        raise RunnerError('Agent cycle has no operator account.')
    research_cfg = intake_config(_snap(ctx, 'research'))
    instructions = _snap(ctx, 'instructions')

    # 1. Researcher suggests URLs. It cannot fetch application evidence and has no shell/edit/subagent permission.
    researcher_model = _agent_model(ctx, 'researcher_model')
    researcher_run = _start_run(ctx, agent, 'researcher', 'research_plan', researcher_model)
    ctx.log(f'Researcher {researcher_model} planning sources (profile researcher).')
    plan = _run_task(ctx, researcher_run, Task(
        kind=AGENT_RESEARCH_TASK, model=researcher_model, profile='researcher', role='research_plan',
        label='Research plan',
        payload={
            'topic': topic, 'question': question, 'allowed_domains': research_cfg['allowed_domains'],
            'max_sources': research_cfg['max_sources'],
            'instructions': (research_cfg.get('research_instructions')
                             or configs.DEFAULTS['research']['research_instructions']),
            'call_timeout': _timeout(ctx),
        },
    ))
    urls = []
    for url in list(job.input.get('seed_urls') or []) + list(plan.get('urls', [])):
        if isinstance(url, str) and url not in urls:
            urls.append(url)
    ctx.log(f'Researcher proposed {len(urls)} URL(s); application intake will validate and preserve them.')

    # 2. Application intake: bounded fetch, private-network refusal, snapshots.
    snapshots, failures = [], []
    for url in urls[:research_cfg['max_sources']]:
        ctx.check()
        try:
            snapshot = preserve(url, research_cfg, topic, question, agent_run=researcher_run)
            snapshots.append(snapshot)
            ctx.log(f'Preserved {snapshot.domain}: {snapshot.byte_count} bytes, sha256 {snapshot.sha256[:12]}.')
        except ResearchError as exc:
            failures.append(f'{url}: {exc}')
            ctx.log(f'Refused or failed: {url} — {exc}', 'warn')
    if not snapshots:
        raise RunnerError('No source was preserved. ' + (failures[0] if failures else 'The researcher returned no usable URLs.'))
    packet = _evidence_packet(snapshots)

    # 3. Writer receives only the preserved packet.
    writer_model = _agent_model(ctx, 'writer_model')
    writer_run = _start_run(ctx, agent, 'writer', 'write_evidence', writer_model)
    ctx.log(f'Writer {writer_model} drafting from {len(packet)} preserved source(s).')
    draft = _run_task(ctx, writer_run, Task(
        kind=AGENT_WRITER_TASK, model=writer_model, profile='writer', role='write_evidence', label='Write from evidence',
        payload={
            'topic': topic, 'question': question, 'evidence': packet,
            'instructions': instructions['drafting'], 'call_timeout': _timeout(ctx),
        },
    ))
    for block in draft.get('blocks', []):
        if block.get('kind') != 'markdown':
            raise block_rules.ValidationError('Agent writer may only return markdown blocks.')
    claims = _agent_claims(draft, snapshots)
    allowed = {s.source_id for s in snapshots}

    article = editorial.create_article(
        title=draft['title'], user=operator, provenance='agent', opening=draft.get('opening', ''),
        open_draft=False, agent=agent, agent_run=writer_run,
    )
    import uuid
    items = [
        {'block_id': str(uuid.uuid4()), 'kind': 'markdown', 'data': block.get('data', {})}
        for block in draft['blocks']
    ]
    candidate = editorial.create_candidate(
        article, title=draft['title'], opening=draft.get('opening', ''), items=items,
        citations=[], claims=claims, origin='agent', user=operator, allowed_source_ids=allowed,
    )
    proposal = editorial.open_proposal(
        candidate, rationale=draft.get('rationale', ''), origin='agent', user=operator, agent=agent,
        agent_run=writer_run, origin_job=job,
    )
    Job.objects.filter(pk=job.pk).update(article=article, proposal=proposal)
    ctx.log(f'Proposal {str(proposal.pk)[:8]} opened against a new article; left pending.')

    # 4. Three isolated reviews, then an optional separate adversarial evaluation candidate.
    reviews, roles = _run_agent_reviews(
        ctx, proposal, packet, snapshots, agent, operator,
        _snap(ctx, 'instructions'), _snap(ctx, 'reviewers'),
    )
    evaluation = None
    if (job.input or {}).get('evaluation_claim'):
        evaluation = _run_evaluation_candidate(
            ctx, proposal, packet, snapshots, agent, operator,
            _snap(ctx, 'instructions'), _snap(ctx, 'reviewers'),
            str(job.input['evaluation_claim']), writer_model,
        )

    AuditEvent.objects.create(
        article=article, job=job, proposal=proposal, actor=operator, agent=agent, agent_run=writer_run,
        model=writer_model, config_versions=_config_refs(job.config_snapshot), action='agent_cycle_completed',
        reason=f'{len(snapshots)} source(s), {len(reviews)} review(s); proposal left pending.',
        detail={'snapshots': [str(s.id) for s in snapshots], 'reviewers': {
            r.role: r.verdict for r in reviews}, 'models': {
            'researcher': researcher_model, 'writer': writer_model,
            'reviewers': {r['key']: r['model'] for r in roles}},
            'evaluation': evaluation,
        },
    )
    return {
        'article': article.slug, 'proposal': str(proposal.pk), 'candidate': candidate.label,
        'snapshots': [{'id': str(s.id), 'url': s.final_url, 'sha256': s.sha256, 'title': s.title} for s in snapshots],
        'failures': failures,
        'reviews': {r.role: r.verdict for r in reviews},
        'models': {'researcher': researcher_model, 'writer': writer_model,
                   'reviewers': {r['key']: r['model'] for r in roles}},
        'evaluation': evaluation,
        'status': 'pending human inspection',
    }


HANDLERS = {
    'agent_cycle': run_agent_cycle,
    'research_draft': run_draft,
    'propose_edit': run_propose,
    'review_proposal': run_review_job,
    'run_eval': run_eval,
}
