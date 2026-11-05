# Change record — 2026-11-04 product-specification pass

**Author:** research and product lead (AI agent), under Justin's assignment.
**Scope:** extend the existing product specification and launch plan; conduct targeted external research; test
the rules against concrete cases; preserve prior decisions and material.
**What was not done:** no code changes, no deployment, no publication, no production data change, no credentials,
no rename, no repository reorganization, no new orchestration framework. The Django app, database and runtime
artifacts are untouched except that the test suite was run.

---

## Files added

| File | What it is |
|---|---|
| `docs/00-CURRENT-STATE.md` | Concise current-state and gap assessment: what exists and works, accepted direction, proposals/inferences/contradictions, extend-vs-replace, gap table, verification notes. |
| `docs/PRODUCT-SPEC.md` | Extended product specification v2.2 (post-critique): product definition, actors, objects/invariants, reader experience, editorial model, contribution/governance, technical/operational, launch, user flows, state machines, checklists, glossary. |
| `docs/DECISION-REGISTER.md` | 40 decisions with recommendation, status, authority route (A–E), evidence, tradeoffs/downside, reversal/revisit trigger, and product-vs-governance domain. Includes a "what the research changed" section and a "decisions requiring Justin" table. |
| `docs/WORKED-EXAMPLES.md` | Three cases (cardboard; invention of the telephone; hypothetical company/living person) walked through creation, reading, correction, source challenge, conflicting submissions, coordinated campaign, stale view, appeal/rollback, and unhappy paths where the rules fail. |
| `docs/EXPERIMENTS.md` | 15 pre-registered experiments with competing options, cases, measurements, cost, stopping rule, and the decision each would change. |
| `docs/LAUNCH-PLAN.md` | Staged path from dogfood to public contribution, seed corpus, "strong launch" definition, readiness criteria, minimum reliable core vs later, admission control, risks, decision points. |
| `docs/BRIEFING.md` | Short briefing: biggest findings, evidence vs proposed, disagreements, recommended next steps, five consequential questions for Justin. |
| `docs/CHANGE-RECORD.md` | This record. |
| `docs/README.md` | Index and reading order for the new document set. |
| `docs/research/01-reader-experience.md` | Research note on reader tasks, trust, citations, evidence inspection, views/provenance, language/reading levels, accessibility/mobile, structured views. 28 fetched sources, labelled. |
| `docs/research/02-editorial-governance.md` | Research note on editable objects, scope/coverage, neutrality checks, evidence quality, contribution/review, sybil/coordination, separation of powers, prompt injection. 32 fetched sources, labelled. |
| `docs/research/03-technical-launch.md` | Research note on versioning/provenance, API/concurrency, reproducibility, search/exports/licensing, ops, launch evidence. 34 fetched sources, labelled. |
| `docs/critique/trust-governance.md` | Independent critique of trust, epistemics and governance (preserved verbatim). |
| `docs/critique/product-feasibility.md` | Independent critique of product, reader experience and feasibility (preserved verbatim). |
| `docs/CRITIQUE-RESPONSE.md` | What changed after the critiques, what did not, and the dissent preserved. |

## Files updated (additive, pointers only)

| File | Change |
|---|---|
| `CURRENT.md` | Added a dated "Latest pass — 2026-11-04: extended product specification (proposal)" section at the top, pointing to the new docs. Prior passes and accepted decisions are preserved verbatim. |
| `README.md` | Added a short "Product specification and planning documents" section pointing to `docs/`. Setup, run instructions and existing content are unchanged. |

## Files deliberately not changed

- `~/projects/galactica/DECISIONS.md`, `EXPLORATION.md`, `docs/`, `openspec/` — the earlier decision record and
  MVP spec are preserved as-is. The new spec references and extends them; it does not overwrite them.
- `core/` application code, templates, static assets, migrations, tests — no implementation changes.
- `db.sqlite3`, `runtime/`, `.venv/`, credentials, `.env` — untouched.
- The project name, package names, URLs, repository layout — untouched.

## What was preserved from earlier work

- The 2026-10-22 decisions and 2026-10-25 spoken answers (public encyclopedia; agents propose; human review at
  the start; durable accounts; open/portable data; founder-stewarded; no ads; funding experiments).
- The 2026-10-27 course clarification (articles/explanations/diagrams are substantive; the claim ledger supports
  them; reading experience and caps remain open; human review at the start is not a permanent requirement).
