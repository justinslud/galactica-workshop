"""Editorial services. Views, runners, jobs and the seed command all change content through here.

Rules enforced here, not in templates or admin:
- Published revisions are immutable. Only a draft can be edited.
- Publishing and reverting lock the article, refuse stale bases, and write an audit event
  in the same transaction as the change.
- Revert creates a new revision; history is never erased.
"""
import hashlib
import json

from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.text import slugify

from . import blocks as block_rules
from .models import Article, AuditEvent, Block, Citation, Claim, EvalCase, Proposal, Review, Revision, Source


class EditorialError(Exception):
    """A rule was violated. The message is safe to show to the user."""


class PermissionDeniedError(EditorialError):
    pass


class ConflictError(EditorialError):
    """The draft or proposal changed underneath the user."""


class StaleProposalError(ConflictError):
    """The target revision is no longer the published one."""


DEFAULT_BLOCK = {'block_id': None, 'kind': 'markdown', 'data': {'text': 'Start writing here.'}}


def require_login(user):
    if not (user and user.is_authenticated):
        raise PermissionDeniedError('Log in to do this.')


def require_staff(user):
    require_login(user)
    if not user.is_staff:
        raise PermissionDeniedError('Staff account required for this action.')


def _actor(user):
    return user if (user and user.is_authenticated) else None


def _audit(article, action, *, actor=None, agent=None, agent_run=None, model='', reason='', revision=None,
           proposal=None, job=None, detail=None):
    return AuditEvent.objects.create(
        article=article, action=action, actor=_actor(actor), agent=agent, agent_run=agent_run,
        model=(model or getattr(agent_run, 'model', '') or ''),
        config_versions=(getattr(agent_run, 'config_versions', {}) or {}), reason=reason,
        revision=revision, proposal=proposal, job=job, detail=detail or {},
    )


def next_number(article):
    last = article.revisions.order_by('-number').values_list('number', flat=True).first()
    return (last or 0) + 1


def content_hash(revision):
    snapshot = {
        'title': revision.title,
        'opening': revision.opening,
        'blocks': [
            {'block_id': str(b.block_id), 'kind': b.kind, 'data': b.data}
            for b in revision.blocks.order_by('position')
        ],
        'citations': sorted(
            [
                {'block_id': str(c.block_id), 'source': str(c.source_id), 'supports': c.supports, 'quote': c.quote}
                for c in revision.citations.all()
            ],
            key=lambda c: json.dumps(c, sort_keys=True),
        ),
    }
    return hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()


def _write_content(revision, items, citations):
    """items: validated blocks with block_id set. citations: list of dicts. Replaces all content."""
    revision.blocks.all().delete()
    revision.citations.all().delete()
    Block.objects.bulk_create([
        Block(revision=revision, block_id=item['block_id'], position=index, kind=item['kind'], data=item['data'])
        for index, item in enumerate(items)
    ])
    Citation.objects.bulk_create([
        Citation(
            revision=revision, block_id=c['block_id'], source_id=c['source_id'],
            supports=c['supports'], quote=c.get('quote', ''),
        )
        for c in citations
    ])


def _validate_citations(raw, items, allowed_source_ids=None):
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise block_rules.ValidationError('Evidence must be a list.')
    block_ids = {str(i['block_id']) for i in items if i['block_id']}
    clean = []
    for index, entry in enumerate(raw, start=1):
        if not isinstance(entry, dict):
            raise block_rules.ValidationError(f'Evidence {index} is malformed.')
        block_id = str(entry.get('block_id', ''))
        if block_id not in block_ids:
            raise block_rules.ValidationError(f'Evidence {index} points at a block that is not in this article.')
        try:
            source = Source.objects.get(pk=entry.get('source_id'))
        except (Source.DoesNotExist, ValueError, TypeError):
            raise block_rules.ValidationError(f'Evidence {index} cites an unknown source.')
        if allowed_source_ids is not None and source.pk not in allowed_source_ids:
            raise block_rules.ValidationError(f'Evidence {index} cites a source not preserved for this job.')
        supports = str(entry.get('supports', '')).strip()
        if not supports or len(supports) > 400:
            raise block_rules.ValidationError(f'Evidence {index} needs a note of what it supports (max 400 characters).')
        quote = str(entry.get('quote', '')).strip()
        if len(quote) > 600:
            raise block_rules.ValidationError(f'Evidence {index} quote is longer than 600 characters.')
        clean.append({'block_id': block_id, 'source_id': source.pk, 'supports': supports, 'quote': quote})
    return clean


