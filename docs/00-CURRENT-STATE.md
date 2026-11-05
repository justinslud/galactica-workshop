# Current state and gap assessment

**Status:** working note for the 2026-11-04 product-specification pass; **updated 2026-11-05 after the M0
remainder pass** (permalinks, claim resolver, license fields, FTS5, backup drill, write idempotency — see §1.4).
**Scope:** the Django workshop in this repository, plus the earlier TypeScript prototype and the
decision records it left behind. This note separates what is verified from what is direction,
proposal, inference or unresolved.
**Method:** read `CURRENT.md`, `README.md`, `core/models.py`, `core/editorial.py`, `core/reviewing.py`,
`core/policy_lab.py`, `core/api.py`, `core/configs.py`, the templates, the tests and the local database;
ran the test suite; read the decision material in `~/projects/galactica` (`DECISIONS.md`,
`EXPLORATION.md`, `docs/model.md`, `docs/SPEC-DIGEST.md`, the OpenSpec change). External research is in
`docs/research/`. Nothing was deployed, published or renamed. The local SQLite database **was migrated** by
the M0 and authorization passes (migrations `0006`–`0009`, applied 2026-11-04/05; `0008` makes the event→article FK
`PROTECT` so deleting an article cannot cascade-delete its publication history) and the M0 remainder (migrations
`0010`–`0012`, applied 2026-11-05: license fields, search document/FTS5, idempotency records and a
legacy content-hash backfill); it is gitignored.

## 1. What actually exists and works

### 1.1 The Django workshop (this repository)

Verified by reading the code and by running `.venv/bin/python manage.py test` on 2026-11-05, after the M0 remainder:
**190 tests pass** (133 before M0; 154 after M0; 171 after authorization; 190 after the remainder), Django system
check clean, `makemigrations --check` clean. The local database currently holds 6 articles, 25 revisions, 47 claims,
263 citations, 18 sources, 4 source snapshots, 19 proposals, 72 reviews, 21 jobs, 6 evaluation cases, 105 audit
events, **3 demonstration topics, 6 publication events, 0 watch rows, 2 contributor profiles, 3 search documents
and 0 idempotency records**. `check_search` reports 3 documents / 3 indexed / ok. No browser-level verification was
performed, so the new surfaces are test/check-verified only.

Implemented and exercised:

| Area | What exists | Where |
|---|---|---|
| Content model | `Article` → immutable `Revision` → ordered typed `Block`s (`markdown`, `image`, `table`, `timeline`), stable `block_id` across revisions | `core/models.py` |
| Topics (M0) | Minimal `Topic` (slug, title, scope statement, parent, disambiguation flag, `created_by`) and an `Article.topic` FK; `/topics/` and `/topics/<slug>/` list only published articles; full scope/coverage checklist is not built | `core/models.py`, `core/views.py` (`topics`, `topic`) |
| Publication history (M0) | Append-only `PublicationEvent` per publish/revert with per-article sequence, kind (`initial`/`publish`/`revert`/`import`), `published_at`/`published_by`, previous revision, policy version, decision, reason and content hash; unique `(article, sequence)` and `(article, revision)`; event→article FK is `PROTECT` (an article cannot be deleted out from under its history); `Article.published` is now a cache, not the history | `core/models.py`, `core/editorial.py` (`_record_publication`, `publish`, `revert`, `create_published_revision`), history page "Publication log" |
| Watchlist (M0) | Opt-in `Watch` (one row per user/article) with `last_seen_at`; login-only `/watchlist/`, web-only digest with no email, per-row or all "mark seen" | `core/models.py`, `core/views.py` (`watchlist`, `article_watch`, `watchlist_seen`) |
| Authorization (2026-11-05) | `ContributorProfile` trust levels (`new`/`standard`/`trusted`/`steward`), capability table, derived proposal states, self-review/self-decision guards, agent scopes and rolling 24h proposal/review quotas; one evaluator in `core/authorization.py` used by services and views | `core/authorization.py`, `core/editorial.py`, `core/views.py` |
| Human review queue (2026-11-05) | `/review/` queue for standard/trusted/steward reviewers: derived state, age, review coverage, missing roles, objections, stale flag, filters; proposal page human review form records `Review.reviewer` with `origin='human'` | `core/views.py` (`review_dashboard`, `proposal_review`), `templates/core/review_dashboard.html`, `templates/core/proposal.html` |
| Drafting | One open draft per article; optimistic version check; published revisions are not editable; only the draft author or a steward can edit/submit | `core/editorial.py` (`ensure_draft`, `save_draft`, `submit_draft`) |
| Proposals | Created against the current published revision; rationale required (20–2000 chars); no-op proposals refused; exact repeats of rejected candidates flagged `repeat_of`; capability + quota checked | `open_proposal` |
| Reviews | One review per role per proposal; role-isolated prompts; panel outcome is a summary, not a decision; human reviews are attributed and counted separately from agent/simulated reviews | `record_review`, `panel_outcome`, `core/prompts.py` |
| Decisions | Capability-gated approve/reject/request revision; human authors cannot decide/publish their own proposal; active policy enforces minimum reviews and objection blocking; publish is separate and refuses stale bases | `decide`, `publish`, `core/authorization.py` |
| Revert | Staff-only, reason required, expected-current check, creates a **new** published revision with a `reverts` pointer and appends a `revert` `PublicationEvent` | `revert` |
| Claims | Revision-bound `Claim` with exact substring, character offsets, support status (`direct`/`partial`/`conflicting`/`absent`) | `_create_claims`, `_claim_status` |
| Citations | `Citation` links a block and optionally a claim to a `Source`; stance (`supports`/`conflicts`/`context`), strength (`direct`/`partial`), quote checked against a preserved snapshot | `_quote_in_snapshots` |
| Source intake | HTTPS-only allowlist, DNS/redirect/time/byte checks, preserved `SourceSnapshot` with SHA-256, raw text, excerpt and errors | `core/research.py` |
| Agent identity | `Agent`, `AgentCredential` (salted hash, prefix), scopes (`read`, `research`, `propose`, `review`, reserved `publish_low_risk`), `AgentRun` with measured/unmeasured usage | `core/models.py`, `core/agent_auth.py` |
| Jobs | DB-backed queue with explicit transitions, claim, heartbeat, stale recovery, cancel, explicit retry, model-call budget, timeout | `core/jobs.py` |
| Config | Versioned `instructions`, `reviewers`, `runner`, `policy`, `limits`, `research`; one default per kind; jobs snapshot the resolved config | `core/configs.py` |
| API | Token-auth JSON read/research/propose/review; no publish endpoint; no session auth | `core/api.py` |
| Policy lab | Pure simulation with planted defects, reviewer correlation, ordered policy rules, escape rate and human-load matrix; deterministic per seed | `core/policy_lab.py`, `/lab/` |
| Audit | `AuditEvent` with actor, agent, model, config versions, reason, revision/proposal/job | `core/editorial.py` |
| Safety | `nh3` sanitisation, fixed tag/attribute allowlist, image URL rules, no agent JavaScript | `core/markup.py`, `core/blocks.py` |

The 2026-11-04 policy-lab run (300 trials/cell, seed 7, 12 scenarios, 6 policies, 3 panels) reports:
one-model panel (correlation 0.85) escapes **44.2%** of defective standard-risk edits and **57.2%** of
high-risk edits when publishing on silence; mixed panel (0.30) escapes 22.3% / 44.0%; weak panel 75.8% /
78.8%. Auditing half of standard edits does not rescue it (44.8% escape at 78 human reviews per 100 edits).
These are **simulated assumptions**, not measured catch rates.

### 1.2 The earlier TypeScript prototype (`~/projects/galactica`)

Tasks 1–9 were reported built: SQLite schema, agent registry with hashed rotatable keys and quotas,
topic/page/section/claim/source ledger, proposal review queue, deterministic static export, six-topic
demo seed. Reported (not rerun here): 111 tests, clean typecheck, byte-identical exports. It is a
**historical/parallel implementation**, not the current product surface. Its durable contributions are
the claim-ledger concepts (append-only claims, confidence classes, shared-origin downgrade, negative
findings, dispute pages) and the deterministic export discipline.

### 1.3 Decision material

`~/projects/galactica/DECISIONS.md` records the 2026-10-22 decisions and the 2026-10-25 spoken answers,
plus the 2026-10-27 course clarification. The clarification is the most recent authoritative statement:
Galactica remains a public encyclopedia/shared reference; explanations and diagrams are substantive;
the claim ledger supports rather than replaces article authorship; reading experience and claim
granularity remain open; human review at the start is not a permanent requirement for every edit.