- The workshop's implemented rules: immutable revisions, typed blocks, claim-level citations, source snapshots,
  proposal/review/publish/revert, stale-base refusal, audit events, config versioning, jobs, API scopes, policy
  lab. The spec proposes extensions; it does not replace these.
- The TS prototype's durable concepts: append-only claims, confidence classes, shared-origin downgrade, negative
  findings, deterministic export. The spec reuses the concepts, not the code.
- The policy lab's measured numbers and its limitations (assumed catch rates, one-model correlation).

## Critique pass

Two independent AI critics reviewed the spec, register, cases, experiments and launch plan with separate briefs;
they did not see each other's work. Their files are preserved in `docs/critique/`. The response is in
`docs/CRITIQUE-RESPONSE.md`. The critiques are advisory; they did not ratify policy. The revision pass changed
the launch scope (5–8 topics in one wedge), the review minimum (tiered, not universal two-review), the quotas
(1–2/day for new accounts), the view scope (derived artifacts only; lead/at-a-glance are revision content), the
assertion schedule (M4, with `claim_key` at M2), the appeals model (one adjudicator at launch), the reader
surface (five states, claim affordance, byline, watchlist), and the metrics (four primary metrics with n and
baseline). The dissent is preserved, including where the lead disagrees with both critics.

## What changed in the recommendations

The full register has 40 entries; these are the material changes from the earlier notes:

1. **Reader design:** from evidence-first to **clarity first, evidence one step away**; added a summary/quick-fact
   surface; disputes show **adjudication**, not raw threads (R1).
2. **Views:** from "a block or a prose section" to a **first-class object with a manifest**, pinned base, claim
   IDs, coverage, generator, `as_of`, review, staleness, follow-through and stable citation (R1, R3).
3. **Publication history:** added **`PublicationEvent`** as the first implementation slice; the mutable
   `Article.published` pointer is not history (R3).
4. **Assertions:** added stable topic-scoped assertions, with the epistemic axis (status) separate from the
   temporal axis (valid time), deprecate-not-delete (R2, R3).
5. **Review:** added **review at creation as the launch policy** (not an invariant), reviewer weighting, sampled re-review of reviewers,
   and the capacity/single-point-of-failure warning (R1, R2).
6. **Sybil/coordination:** reframed as **review-capacity protection**, with the review-pipeline attack and
   CheckUser's own limitations; no IP-based identity (R2).
7. **BLP/negative information:** added the asymmetric BLP default, the company carve-out, right of reply, and
   the no-forced-balance rules (R2).
8. **API:** added ETag/`If-Match`/`412`, `Idempotency-Key`/`409`/`422`, `problem+json`, `429`/`Retry-After`,
   cursor pagination and serial-client etiquette (R3).
9. **Ops:** added the GitLab postmortem lesson, the restore drill with row counts, per-agent daily spend caps,
   incident classes, and moderation workload metrics (R3).
10. **Licensing:** added CC BY-SA 4.0 attribution elements, §4 database rights, ODbL Produced Work vs
    Derivative Database, snapshot non-redistribution, and the "choose before public exports" constraint (R3).
11. **Launch:** added the historical calibration (Nupedia 24 articles; Wikipedia 18,000 first year; Citizendium
    <100 active; Knol; Everipedia; Grokipedia 800k then freeze), the review-capacity gate, and the "strong
    launch is not article count" definition (R3).
12. **Name:** kept D-01 open and added the T5 collision / "Truth Attractor" overclaim risk (inference, not a
    verified legal opinion).

## Evidence basis and limitations

- External research is in `docs/research/` with source URLs, access dates and labels (demonstrated, claimed,
  historical/abandoned, proposed adaptation, open). The notes record failed fetches and unverified claims.
- The research is a targeted first pass, not a systematic review. Some sources are secondary (e.g., Grokipedia
  outcome figures); some numbers are second-hand (the "which parts of an article" synthesis); the notes say so.
- The policy lab's catch rates and correlation remain assumptions, not measurements.
- No reader usability test, load test, restore drill, accessibility audit, or cost measurement was run in this
  pass. The experiments in `docs/EXPERIMENTS.md` are the plan to run them.
- No code was changed, so no new test results are claimed. The existing suite was run: 133 tests pass, system
  check clean.
- AI critique was used as advisory input; it does not ratify policy or decide factual questions. See
  `docs/BRIEFING.md` for the preserved disagreements.

