# Authorization and editorial state machine

**Status:** design note plus an implemented first slice, 2026-11-05. It is not a constitution and not a
community-ratified policy. The code enforces the tables below; changing a table is a policy change and must be
recorded.

**Purpose:** replace scattered `is_staff` checks with one deterministic place that answers three questions:

1. What state is this editorial object in?
2. Which transitions are legal from that state?
3. May this actor perform that transition now, given capability, relationship, quotas and object state?

The goal is not a large policy engine. It is a small, readable, testable transition table with explicit reason
codes. If a rule is not in this document and not in `core/authorization.py`, it is not a rule.

---

## 1. Actors and trust levels

| Actor | What it is | How it authenticates | Can it publish? |
|---|---|---|---|
| Anonymous | Reader only | None | No |
| Account — `new` | A newly created human account, or one deliberately set to limited | Session | No |
| Account — `standard` | Default human account | Session | No |
| Account — `trusted` | Human reviewer with a track record, set by a steward | Session | No |
| Account — `steward` | Staff/publisher; currently Django `is_staff` | Session | Yes, through the policy gate |
| Agent | A non-human actor with an operator and scopes | Hashed token | Never (no publish scope) |
| Service | Internal application code (job runner, migration) | No user session | Only through a service function that rechecks guards |

**Trust is capability, not identity verification.** A trust level says how much review/submission capacity the
account gets. It does not assert the person's real name, expertise or good faith. Stewards can change a level; the
change is audited. A verified identity is a separate, later feature and must not be smuggled into this table.

**Defaults:**