### 1.4 M0 implementation status (complete, 2026-11-05)

M0 is implemented and test-covered in the workshop. The first slice added the append-only `PublicationEvent`
(event→article FK is `PROTECT`), the minimal `Topic` plus `Article.topic` and demo topic seeding (3 demo topics),
the opt-in `Watch`, migrations `0006`–`0008`, the reader surfaces `/topics/`, `/topics/<slug>/`,
`/contributors/<username>/`, `/watchlist/`, the watch toggle/mark-seen endpoints, the article byline/topic/
provenance/watch block and the history publication log.

The remainder (2026-11-05) added:
- `/article/<slug>/r/<n>/` revision permalinks with canonical links and a citation block (revision id, content
  hash, license, access date); public for published/superseded revisions, 404 for anonymous draft access.
- `/claims/<uuid>/` HTML and `/api/v1/claims/<uuid>/` token JSON claim resolver, with `resolution`,
  `valid_to`, citations/snapshots and a current-revision pointer. Claim ids are revision-bound; no merge/alias map.
- `Article.license` / `Article.attribution`, `Source.license` / `Source.attribution`, and a
  `PublicationEvent.license` snapshot so relicensing does not rewrite history. Default article licence is
  CC BY-SA 4.0 (subject to counsel).
- `SearchDocument` plus an external-content FTS5 table/triggers, `/search/` with BM25 ranking and match reasons,
  `rebuild_search` and `check_search`; publishing/reverting refreshes the index.
- `scripts/backup.sh` and `scripts/restore_drill.sh`; a real local drill passed on 2026-11-05 (8 tables,
  integrity ok, checksum/row counts matched). Local-only and unscheduled.
- `IdempotencyRecord` and `Idempotency-Key` on proposal/review/research writes; `If-Match` on agent proposal
  writes; `409`/`412`/`422`/`428`; ETag/`If-None-Match` on reads; `application/problem+json` errors.

**Still not done (M1+):** correction intake, review tiers, full `Topic` scope/coverage; a designed public
(anonymous) full-history page, email digest, and `View`/`Assertion` objects. No claim merge/alias map, no
`claim_key`, no multilingual search, no scheduled/off-host backup, no live restore, and no human E1/E4 sessions.
E1/E4 kits exist under `experiments/`; they are not results.

### 1.5 Authorization and review-queue status (2026-11-05)

**Implemented and test-covered:** `core/authorization.py` (capability table, derived proposal states, one
`can()` evaluator, reason codes, self-review/self-decision/self-publication guards, agent scope checks,
rolling 24h proposal/review quotas); `ContributorProfile` trust levels (`new`/`standard`/`trusted`/`steward`;
staff default steward, others standard); `Review.reviewer`; human review form on the proposal page (records
`origin='human'`); `/review/` queue with counters, filters, coverage, missing roles, objections and stale flags;
migration `0009_contributor_profiles_reviewer`. Services (`open_proposal`, `submit_draft`, `save_draft`,
`ensure_draft`, `record_review`, `decide`, `publish`, `revert`) route through the evaluator.

**Starting parameters, not measurements:** quotas are `new` 1 proposal/0 reviews per day, `standard` 5/10,
`trusted` 10/25, steward unlimited. Same-agent reviews are allowed in v1 but marked `same_agent` in the audit
and are not independent evidence. **Not in this slice:** auto-assignment, automatic trust promotion, an external
policy engine, a `withdrawn` state, appeal/dispute workflows, per-reviewer calibration, and a trust-management UI
beyond Django admin. The suite was **171 tests** at that point (17 new in `core/tests/test_authorization_dashboard.py`); no
browser-level check was run.

## 2. Accepted direction (do not silently re-litigate)

These are supported by dated decisions or the course clarification. They are still revisable, but a
change should be recorded as a change, not presented as a discovery.

1. **Public, multilingual reference for humans and agents.** Agents are expected contributors; people
   and their agents read and explore.
2. **Articles are the readable product.** Explanations, examples, diagrams and editorial selection are
   substantive. The claim/evidence layer supports them.
3. **Agents propose; they do not write published state directly.** Human review at the start; later
   agent review is allowed in principle under foundation policy, with a stated path to decentralization.
4. **Durable accounts, not keys, carry identity.** Keys are rotatable credentials. A key proves
   continuity, not truth or expertise.
5. **Evidence is attached close to claims**, with source records, retrieval snapshots, revision history
   and support/contradict/qualify relationships.