## How to review this change

1. Read `docs/BRIEFING.md` first.
2. Read `docs/00-CURRENT-STATE.md` for what exists vs what is proposed.
3. Skim `docs/PRODUCT-SPEC.md` §0–§3 and §4.1–§4.6, then `docs/DECISION-REGISTER.md` for the decisions.
4. Check `docs/WORKED-EXAMPLES.md` for where the rules fail.
5. Check `docs/EXPERIMENTS.md` for what to run next.
6. Check `docs/LAUNCH-PLAN.md` for the staged path and readiness criteria.

## Open items for Justin

- D-01 name; D-30 licensing; D-34 governance transition; D-36 real vs hypothetical seed subjects; D-37 public
  beta timing. See `docs/BRIEFING.md` for the five questions and what can proceed without them.

---

# Appended pass — 2026-11-04: M0 implementation and documentation reconciliation

**Scope:** implement the first M0 slice in the workshop, then bring the documentation set in line with the
implemented slice and with the 2026-11-04 decisions. This appendix is **additive**: the product-specification
record above is preserved as written at that time; nothing in it is overwritten.

## Code and data changed (M0 slice)

| File | Change |
|---|---|
| `core/models.py` | Added `PublicationEvent` (append-only; per-article sequence; kinds `initial`/`publish`/`revert`/`import`; `published_at`/`published_by`, `previous_revision`, `policy_version`, `decision`, `reason`, `content_hash`; unique `(article, sequence)` and `(article, revision)`; event→article FK `PROTECT`); minimal `Topic` (slug/title/scope statement/parent/disambiguation flag/creator); `Watch` (unique user+article, `last_seen_at`); `Article.topic` FK. |
| `core/editorial.py` | `_record_publication` helper; `publish()`, `revert()` and `create_published_revision()` append `PublicationEvent` rows in the same transaction as the pointer update. `content_hash` now also covers claim rows and citation stance/strength, so the event hash matches the claim-level content it records. |
| `core/views.py`, `core/urls.py` | `/topics/`, `/topics/<slug>/`, `/contributors/<username>/` (public credit page, no private data), `/watchlist/` (login, opt-in, web-only digest, no email), `POST /article/<slug>/watch/` toggle, `POST /watchlist/seen/`; article page byline/topic/provenance/watch block; history page publication log. |
| `core/api.py` | Read API article payload now includes the article's `topic` (slug/title); no new API endpoint and no publish endpoint. |
| `core/admin.py` | Admin for `Topic`, read-only admin for `PublicationEvent` and `Watch`; `Article` admin shows/filters topic. |
| `core/seeding.py` | `ensure_topics` seeds 3 demonstration topics and attaches the matching demo articles once. |
| `core/migrations/0006_m0_publication_topics_watch.py` | Schema: `Topic`, `PublicationEvent`, `Watch`, `Article.topic`. |
| `core/migrations/0007_backfill_publication_events.py` | Backfill: reconstructs the publication chain for existing articles (6 events on the local DB). |
| `core/migrations/0008_publication_event_protect_article.py` | Makes `PublicationEvent.article` `PROTECT` so deleting an article cannot cascade-delete its publication history. |
| `templates/core/topics.html`, `topic.html`, `contributor.html`, `watchlist.html`; `templates/core/article.html`, `history.html`, `base.html`; `static/css/galactica.css` | New reader surfaces and supporting styles/navigation. |
| `core/tests/test_m0_publication_topic_watch.py` | 21 new tests (publication events, byline/credit page, topic pages, watchlist behaviour and privacy). |

**Verification:** `manage.py test` → **154 tests pass** (was 133); `manage.py check` clean; `makemigrations --check`
clean. Migrations `0006`/`0007`/`0008` were applied to the local SQLite database (gitignored). No browser-level
check was made; the new pages are covered by Django tests, not observed visually.

## Documentation changed in this pass