def _clean_header(title, opening):
    title = (title or '').strip()
    opening = (opening or '').strip()
    if not 1 <= len(title) <= 200:
        raise block_rules.ValidationError('Title is required (max 200 characters).')
    if len(opening) > 600:
        raise block_rules.ValidationError('Opening must be 600 characters or fewer.')
    return title, opening


def _claim_status(citations):
    if not citations:
        return 'absent', 'No preserved citation is attached.'
    if any(c.stance == 'conflicts' for c in citations):
        return 'conflicting', 'At least one preserved source conflicts with this claim.'
    if any(c.strength == 'partial' for c in citations):
        return 'partial', 'At least one citation states only partial support.'
    return 'direct', 'Every attached citation states direct support.'


def _quote_in_snapshots(source, quote):
    from .research import normalise_quote
    needle = normalise_quote(quote)
    if not needle:
        return False
    return any(needle in normalise_quote(s.raw_text) for s in source.snapshots.all())


def _create_claims(revision, items, claims, allowed_source_ids=None):
    """Create claim rows and claim-level citations. Claims must be exact substrings of Markdown blocks."""
    if not isinstance(claims, list) or not claims:
        return 0
    created = 0
    for index, raw in enumerate(claims, start=1):
        if not isinstance(raw, dict):
            raise block_rules.ValidationError(f'Claim {index} is malformed.')
        try:
            block_index = int(raw.get('block_index'))
        except (TypeError, ValueError):
            raise block_rules.ValidationError(f'Claim {index} needs block_index.')
        if not 0 <= block_index < len(items):
            raise block_rules.ValidationError(f'Claim {index} points outside the blocks.')
        item = items[block_index]
        if item['kind'] != 'markdown':
            raise block_rules.ValidationError(f'Claim {index} must sit in a markdown block.')
        text = str(raw.get('text', '')).strip()
        if not 1 <= len(text) <= 1200:
            raise block_rules.ValidationError(f'Claim {index} text is empty or too long.')
        source_text = item['data'].get('text', '')
        start = source_text.find(text)
        if start == -1:
            raise block_rules.ValidationError(
                f'Claim {index} is not an exact substring of its block; claim text must match the article.')
        claim = Claim.objects.create(
            revision=revision, block_id=item['block_id'], position=index, text=text,
            start=start, end=start + len(text),
        )
        citations = []
        for c_index, cit in enumerate(raw.get('citations') or [], start=1):
            if not isinstance(cit, dict):
                raise block_rules.ValidationError(f'Claim {index} citation {c_index} is malformed.')
            try:
                source = Source.objects.get(pk=cit.get('source_id'))
            except (Source.DoesNotExist, ValueError, TypeError):
                raise block_rules.ValidationError(f'Claim {index} citation {c_index} names an unknown source.')
            if allowed_source_ids is not None and source.pk not in allowed_source_ids:
                raise block_rules.ValidationError(
                    f'Claim {index} citation {c_index} cites a source not preserved for this job.')
            supports = str(cit.get('supports', '')).strip()
            if not 5 <= len(supports) <= 400:
                raise block_rules.ValidationError(f'Claim {index} citation {c_index} needs a support note (5-400).')
            quote = str(cit.get('quote', '')).strip()
            if quote and not _quote_in_snapshots(source, quote):
                raise block_rules.ValidationError(
                    f'Claim {index} citation {c_index} quote is absent from the preserved snapshot.')
            stance = cit.get('stance', 'supports')
            strength = cit.get('strength', 'direct')
            if stance not in dict(Citation.STANCE) or strength not in dict(Citation.STRENGTH):
                raise block_rules.ValidationError(f'Claim {index} citation {c_index} has an invalid stance/strength.')
            citations.append(Citation(
                revision=revision, block_id=item['block_id'], claim=claim, source=source,
                supports=supports, quote=quote, stance=stance, strength=strength,
            ))
        Citation.objects.bulk_create(citations)
        status, note = _claim_status(citations)
        claim.support_status = status
        claim.support_note = note
        claim.save(update_fields=['support_status', 'support_note'])
        created += 1
    return created