6. **Open, portable base knowledge.** Ordinary reading is free. No advertising. Funding experiments
   may include paid high-volume API access, grants, institutional support and an endowment.
7. **Founder-stewarded early**, with published rules, changes and appeals, and an intention to
   decentralize after the model is understood.
8. **Workshop stack and safety rules:** Django 6.1 / Python 3.14 / SQLite, immutable revisions, staff
   publication, audited decisions, no automatic publication, sanitised rendering.
9. **No automatic publication is implemented.** The low-risk policy is a proposal-only configuration.
10. **The policy lab does not authorize autonomy.** It prices the trade-off; its catch rates are
    assumptions.

## 3. Proposals, inferences, contradictions and unresolved questions

### 3.1 Proposals in the existing material (not accepted)

- Low-risk shadow-mode evaluation with random human audits, and a `publish_low_risk` path only after
  measured false-approval data (`CURRENT.md`, README).
- Multiple-source research with content-hash deduplication.
- Sentence-level or section-block claim attachment (partly implemented since).
- A genuinely contradictory source pair experiment.
- Human audit of the pending AlterEgo proposal and the adversarial candidate.
- A browser smoke check (Playwright) and uploaded media.
- Topic merge, cross-article relations, multilingual content, per-user visibility, separate agent inbox,
  retention policy for snapshots.
- The 2026-10-27 proposed reading-experience exercise: one complete article with expandable evidence and
  a diagram, plus a simulated correction.

### 3.2 Inferences made in this pass (label them as such)

- Article-first is the right **publication unit**; claims should become stable, topic-scoped
  **assertions** with revision-bound occurrences, rather than remaining only revision-bound text.
- Derived views need their own object with a pinned base revision, generator/transform version, review
  status and a stale flag. This is the cleanest way to keep summaries, timelines, maps and translations
  from silently changing the factual basis.
- Reviewer independence, not policy cleverness, is the main lever the lab identifies; that implies
  cross-model/provider panels and recorded independence metadata before any autonomy.
- Human attention should be treated as a **budgeted resource** with risk-based routing, not as an
  unlimited gate.

### 3.3 Contradictions and tensions

1. **Claim ledger vs. article.** `docs/model.md` says "Galactica is a claim ledger with page views on
   top"; the 2026-10-27 clarification says that overstates it. The workshop is article-first. Treat the
   clarification as authoritative; the ledger is supporting infrastructure.
2. **"Everything reviewed" vs. later agent review.** The spoken answer allows later agent review; the
   workshop only implements human staff publication. Both are compatible only if "review" is defined by
   policy version and risk class, not by a permanent human veto on every edit.
3. **Caps.** The TypeScript MVP caps pages at 6 sections / 400-character summaries. The workshop has no
   caps. Neither is accepted as final. The clarification explicitly leaves caps open.
4. **Source policy and language governance** were deferred in the decisions; this spec must propose
   defaults without pretending they were decided.
5. **Name.** Galactica is a working name; T5 / t5.wiki is under consideration. No rename is authorized.
6. **Independence.** Three reviewer roles run in fresh sessions but often on the same model and the same
   evidence packet. That is independence of session, not of evidence or model. The lab models the
   correlation; the app does not measure it.
7. **"Human review" capacity.** The project is founder-stewarded with limited human attention, but the
   current policy requires at least two reviews and a staff decision for every published edit. That does
   not scale to agent-scale contribution and has not been costed.

### 3.4 Unresolved questions carried forward

- What is the minimum viable **topic** object, and does it exist separately from an article? *(M0 adds a minimal
  `Topic` and `Article.topic`; scope/coverage, split/merge and disambiguation behavior are still open.)*
- How are claims tracked across revisions without turning every sentence into a permanent record?
- What exactly is a "view", who reviews it, and how is staleness surfaced?
- Which review roles are factual, which are editorial, and which are community preference?
- How does a reader or a subject file a correction, and what happens next?
- How are appeals heard, by whom, and on what timeline?
- What identity evidence is observed, self-declared or verified?
- How is review capacity measured, and what are the initial quotas?
- What is the launch corpus, and what would make a reader return?
- What licensing and export obligations apply to articles, structured data and source snapshots?
- What is the name?

## 4. What to extend rather than replace

