"""One deterministic place for editorial capabilities, transitions and quotas.

This module answers *whether* an action is allowed. Services still perform the mutation and write the audit
event. The tables here are policy; changing them is a policy change. See docs/AUTHORIZATION-STATE-MACHINE.md.
"""
from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone

from .models import ContributorProfile, Proposal, Review


# ----- Capabilities and trust ---------------------------------------------------------------

CAP_READ = 'read'
CAP_PROPOSE = 'propose'
CAP_REVIEW = 'review'
CAP_VIEW_QUEUE = 'view_review_queue'
CAP_DECIDE = 'decide'
CAP_PUBLISH = 'publish'
CAP_REVERT = 'revert'
CAP_CONFIGURE = 'configure'
CAP_ADMINISTER = 'administer'

TRUST_CAPABILITIES = {
    'new': {CAP_READ, CAP_PROPOSE},
    'standard': {CAP_READ, CAP_PROPOSE, CAP_REVIEW, CAP_VIEW_QUEUE},
    'trusted': {CAP_READ, CAP_PROPOSE, CAP_REVIEW, CAP_VIEW_QUEUE},
    'steward': {
        CAP_READ, CAP_PROPOSE, CAP_REVIEW, CAP_VIEW_QUEUE, CAP_DECIDE, CAP_PUBLISH, CAP_REVERT,
        CAP_CONFIGURE, CAP_ADMINISTER,
    },
}

DAILY_LIMITS = {
    'new': {CAP_PROPOSE: 1, CAP_REVIEW: 0},
    'standard': {CAP_PROPOSE: 5, CAP_REVIEW: 10},
    'trusted': {CAP_PROPOSE: 10, CAP_REVIEW: 25},
    'steward': {CAP_PROPOSE: None, CAP_REVIEW: None},
}

AGENT_SCOPES = {
    'read': CAP_READ,
    'research': 'research',
    'propose': CAP_PROPOSE,
    'review': CAP_REVIEW,
}


@dataclass(frozen=True)
class Decision:
    allowed: bool
    code: str
    message: str = ''
    remaining: int | None = None


def allow(code='allowed', remaining=None):
    return Decision(True, code, '', remaining)


def deny(code, message, remaining=None):
    return Decision(False, code, message, remaining)


def profile_for(user):
    """Return the human capability profile, creating a conservative default once.

    Staff default to steward; everyone else defaults to standard. A steward can lower or raise the level in
    Django admin; the change is visible and auditable because it changes future decisions.
    """
    if not user or not user.is_authenticated:
        return None
    cached = getattr(user, '_authorization_profile', None)
    if cached is not None:
        return cached
    default = 'steward' if user.is_staff else 'standard'
    profile, _ = ContributorProfile.objects.get_or_create(
        user=user, defaults={'trust_level': default},
    )
    user._authorization_profile = profile
    return profile


def capabilities_for(actor):
    if actor is None:
        return {CAP_READ}
    if isinstance(actor, ContributorProfile):
        return set(TRUST_CAPABILITIES.get(actor.trust_level, set()))
    if getattr(actor, 'is_authenticated', False):
        profile = profile_for(actor)
        return set(TRUST_CAPABILITIES.get(profile.trust_level, set())) if profile else {CAP_READ}
    return {CAP_READ}


def _agent_capabilities(agent):
    if not agent or not agent.is_active:
        return set()
    caps = {AGENT_SCOPES[scope] for scope in (agent.scopes or []) if scope in AGENT_SCOPES}
    caps.add(CAP_READ)
    return caps


# ----- Quotas ---------------------------------------------------------------------------------

def _quota_used(user, action):
    since = timezone.now() - timedelta(hours=24)
    if action == CAP_PROPOSE:
        return Proposal.objects.filter(
            created_by=user, created_at__gte=since,
        ).exclude(origin='evaluation').count()
    if action == CAP_REVIEW:
        return Review.objects.filter(
            reviewer=user, origin='human', created_at__gte=since,
        ).count()
    return 0


def remaining_quota(actor, action):
    if isinstance(actor, ContributorProfile):
        limit = DAILY_LIMITS.get(actor.trust_level, {}).get(action)
        user = actor.user
    elif getattr(actor, 'is_authenticated', False):
        profile = profile_for(actor)
        limit = DAILY_LIMITS.get(profile.trust_level, {}).get(action) if profile else 0
        user = actor
    else:
        return 0
    if limit is None:
        return None
    return max(limit - _quota_used(user, action), 0)


def _quota_decision(actor, action):
    remaining = remaining_quota(actor, action)
    if remaining is None or remaining > 0:
        return allow(remaining=remaining)
    return deny(
        'quota_exceeded',
        f'Daily {action} limit reached. The limit is based on the account trust level; try again after '
        f'24 hours or ask a steward to review the tier.',
        remaining=0,
    )


# ----- States ---------------------------------------------------------------------------------

def proposal_state(proposal):
    """Derive the workflow state without adding a second stored status column."""
    if proposal is None:
        return 'missing'
    status = proposal.status
    if status == 'pending':
        return 'under_review' if proposal.reviews.exists() else 'submitted'
    return {
        'approved': 'approved',
        'published': 'published',
        'rejected': 'rejected',
        'revision_requested': 'changes_requested',
    }.get(status, status)


STATE_LABELS = {
    'submitted': 'Submitted',
    'under_review': 'Under review',
    'approved': 'Approved, not published',
    'published': 'Published',
    'rejected': 'Rejected',
    'changes_requested': 'Changes requested',
    'withdrawn': 'Withdrawn',
}


def state_label(proposal):
    return STATE_LABELS.get(proposal_state(proposal), proposal_state(proposal))