def _assign_ids(items):
    import uuid
    for item in items:
        if not item['block_id']:
            item['block_id'] = str(uuid.uuid4())
    return items


@transaction.atomic
def create_article(*, title, user, provenance='workshop', opening='', open_draft=True, agent=None, agent_run=None):
    """Create an article with an open draft. Anyone logged in can start a workshop article."""
    require_login(user)
    title, opening = _clean_header(title, opening)
    base_slug = slugify(title)[:100] or 'article'
    slug, suffix = base_slug, 2
    while Article.objects.filter(slug=slug).exists():
        slug = f'{base_slug}-{suffix}'
        suffix += 1
    article = Article.objects.create(slug=slug, title=title, opening=opening, provenance=provenance)
    if not open_draft:
        _audit(article, 'article_created', actor=user, agent=agent, agent_run=agent_run,
               detail={'provenance': provenance, 'open_draft': False})
        return article
    draft = Revision.objects.create(
        article=article, number=1, state='draft', title=title, opening=opening,
        created_by=user, updated_by=user,
    )
    _write_content(draft, _assign_ids([dict(DEFAULT_BLOCK)]), [])
    _audit(article, 'article_created', actor=user, agent=agent, agent_run=agent_run, revision=draft,
           detail={'provenance': provenance})
    return article


@transaction.atomic
def ensure_draft(article, user):
    """Return the open draft, creating one from the published revision if needed."""
    require_login(user)
    article.refresh_from_db()
    existing = article.revisions.filter(state='draft').first()
    if existing:
        return existing
    try:
        with transaction.atomic():
            base = article.published
            if base is None:
                draft = Revision.objects.create(
                    article=article, number=next_number(article), state='draft',
                    title=article.title, opening=article.opening, created_by=user, updated_by=user,
                )
                _write_content(draft, _assign_ids([dict(DEFAULT_BLOCK)]), [])
                return draft
            draft = Revision.objects.create(
                article=article, number=next_number(article), state='draft',
                title=base.title, opening=base.opening, created_by=user, updated_by=user,
                reverts=None,
            )
            _copy_content(base, draft)
            return draft
    except IntegrityError:
        return article.revisions.get(state='draft')


def _copy_content(source, target):
    items = [
        {'block_id': b.block_id, 'kind': b.kind, 'data': b.data}
        for b in source.blocks.order_by('position')
    ]
    citations = [
        {'block_id': c.block_id, 'source_id': c.source_id, 'supports': c.supports, 'quote': c.quote}
        for c in source.citations.all()
    ]
    _write_content(target, items, citations)


@transaction.atomic
def save_draft(draft, user, *, title, opening, items, citations, expected_version):
    """Save the open draft. items/citations come from the editor payload and are validated here."""
    require_login(user)
    draft = Revision.objects.select_for_update().get(pk=draft.pk)
    if draft.state != 'draft':
        raise EditorialError('This revision is no longer an editable draft.')
    if int(expected_version) != draft.version:
        raise ConflictError(
            'Someone saved this draft after you opened it. Reload the editor to see the latest '
            'version, then reapply your changes.'
        )
    title, opening = _clean_header(title, opening)
    clean_items = _assign_ids(block_rules.validate_blocks(items))
    clean_citations = _validate_citations(citations, clean_items)
    draft.title = title
    draft.opening = opening
    draft.version += 1
    draft.updated_by = _actor(user)
    draft.save()
    _write_content(draft, clean_items, clean_citations)
    return draft