| Component | Verdict | Reason |
|---|---|---|
| `Article` / `Revision` / `Block` | **Extend** | Immutable revisions, stable block IDs and typed blocks are the right spine. Add topic/scope metadata and more block kinds, do not rewrite. |
| `Claim` / `Citation` / `SourceSnapshot` | **Extend** | Claim-level evidence and quote checking already work. Add a stable `claim_key` now; full assertion identity, source assessment and independence metadata are later (M2/M4). |
| `Proposal` / `Review` / `decide` / `publish` / `revert` | **Extend** | The proposal gate, stale-base refusal, append-only revert and audit trail are the core trust machinery. Add review rounds, risk classes, appeals and correction intake. |
| `Job` / `ConfigVersion` | **Extend** | Config snapshots and explicit job states are a strong reproducibility base. Add replay metadata and cost accounting. |
| `Agent` / `AgentCredential` / `AgentRun` | **Extend** | Scoped tokens and measured/unmeasured usage are honest. Add operator/org verification levels and topic-scoped track record. |
| `core/policy_lab.py` | **Extend** | It is the only quantitative policy tool. Feed it measured catch rates and add a shadow-mode report; do not treat it as a decision engine. |
| `core/api.py` | **Extend** | The read/research/propose/review API is a good base. Add idempotency, ETags, cursor pagination, exports and an MCP facade later. |
| Static export (TypeScript prototype) | **Reuse the discipline, not the code** | Deterministic, secret-scanned exports are worth keeping as a property. The workshop's SQLite/Django surface is the current implementation. |
| `docs/model.md` claim-ledger framing | **Supersede the framing, keep the concepts** | Article-first is the current direction; append-only claims, confidence classes and shared-origin checks remain useful. |
| Page caps (6 sections / 400 chars) | **Do not adopt as-is** | They were an MVP forcing function, not a product decision. Replace with a scope/coverage model and measured split rules. |

## 5. Gap assessment by area

| Area | Current state | Gap that matters for an ambitious reference |
|---|---|---|
| Reader experience | Article page (byline, topic, provenance, watch toggle), block rendering, citations drawer, revision permalinks with citation/licence, claim resolver (HTML + token JSON), FTS5 search over published titles/bodies/claims/sources, history page with publication log, topic index/pages, public contributor credit page, login-only watchlist; no related-topic graph, timelines beyond a block type, maps, reading levels or languages | No defined article anatomy, no evidence-inspection UX beyond a drawer, no correction/dispute surface, no view provenance, no designated public full-history page, no multilingual/CJK search, no accessibility/mobile verification |
| Knowledge model | Article/revision/block/claim/citation/source; minimal `Topic` (M0) and append-only `PublicationEvent` (M0); no stable assertion, no source assessment, no dispute object | Scope, coverage, splitting, definitions, regional variation, negative findings, COI and source-quality judgments have no home |
| Contribution | Human drafts + proposals; agent cycle; scoped tokens; capability/trust profiles with quotas; self-review/self-decision guards; human review queue | No onboarding, automatic trust promotion, correction intake, appeal, dispute procedure, risk classes or measured review-capacity model |
| Governance | Founder/staff authority; policy config versions; audit | No policy-change procedure, no separation of factual/editorial/community judgment, no sybil/coordination playbook, no transparency reports |
| Technical | SQLite, jobs, config snapshots, snapshots, token API with ETag/304 and idempotent writes, FTS5 search, backup/restore drill, licence fields, tests | No exports, no replay tool, no scheduled/off-host backup, no live restore, no multilingual search, no cost model, no incident runbook |
| Launch | Three demo articles plus agent drafts; local only | No seed portfolio, no beta criteria, no contributor docs, no usefulness metrics, no staged admission control |

## 6. Verification notes and limits of this assessment

- Tests were run against the current working tree. This note first read the database without migrating it; the
  M0 pass migrated the local database (`0006`/`0007`/`0008`) and the 2026-11-05 authorization pass added `0009`;
  the current suite is **190 tests** with clean checks.
- The M0 and authorization slices are code- and test-verified only: no browser-level verification was performed,
  so the new pages' visual and mobile behaviour is inferred from templates and CSS.
- No browser automation was available, so visual and mobile behaviour is inferred from templates and CSS,
  not observed.
- The TypeScript prototype's reported results were not rerun; they are labelled as reported.
- External claims and URLs are in `docs/research/` and are labelled by evidence type there.
- Nothing in this pass changes production data, credentials, deployment or the repository layout.