| File | Change |
|---|---|
| `CURRENT.md` | Added "Latest pass — 2026-11-04: M0 publication/topic/watch slice (implemented, verified)" at the top; retitled the spec pass to "Earlier pass"; updated the header date line and the spec pass's Next line (now points at the M0 pass). Earlier passes preserved. |
| `docs/00-CURRENT-STATE.md` | 133→154 tests; current DB counts (3 topics, 6 publication events); M0 rows in the implemented table; new §1.4 M0 status; gap-table rows for reader experience/knowledge model; unresolved-question and verification-note updates. |
| `docs/PRODUCT-SPEC.md` | §3.13 mapping rows for `Topic` (partial M0), `Article.topic`, `PublicationEvent` (added M0); new "M0 implementation status" note; §3.14 M0 progress note; §7.4 decision-rights rows (D-01/D-30/D-34); §10 decision statuses (D-30/D-34/D-36/D-37) and M0 pointer. |
| `docs/LAUNCH-PLAN.md` | §14 decision table gained an "answered 2026-11-04" status column; licensing dependency, name work item, foundation work item and timeline name-decision cells reconciled with D-01/D-30/D-34. |
| `docs/BRIEFING.md` | Test count 133→154; next-step item 1 now says the M0 slice is implemented and names the remaining M0 items; added "Implementation update — M0 slice"; linked the decision updates. |
| `docs/DECISION-REGISTER.md` | 2026-11-04 section: "nothing implemented" sentence replaced by a doc-only-vs-M0-implementation distinction; added "M0 implementation status" table; D-03 marked partial M0; D-36 implementation note (3 demo topics only); D-16 evidence updated. |
| `README.md` | Added a short note that the partial M0 slice is implemented and pointed to `CURRENT.md` for scope/limits. |
| `docs/README.md` | Added the M0 implementation status, pointed to `CURRENT.md`/the change record, and reconciled the "does not contain" list with the 2026-11-04 licensing/governance answers. |
| `docs/CHANGE-RECORD.md` | This appended pass record. |

## What is explicitly not done

- Not full M0 and no M1+ item: stable permalink/claim resolver, license/attribution fields, SQLite backup/restore
  drill, FTS5, `Idempotency-Key`/`If-Match`, correction intake, review tiers, full `Topic` scope/coverage, a
  designed public (anonymous) full-history page, email digest, and the `View`/`Assertion` objects.
- No deployment, no production data change, no credentials, no rename, no repository reorganization, no commit.
- The editorial gate, review roles, quotas and the write API are unchanged; the read API only exposes the new
  topic field.
- The 3 seeded topics are demonstration data, not a seed-corpus decision; the wedge and anchor-topic list remains
  open (D-36).
- The extended `content_hash` is not backfilled onto existing revision/proposal rows; existing stored hashes remain
  as they were, so repeat-of-rejected detection only compares hash values produced after this pass.

## Decision statuses recorded

The 2026-11-04 answers (D-01 interim, D-30 accepted subject to counsel, D-34 accepted with foundation deferred,
D-36 partly answered, D-37 stage order accepted with timing open) and the three recorded open questions (OQ-1
claim-ledger/article bridge, OQ-2 deterministic authorization/quota, OQ-3 authored-vs-generated views) are in
`docs/DECISION-REGISTER.md` under "Decision updates — 2026-11-04". No other decision status changed.

---

# Appended pass — 2026-11-05: authorization, state machine and human review dashboard

**Scope:** implement the first slice of the lead-authored design note
[`AUTHORIZATION-STATE-MACHINE.md`](AUTHORIZATION-STATE-MACHINE.md) — one deterministic evaluator for editorial
capabilities, states, transitions, quotas and relationship guards — plus the human review queue, then record it.
This appendix is **additive**; the 2026-11-04 records above are preserved as written.

## Code and data changed (2026-11-05 slice)

| File | Change |
|---|---|
| `core/authorization.py` (new) | Capability/trust table (`new`/`standard`/`trusted`/`steward`); derived proposal states (`submitted`/`under_review`/`approved`/`published`/`rejected`/`changes_requested`); one `can()` evaluator with reason codes; rolling 24-hour quotas; self-review, self-decision and self-publication guards; evaluation refusal; agent-scope checks. |
| `core/models.py` | `ContributorProfile` (trust level, notes; staff default `steward`, others `standard`; admin-editable) and `Review.reviewer` user FK. |
| `core/migrations/0009_contributor_profiles_reviewer.py` | Creates `ContributorProfile`, adds `Review.reviewer`. |
| `core/editorial.py` | `_authorize` helper; authorization enforced in `open_proposal`, `submit_draft`, `save_draft`/`ensure_draft`, `record_review`, `decide`, `publish`, `revert`; audit detail flags `same_agent` reviews. |
| `core/views.py`, `core/urls.py` | `/review/` human queue (`review_dashboard`, login required, `view_review_queue` capability); human review form posts recorded with `origin=human` and the reviewer. |
| `templates/core/review_dashboard.html`, `templates/core/proposal.html`, `templates/base.html`, `static/css/galactica.css` | Queue template with state filters, counters, coverage, objections and stale flags; proposal-page human review form; nav link; styles. |
| `core/tests/test_authorization_dashboard.py` | 17 new tests (capability boundaries, anonymous/`new` denial, self-review/decision/publication, evaluation refusal, quotas, role duplication, state transitions, dashboard access and the human review form). |