- staff/superuser → `steward`;
- other accounts → `standard`;
- no account is silently `trusted`; a steward must promote it;
- `new` is for explicit limitation (new account, probation, or a steward's decision).

---

## 2. Capabilities

Capabilities are coarse. Object state and relationship guards do the rest.

| Capability | Meaning |
|---|---|
| `read` | Read published content and public credit pages |
| `propose` | Create drafts/articles and submit a proposal |
| `review` | Record a human review on a proposal |
| `view_review_queue` | Open the human review dashboard |
| `decide` | Approve, reject, or request changes on a proposal |
| `publish` | Publish an approved proposal |
| `revert` | Restore an earlier published revision as a new revision |
| `configure` | Change versioned runner/reviewer/policy configuration |
| `administer` | Django admin / destructive operations |

**Trust matrix:**

| Trust | read | propose | review | queue | decide | publish | revert | configure |
|---|---|---|---|---|---|---|---|---|
| `new` | yes | 1/day | no | no | no | no | no | no |
| `standard` | yes | 5/day | 10/day | yes | no | no | no | no |
| `trusted` | yes | 10/day | 25/day | yes | no | no | no | no |
| `steward` | yes | unlimited | unlimited | yes | yes | yes | yes | yes |

Agents use their token scopes (`read`, `research`, `propose`, `review`) and never gain `decide`, `publish`,
`revert`, `configure` or `administer`. Agent review usage is bounded by the job's model-call and time limits, not by
the human daily quota.

**Quotas** are rolling 24-hour counts and are evaluated at the service boundary:

- proposals: `Proposal.created_by = actor` in the last 24 hours;
- human reviews: `Review.reviewer = actor` and `Review.origin = 'human'` in the last 24 hours.

A denied quota is a normal, explainable answer: `quota_exceeded` with the limit and reset window. It is not an
authentication failure.

---

## 3. Object states

The proposal is the unit of editorial decision. A single stored `Proposal.status` is not enough to describe where
work is, so the state is **derived** deterministically:

| Derived state | Condition | Reader/editor meaning |
|---|---|---|
| `submitted` | `status='pending'` and no reviews | Waiting for the first reviewer |
| `under_review` | `status='pending'` and at least one review | Review in progress |
| `approved` | `status='approved'` | Policy satisfied; publishing is a separate step |
| `published` | `status='published'` | Current or historical publication record |
| `rejected` | `status='rejected'` | Closed; candidate kept |
| `changes_requested` | `status='revision_requested'` | Closed; author may open a new draft |
| `withdrawn` | reserved for a future explicit status | Not implemented |

The stored statuses remain unchanged in this slice (no migration of existing rows, no seed breakage). The derived
state is computed by `authorization.proposal_state()` and shown in the dashboard and proposal page.

Draft and revision states remain the existing `draft` / `proposed` / `published` / `superseded` / `rejected`
values. A proposal cannot be edited after submission; a new draft is the edit path.

---

## 4. Transition table

Every transition is checked in this order: object exists → state allows the action → actor capability → relationship
guard → quota → policy guard. The first failing check returns a reason code. The service then either raises a
permission error (403), a state/validation error (409/400), or a quota error with a user-safe explanation.

| # | Action | From | To | Capability | Relationship / state guards | Side effects |
|---|---|---|---|---|---|---|
| T1 | `submit` | open `draft` | `submitted` | `propose` | actor is draft author or steward; draft has a real change; base is current; quota | revision `proposed`, proposal created, audit |
| T2 | `review` | `submitted` or `under_review` | `under_review` | `review` | proposal pending; role not already used; actor is not the author (human proposals); quota for human reviews | review row, audit (same-agent reviews flagged non-independent) |
| T3 | `approve` | `submitted` or `under_review` | `approved` | `decide` | policy minimum reviews met; no blocking objection; actor is not the author of a human proposal | status, decision note, audit |
| T4 | `reject` | `submitted` or `under_review` | `rejected` | `decide` | reason required; actor is not the author of a human proposal | candidate rejected, audit |
| T5 | `request_changes` | `submitted` or `under_review` | `changes_requested` | `decide` | reason required; actor is not the author of a human proposal | candidate rejected, audit |
| T6 | `publish` | `approved` | `published` | `publish` | base still current; not evaluation; actor is not the author of a human proposal | revision published, pointer updated, `PublicationEvent`, audit |
| T7 | `revert` | current published revision | new published revision | `revert` | target is a published/superseded revision of the same article; expected current matches; reason 5–500 chars | new revision, pointer updated, `PublicationEvent`, audit |
| T8 | `withdraw` | `submitted` or `under_review` | `withdrawn` | `propose` | author or steward | **Not implemented**; reserved |

**Self-review** is blocked for human-origin proposals: a person cannot review their own proposal. For agent-origin
proposals, a same-agent review is allowed in v1 but is recorded in the audit detail as `same_agent: true` and is
**not independent evidence**; the agent cycle does not yet use a distinct reviewer identity. The operator may be
the same person, because the agent is a distinct actor. Do not count same-agent reviews as independent when
measuring reviewer value (E2/E3).

**Self-decision and self-publication** are blocked for human-origin proposals. A steward who wrote a human
proposal cannot approve or publish it; another steward must. For simulated/agent proposals, the operator may
decide because the proposal's author is the agent/simulator, not the operator. This distinction is deliberate and
audited.

**Evaluation proposals** are never approved or published, regardless of actor.

**Stale bases** are refused at publication, not at review. A reviewed proposal may become stale while it waits;
the publish transition rechecks the pointer.

---

## 5. Reason codes

| Code | Meaning | Surface |
|---|---|---|
| `anonymous` | Login required | Redirect to login |
| `missing_capability` | Actor's trust level/scopes lack the action | 403 with reason |
| `wrong_state` | Action is not legal from the current state | 409 with explanation |
| `not_author` | Only the draft/proposal author (or steward) may act | 403 |
| `self_review` | A human cannot review their own proposal | 403 |
| `self_decision` | A human cannot decide/publish their own proposal | 403 |
| `already_reviewed` | That role already reviewed this proposal | 409 |
| `quota_exceeded` | Daily proposal/review limit reached | 429-style explanation |
| `stale` | Base revision is no longer current | 409, no side effects |
| `evaluation` | Evaluation candidates are never published | 409 |
| `unknown_role` | Review role not in the configured role list | 400 |

The service layer returns the same decision whether the action comes from a browser, an HTML form, or the token
API. The dashboard is a view over these decisions, not a second permission system.

---

## 6. Human review dashboard

Route: `/review/` (name `review_dashboard`). Access: any actor with `view_review_queue`
(`standard`, `trusted` or `steward`); anonymous redirects to login; `new` gets 403. `standard` can see the
queue and review, but cannot decide or publish.

The first screen answers: **what needs a human now?**

Required blocks:

1. **Queue summary:** submitted (no reviews), under review, approved awaiting publish, changes requested,
   stale approvals, rejected in the last 7 days.
2. **Queue table:** article, proposal, derived state, origin, author/agent, age, review coverage by role,
   policy threshold, stale flag, last decision. Sort oldest first; filters for state, origin, article and text.
3. **Review coverage:** per proposal, which configured roles have a verdict and which are missing. A proposal with
   an objection is visibly blocked from approval.
4. **Actions:** open proposal (diff + evidence + review form), approve/reject/request changes, publish when
   allowed. Actions are rendered only if `authorization.can(...)` says yes; server checks again.
5. **My recent reviews:** the reviewer's human reviews in the last 7 days, with verdicts, so workload is visible.
6. **No auto-assignment:** the queue is shared. Assignment/claiming is a later feature; do not pretend a proposal
   is owned when it is not.

The proposal page adds a human review form (role, verdict, comment, evidence notes) for actors with `review`
capability, excluding roles already used and excluding self-review. The form records `Review.reviewer`.

---

## 7. Determinism and tests

`core/authorization.py` is the single evaluator. It exports:

- `proposal_state(proposal) -> str`
- `profile_for(user) -> ContributorProfile`
- `can(actor, action, obj=None, *, proposal=None, role=None, agent=None) -> Decision`
- a service-layer `_authorize` wrapper that maps a denied `Decision` to a 403 or an editorial error
- `available_actions(actor, proposal) -> list[Decision]`
- `remaining_quota(actor, action) -> int | None`

Tests must cover, at minimum: each capability boundary; anonymous denial; self-review; self-decision;
self-publication; evaluation refusal; stale publication; role duplication; quota exhaustion; state transitions;
dashboard access; and the human review form. A test that only checks the template text is not enough; assert the
service result and the audit row.

---

## 8. Non-goals for this slice

- No external policy engine or new orchestration framework.
- No real-name/identity verification, no reputation score, no per-topic expertise claims.
- No automatic assignment, no auto-publication, no agent publish scope.
- No correction/dispute/appeal state machine yet; those are later objects.
- No change to the existing publication policy minimums beyond routing through the new evaluator.

## 9. Open questions (not decisions)

1. How does an account move from `new` to `standard`/`trusted`? The first slice uses steward action + audit;
   whether an automatic promotion rule should exist is open.
2. Should `new` accounts see the queue after their first accepted review? The first slice blocks `new`; a
   promotion path is not yet automated.
3. Are the quota numbers right? They are starting parameters, not measured. E2/E3 and the review-hour ratio should
   calibrate them.
4. Should a steward be able to decide a human proposal they edited but did not author? The first slice uses
   `created_by`, not edit history, as the authorship test; that is conservative but incomplete.
5. When a proposal is withdrawn, should the candidate remain public? Not implemented.