def _valid_roles():
    from .configs import REVIEW_ROLES
    return {key for key, _label, _instructions in REVIEW_ROLES}


# ----- Decisions ------------------------------------------------------------------------------

def _agent_decision(agent, action, proposal=None, role=None):
    caps = _agent_capabilities(agent)
    if not caps:
        return deny('missing_capability', 'This agent is inactive or has no usable scopes.')
    needed = {
        'propose': CAP_PROPOSE,
        'review': CAP_REVIEW,
        'read': CAP_READ,
    }.get(action)
    if needed is None:
        return deny('missing_capability', 'Agents cannot decide, publish, revert or configure.')
    if needed not in caps:
        return deny('missing_capability', f'This agent does not have the "{action}" scope.')
    if action == 'review':
        if proposal is None:
            return deny('wrong_state', 'No proposal supplied.')
        if proposal.status != 'pending':
            return deny('wrong_state', 'This proposal is no longer open for review.')
        if role not in _valid_roles():
            return deny('unknown_role', 'Unknown review role.')
        if proposal.reviews.filter(role=role).exists():
            return deny('already_reviewed', f'The {role} role already reviewed this proposal.')
        # A same-agent review is allowed in v1 but is marked non-independent in the audit detail. Blocking it
        # would require the agent cycle to use a distinct reviewer identity, which is a later change.
    return allow()


def can(actor, action, obj=None, *, proposal=None, role=None, agent=None):
    """Evaluate one action. Returns a Decision; never mutates content.

    Actor may be a Django user, a ContributorProfile, or None. Pass `agent` for a token-authenticated
    non-human actor. Internal job/simulated calls deliberately pass no human actor and are not governed by
    the human quota; their job limits and audit rows still apply.
    """
    if proposal is None and isinstance(obj, Proposal):
        proposal = obj

    if agent is not None:
        return _agent_decision(agent, action, proposal=proposal, role=role)

    if not actor or not getattr(actor, 'is_authenticated', False):
        return deny('anonymous', 'Log in to do this.')

    profile = profile_for(actor)
    if profile is None:
        return deny('anonymous', 'Log in to do this.')
    caps = set(TRUST_CAPABILITIES.get(profile.trust_level, set()))

    if action == CAP_VIEW_QUEUE:
        return allow() if CAP_VIEW_QUEUE in caps else deny(
            'missing_capability', 'The review queue is limited to trusted reviewers and stewards.')

    if action in (CAP_CONFIGURE, CAP_ADMINISTER):
        return allow() if action in caps else deny(
            'missing_capability', 'Steward capability required.')

    if action == 'edit_draft':
        if CAP_PROPOSE not in caps:
            return deny('missing_capability', 'Contributor capability required.')
        if obj is None:
            return deny('wrong_state', 'No draft supplied.')
        if obj.state != 'draft':
            return deny('wrong_state', 'Only an open draft can be edited.')
        if obj.created_by_id and obj.created_by_id != actor.pk and CAP_ADMINISTER not in caps:
            return deny('not_author', 'Only the draft author or a steward can edit this draft.')
        return allow()

    if action == CAP_PROPOSE:
        if CAP_PROPOSE not in caps:
            return deny('missing_capability', 'Contributor capability required.')
        return _quota_decision(actor, CAP_PROPOSE)

    if action == 'review':
        if CAP_REVIEW not in caps:
            return deny('missing_capability', 'Reviewer capability required.')
        if proposal is None:
            return deny('wrong_state', 'No proposal supplied.')
        if proposal.status != 'pending':
            return deny('wrong_state', 'This proposal is no longer open for review.')
        if role not in _valid_roles():
            return deny('unknown_role', 'Unknown review role.')
        if proposal.reviews.filter(role=role).exists():
            return deny('already_reviewed', f'The {role} role already reviewed this proposal.')
        if proposal.created_by_id == actor.pk and proposal.origin == 'human':
            return deny('self_review', 'You cannot review your own proposal.')
        return _quota_decision(actor, CAP_REVIEW)

    if action in ('approve', 'reject', 'request_changes', CAP_DECIDE):
        if CAP_DECIDE not in caps:
            return deny('missing_capability', 'Steward decision capability required.')
        if proposal is None:
            return deny('wrong_state', 'No proposal supplied.')
        if proposal.origin == 'evaluation':
            return deny('evaluation', 'Evaluation proposals are never approved or published.')
        if proposal.status != 'pending':
            return deny('wrong_state', 'This proposal is already closed.')
        if proposal.created_by_id == actor.pk and proposal.origin == 'human':
            return deny('self_decision', 'Another steward must decide a proposal you wrote.')
        return allow()

    if action == CAP_PUBLISH:
        if CAP_PUBLISH not in caps:
            return deny('missing_capability', 'Steward publish capability required.')
        if proposal is None:
            return deny('wrong_state', 'No proposal supplied.')
        if proposal.origin == 'evaluation':
            return deny('evaluation', 'Evaluation proposals are never published.')
        if proposal.status != 'approved':
            return deny('wrong_state', 'Only an approved proposal can be published.')
        if proposal.created_by_id == actor.pk and proposal.origin == 'human':
            return deny('self_decision', 'Another steward must publish a proposal you wrote.')
        return allow()

    if action == CAP_REVERT:
        return allow() if CAP_REVERT in caps else deny(
            'missing_capability', 'Steward revert capability required.')

    if action == CAP_READ:
        return allow()
    return deny('missing_capability', f'Unknown action "{action}".')


def available_actions(actor, proposal):
    """The actions the UI may show. The service rechecks every one before mutation."""
    actions = ('review', 'approve', 'reject', 'request_changes', 'publish')
    return {
        action: can(actor, action, proposal=proposal)
        for action in actions
    }