**Verification:** `manage.py test` → **171 tests pass** (was 154; 17 new); `manage.py check` clean;
`makemigrations --check` clean. Migration `0009` was applied to the local SQLite database (gitignored). No
browser-level check was made; the queue and form are verified by Django tests, not observed visually.

**Quotas are starting parameters, not measurements:** `new` 1 proposal/day and 0 human reviews; `standard` 5/10;
`trusted` 10/25; steward unlimited; rolling 24 hours; human reviews counted only with `origin=human`. E2/E3 and
the review-hour ratio should calibrate them.

**Same-agent caveat:** same-agent reviews are allowed in v1 but audited as `same_agent: true` and are **not
independent evidence**; do not count them when measuring reviewer value.

## Documentation changed in this pass

| File | Change |
|---|---|
| `docs/AUTHORIZATION-STATE-MACHINE.md` | Lead-authored design note (added before this pass); left unrewritten, linked from the index, register, briefing and this record. |
| `CURRENT.md` | New "Latest pass — 2026-11-05: authorization, state machine and human review dashboard (implemented, verified)"; the M0 pass retitled "Earlier pass"; header date line updated. Earlier passes preserved. |
| `docs/DECISION-REGISTER.md` | Summary rows and detailed entries for D-41 (authorization and editorial state machine) and D-42 (human review dashboard), both accepted direction + implemented v1; new "Implementation update — 2026-11-05" section with the quota caveat and open calibration questions; implementation notes on D-19/D-23 keeping their statuses distinct; OQ-2 marked partly addressed; header and closing pass notes updated. |
| `docs/BRIEFING.md` | Test count 154→170; new "Implementation update — 2026-11-05"; E2/E3 guidance excludes same-agent reviews; a "do not treat trust levels as identity verification" caution; links to the design note and register section. |
| `docs/README.md` | Design note added to the reading order (item 4); decision count 40→42; implemented-status paragraph covers both slices; `accepted` definition includes implemented accepted direction; scope note on what is not a full policy engine. |
| `docs/CHANGE-RECORD.md` | This appended pass record. |

## What is explicitly not done

- Not a full policy engine: no external policy engine, no auto-assignment/claiming, no automatic trust promotion,
  no `withdrawn` state, no appeal/dispute state machine, no trust-management UI beyond Django admin, no
  per-reviewer calibration.
- No identity verification, real-name check, reputation score or per-topic expertise claims; `ContributorProfile`
  trust levels are editorial capability only.
- No change to the publication policy minimums or objection rules (D-19) and no change to the identity direction
  (D-23). No agent publish scope.
- No deployment, no production data change, no credentials, no rename, no repository reorganization, no commit.

## Decision statuses recorded

D-41 and D-42 are **accepted direction + implemented v1 (2026-11-05)**; their open calibration questions (trust
promotion, `new` queue access, quota numbers, edited-but-not-authored decisions, withdrawal behavior) are listed in
`docs/DECISION-REGISTER.md` under "Implementation update — 2026-11-05". D-19 and D-23 keep their existing
statuses. OQ-2 is partly addressed by D-41; OQ-1 and OQ-3 are unchanged. No other decision status changed.

---

# Change record addendum — 2026-11-05 M0 remainder and E1/E4 kits

**Scope:** complete the M0 items that the 2026-11-04 M0 pass explicitly left open, then prepare E1/E4. No M1+
feature, no publication-policy change, no rename, no deployment, no credentials, no production data change.

## Added