def open_proposal(revision, *, rationale, origin, user=None, eval_case=None, agent=None, agent_run=None,
                  origin_job=None, origin_model=''):
    """Turn a candidate revision into a proposal against the currently published revision."""
    article = revision.article
    article.refresh_from_db()
    rationale = (rationale or '').strip()
    if not 20 <= len(rationale) <= 2000:
        raise block_rules.ValidationError('Rationale must be 20 to 2000 characters, explaining why the change helps readers.')
    base = article.published
    if revision.state not in ('draft', 'proposed'):
        raise EditorialError('Only a draft or candidate can become a proposal.')
    if base is not None and content_hash(revision) == content_hash(base):
        raise block_rules.ValidationError(f'This draft has no changes from {base.label}. Edit something before proposing.')
    with transaction.atomic():
        revision.state = 'proposed'
        revision.content_hash = content_hash(revision)
        revision.published_at = None
        revision.save()
        repeat = Proposal.objects.filter(
            article=article, base=base, candidate__content_hash=revision.content_hash, status='rejected'
        ).order_by('-created_at').first()
        proposal = Proposal.objects.create(
            article=article, base=base, candidate=revision, origin=origin, rationale=rationale,
            created_by=_actor(user), repeat_of=repeat, eval_case=eval_case, agent=agent,
            origin_job=origin_job, origin_model=(origin_model or getattr(agent_run, 'model', '') or ''),
        )
        _audit(
            article, 'proposal_opened', actor=user, agent=agent, agent_run=agent_run, revision=revision,
            proposal=proposal, job=origin_job,
            reason=rationale[:200], detail={'origin': origin, 'base': base.label if base else None,
                                            'repeat_of': str(repeat.id) if repeat else None},
        )
    return proposal


def create_candidate(article, *, title, opening, items, citations, origin, user=None, allowed_source_ids=None,
                     claims=None):
    """Build a candidate revision (state=proposed) from full article content. Used by runners and eval cases."""
    title, opening = _clean_header(title, opening)
    clean_items = _assign_ids(block_rules.validate_blocks(items))
    if claims and citations:
        raise block_rules.ValidationError('Provide either claim-level citations or block-level citations, not both.')
    clean_citations = _validate_citations(citations, clean_items, allowed_source_ids)
    with transaction.atomic():
        candidate = Revision.objects.create(
            article=article, number=next_number(article), state='proposed',
            title=title, opening=opening, created_by=_actor(user), updated_by=_actor(user),
        )
        _write_content(candidate, clean_items, [] if claims else clean_citations)
        if claims:
            _create_claims(candidate, clean_items, claims, allowed_source_ids)
    return candidate


@transaction.atomic
def submit_draft(draft, user, rationale):
    require_login(user)
    draft = Revision.objects.select_for_update().get(pk=draft.pk)
    if draft.state != 'draft':
        raise EditorialError('Only the open draft can be submitted.')
    return open_proposal(draft, rationale=rationale, origin='human', user=user)


@transaction.atomic
def record_review(proposal, *, role, verdict, comment, evidence_notes='', origin='simulated', declared_model='',
                  job=None, agent=None, agent_run=None, operator=None, claim_verdicts=None):
    proposal = Proposal.objects.select_for_update().get(pk=proposal.pk)
    if proposal.status != 'pending':
        raise EditorialError('Reviews can only be added while a proposal awaits a decision.')
    if verdict not in dict(Review.VERDICTS):
        raise block_rules.ValidationError('Unknown verdict.')
    try:
        with transaction.atomic():
            review = Review.objects.create(
                proposal=proposal, role=role, verdict=verdict, comment=comment[:1200],
                evidence_notes=evidence_notes[:1200], origin=origin, declared_model=declared_model[:120], job=job,
                agent=agent, agent_run=agent_run, claim_verdicts=claim_verdicts or {},
            )
    except IntegrityError:
        raise ConflictError(f'The {role} reviewer already reviewed this proposal.')
    _audit(
        proposal.article, 'review_recorded', revision=proposal.candidate, proposal=proposal, job=job,
        actor=operator, agent=agent, agent_run=agent_run, model=declared_model,
        detail={'role': role, 'verdict': verdict, 'origin': origin},
    )
    return review