| File | What it is |
|---|---|
| `core/licensing.py` | License table, default, citation strings. Not legal advice. |
| `core/search.py` | `SearchDocument` build, published-only FTS5 search, match reasons, snippet, integrity report. |
| `core/idempotency.py` | `Idempotency-Key` lifecycle, replay, `If-Match` check, `application/problem+json` errors. |
| `core/migrations/0010_article_attribution_article_license_and_more.py` | Article/Source/PublicationEvent license fields; `SearchDocument`; `IdempotencyRecord`. |
| `core/migrations/0011_search_fts_and_license_backfill.py` | FTS5 table/triggers, search backfill, publication licence backfill. |
| `core/migrations/0012_backfill_content_hashes.py` | Backfill empty legacy `Revision`/`PublicationEvent`/`SearchDocument` content hashes. |
| `core/management/commands/rebuild_search.py`, `check_search.py` | Rebuild and verify the derived index. |
| `core/tests/test_m0_remainder.py` | 19 tests for permalinks, claim resolver, licenses, search, idempotency and preconditions. |
| `templates/core/claim.html`, `templates/core/search.html` | Public claim resolver and search results. |
| `scripts/backup.sh`, `scripts/restore_drill.sh` | Online SQLite backup + manifest; read-only restore drill. |
| `docs/OPERATIONS.md` | Backup/restore runbook, drill record, RPO/RTO caveat, "an export is not a backup". |
| `experiments/E1-reader-task/` | Protocol, synthetic sessions template, stdlib analysis with `--self-test`. |
| `experiments/E4-correction-triage/` | Protocol, 30 synthetic cases, triage log, stdlib analysis with `--self-test`. |

## Updated

| File | Change |
|---|---|
| `core/models.py` | `Article.license`/`attribution`, `Source.license`/`attribution`, `PublicationEvent.license`, `SearchDocument`, `IdempotencyRecord`. |
| `core/editorial.py` | Publication events snapshot the licence and refresh search; `open_proposal` accepts and rechecks `expected_base_id` under the article lock; source licence fields. |
| `core/api.py` | Claim payload/resolver; licence/citation fields; ETag/304; idempotent write wrapper; `If-Match` on agent proposals; `problem+json` errors. |
| `core/views.py` | Revision permalink, claim resolver, search page, shared article context, source form licence fields. |
| `core/urls.py` | `/article/<slug>/r/<n>/`, `/claims/<uuid>/`, `/search/`, `/api/v1/claims/<uuid>/`. |
| `templates/core/article.html`, `_article_body.html`, `history.html`, `base.html` | Canonical link, citation/licence block, claim links, search nav, revision permalinks, publication licence column. |
| `static/css/galactica.css` | Citation, claim resolver and search styles. |
| `core/admin.py` | Licence/search/idempotency admin visibility. |
| `README.md` | M0 completion, new commands, write-API contract, experiment-kit pointer. |
| `CURRENT.md` | New latest-pass section; previous passes preserved; stale absolute path corrected. |
| `docs/00-CURRENT-STATE.md`, `docs/PRODUCT-SPEC.md`, `docs/DECISION-REGISTER.md`, `docs/BRIEFING.md`, `docs/README.md` | M0 status/test counts, D-43, limits, E1/E4 no-results note. |

## Verification

- `manage.py test core` → **190 tests pass** (171 before; 19 new). Expected logging test still prints a
  `RuntimeError: secret detail` traceback; the suite is green.
- `manage.py check` clean; `makemigrations --check` clean.
- Migrations `0010`–`0012` applied locally; `check_search` reports 3 documents / 3 indexed / ok.
- `scripts/backup.sh` and `scripts/restore_drill.sh` run on 2026-11-05: PASS, 8 tables, SHA-256
  `6191b646…`, 1,335,296 bytes; the live DB was not opened by the drill and no live restore was executed.
- No browser-level visual check; pages are Django test-client/HTML verified. The app was restarted after the
  change so the running process serves the new code.

## Explicitly not done

- No claim merge/alias/301 map and no `claim_key` across revisions (M2); claim ids are revision-bound.
- No multilingual/CJK search evaluation; FTS5 uses `unicode61`; no search telemetry.
- No scheduled/off-host backup, retention, encryption or live restore; the drill verifies a copy only.
- Idempotency covers the JSON write API only; web forms are not wrapped; error responses are not cached.
- License fields are implementation only; the CC BY-SA recommendation still awaits counsel.
- E1/E4 have protocols and synthetic fixtures only; **no human sessions were run and no result exists**.
- No M1+ correction intake, review tiers, full topic scope/coverage, public full-history page, email digest,
  `View`/`Assertion` objects, deployment, rename or production data change.