def panel_outcome(reviews, policy):
    """Deterministic summary of a set of reviews. Not a publication decision."""
    verdicts = [r.verdict for r in reviews]
    if not verdicts:
        return 'incomplete'
    if 'object' in verdicts:
        return 'objected'
    supports = verdicts.count('support')
    if 'concern' in verdicts:
        return 'contested'
    if supports >= policy.get('min_supports', 2):
        return 'supported'
    return 'incomplete'


def _policy():
    from .configs import active_policy
    return active_policy()


@transaction.atomic
def decide(proposal, user, decision, note=''):
    """Approve, reject or request revision. Approval checks the active publication policy."""
    require_staff(user)
    proposal = Proposal.objects.select_for_update().get(pk=proposal.pk)
    note = (note or '').strip()
    if proposal.origin == 'evaluation':
        raise EditorialError('Evaluation proposals are never approved or published.')
    if decision not in ('approve', 'reject', 'request_revision'):
        raise block_rules.ValidationError('Unknown decision.')
    if proposal.status not in ('pending', 'approved'):
        raise EditorialError(f'This proposal is already {proposal.get_status_display().lower()}.')
    if decision in ('reject', 'request_revision') and not note:
        raise block_rules.ValidationError('Give a short reason so the author knows what to change.')
    policy = _policy()
    reviews = list(proposal.reviews.all())
    if decision == 'approve':
        if len(reviews) < policy['min_reviews']:
            raise EditorialError(
                f'Policy needs at least {policy["min_reviews"]} reviews before approval; this proposal has {len(reviews)}.'
            )
        if policy['block_on_objection'] and any(r.verdict == 'object' for r in reviews):
            raise EditorialError('Policy blocks approval while a reviewer objects. Reject or request a revision instead.')
        proposal.status = 'approved'
        action = 'proposal_approved'
    elif decision == 'reject':
        proposal.status = 'rejected'
        action = 'proposal_rejected'
        proposal.candidate.state = 'rejected'
        proposal.candidate.save(update_fields=['state'])
    else:
        proposal.status = 'revision_requested'
        action = 'revision_requested'
        proposal.candidate.state = 'rejected'
        proposal.candidate.save(update_fields=['state'])
    proposal.decided_by = _actor(user)
    proposal.decided_at = timezone.now()
    proposal.decision_note = note
    proposal.save()
    _audit(proposal.article, action, actor=user, reason=note, revision=proposal.candidate, proposal=proposal,
           detail={'policy': policy, 'reviews': len(reviews)})
    return proposal


def publish(proposal, user):
    """Publish an approved proposal. Refuses when the article moved on since the proposal was made."""
    require_staff(user)
    stale = None
    with transaction.atomic():
        article = Article.objects.select_for_update().get(pk=proposal.article_id)
        proposal = Proposal.objects.select_for_update().get(pk=proposal.pk)
        if proposal.origin == 'evaluation':
            raise EditorialError('Evaluation proposals are never published.')
        if proposal.status != 'approved':
            raise EditorialError('Only approved proposals can be published.')
        if proposal.base_id != article.published_id:
            current = article.published
            _audit(
                article, 'publish_refused_stale', actor=user, proposal=proposal, revision=proposal.candidate,
                reason='Base revision is no longer current.',
                detail={'base': proposal.base.label if proposal.base else None,
                        'current': current.label if current else None},
            )
            stale = (proposal.base.label if proposal.base else 'none', current.label if current else 'none')
        else:
            previous = article.published
            candidate = proposal.candidate
            if previous is not None:
                previous.state = 'superseded'
                previous.save(update_fields=['state'])
            candidate.state = 'published'
            candidate.published_at = timezone.now()
            candidate.updated_by = _actor(user)
            candidate.save()
            article.published = candidate
            article.title = candidate.title
            article.opening = candidate.opening
            article.save()
            proposal.status = 'published'
            proposal.result = candidate
            proposal.save()
            _audit(
                article, 'published', actor=user, revision=candidate, proposal=proposal,
                reason=proposal.decision_note or 'Approved proposal published.',
                detail={'from': previous.label if previous else None, 'to': candidate.label},
            )
    if stale:
        raise StaleProposalError(
            f'Refused: this proposal was written against {stale[0]}, but the article is now at {stale[1]}. '
            'Open a new proposal from the current revision.'
        )
    return proposal.result


def revert(article, target, user, *, reason, expected_current_id):
    """Restore an earlier revision's content as a NEW published revision. History is kept."""
    require_staff(user)
    reason = (reason or '').strip()
    if not 5 <= len(reason) <= 500:
        raise block_rules.ValidationError('Give a reason for the revert (5 to 500 characters).')
    stale = None
    with transaction.atomic():
        article = Article.objects.select_for_update().get(pk=article.pk)
        current = article.published
        if target.article_id != article.pk:
            raise EditorialError('That revision belongs to another article.')
        if target.state not in ('published', 'superseded'):
            raise EditorialError('Only earlier published revisions can be restored.')
        if current is None or current.pk == target.pk:
            raise EditorialError('That revision is already the current one.')
        if str(expected_current_id) != str(current.pk):
            _audit(
                article, 'revert_refused_stale', actor=user, reason=reason, revision=target,
                detail={'expected': str(expected_current_id), 'current': current.label},
            )
            stale = current.label
        else:
            new = Revision.objects.create(
                article=article, number=next_number(article), state='published',
                title=target.title, opening=target.opening, reverts=target,
                summary=f'Revert to {target.label}', created_by=_actor(user), updated_by=_actor(user),
                published_at=timezone.now(),
            )
            _copy_content(target, new)
            current.state = 'superseded'
            current.save(update_fields=['state'])
            article.published = new
            article.title = new.title
            article.opening = new.opening
            article.save()
            _audit(
                article, 'reverted', actor=user, reason=reason, revision=new,
                detail={'restored_from': target.label, 'previous': current.label, 'result': new.label},
            )
    if stale:
        raise StaleProposalError(f'Refused: the article is now at {stale}. Reload the history page and retry.')
    return new


def create_published_revision(article, user, *, items, citations, summary, title=None, opening=None, claims=None):
    """Create and publish a revision directly. Only for seeding demonstration content, and only by staff."""
    require_staff(user)
    with transaction.atomic():
        article = Article.objects.select_for_update().get(pk=article.pk)
        title, opening = _clean_header(title or article.title, opening if opening is not None else article.opening)
        clean_items = _assign_ids(block_rules.validate_blocks(items))
        clean_citations = _validate_citations(citations, clean_items)
        previous = article.published
        revision = Revision.objects.create(
            article=article, number=next_number(article), state='published', title=title, opening=opening,
            summary=summary[:300], created_by=_actor(user), updated_by=_actor(user), published_at=timezone.now(),
        )
        _write_content(revision, clean_items, [] if claims else clean_citations)
        if claims:
            _create_claims(revision, clean_items, claims)
        if previous is not None:
            previous.state = 'superseded'
            previous.save(update_fields=['state'])
        article.published = revision
        article.title = title
        article.opening = opening
        article.save()
        _audit(article, 'published', actor=user, revision=revision,
               reason=summary[:300], detail={'from': previous.label if previous else None, 'to': revision.label})
    return revision


def create_source(*, title, url='', kind='other', authors='', publisher='', published_on='', check_status='unchecked', retrieval_note='', user=None):
    require_login(user)
    title = (title or '').strip()
    if not title:
        raise block_rules.ValidationError('Source title is required.')
    if url and not url.startswith(('https://', 'http://')):
        raise block_rules.ValidationError('Source URL must start with http:// or https://.')
    return Source.objects.create(
        title=title[:300], url=url, kind=kind, authors=authors[:300], publisher=publisher[:200],
        published_on=published_on[:60], check_status=check_status, retrieval_note=retrieval_note[:2000],
    )


def revision_items(revision):
    return [
        {'block_id': str(b.block_id), 'kind': b.kind, 'data': dict(b.data)}
        for b in revision.blocks.order_by('position')
    ]


def eval_case_base(case):
    base = case.article.published
    if base is None:
        raise EditorialError(f'Article {case.article.slug} has no published revision to test against.')
    return base
