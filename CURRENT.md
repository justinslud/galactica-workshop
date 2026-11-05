# CURRENT — Galactica Workshop

**Updated:** 2026-11-05 (latest pass: authorization/state-machine/human-review-dashboard slice, implemented and
verified; previous: M0 publication/topic/watch slice, then extended product specification, proposal)
**Location:** `/home/justin/projects/galactica-workshop` (separate Django app; the TypeScript project at
`/home/justin/projects/galactica` is untouched)

## Objective

Build the first usable local Galactica workshop: editable, versioned articles; proposals with evidence and independent
reviews; human publication, correction and revert; configurable runner/reviewer/policy versions; background jobs; and
repeatable editorial test cases. Django + SQLite, localhost only, no Docker/Redis/SPA.

## Latest pass — 2026-11-05: authorization, state machine and human review dashboard (implemented, verified)

**Objective:** replace scattered `is_staff` checks with one deterministic evaluator for capabilities, editorial
states, transitions, relationship guards and quotas, and give humans a single queue for what needs review — without
changing the publication policy minimums, the identity model or the agent publish boundary.

**Implemented (workshop code):**
- `core/authorization.py` — capability/trust table (`new`/`standard`/`trusted`/`steward`), derived proposal states
  (`submitted`, `under_review`, `approved`, `published`, `rejected`, `changes_requested`), one `can()`
  evaluator with explicit reason codes, rolling 24-hour quotas, self-review/self-decision/self-publication guards,
  evaluation refusal, and agent-scope checks.
- `ContributorProfile` (staff default `steward`, other accounts default `standard`; admin-editable; a capability
  tier, not identity verification) and a `Review.reviewer` user FK; migration
  `0009_contributor_profiles_reviewer`.
- Services now enforce authorization in `open_proposal`, `submit_draft`, `save_draft`/`ensure_draft`,
  `record_review`, `decide`, `publish` and `revert`; the human review form records `origin=human` and the reviewer.
- `/review/` human queue (standard/trusted/steward; anonymous redirects to login, `new` denied) with state filters,
  counters, review coverage, objections, stale flags and no auto-assignment; nav link; a human review form on the
  proposal page.
- Quotas (starting parameters, not measured): `new` 1 proposal/day and 0 human reviews; `standard` 5/10; `trusted`
  10/25; steward unlimited; rolling 24 hours; human reviews counted only with `origin=human`.
- Same-agent reviews are allowed in v1 but recorded in the audit detail as `same_agent: true` and are **not
  independent evidence**.

**Verification:** `manage.py test` → **171 tests pass** (was 154; 17 new in
`core/tests/test_authorization_dashboard.py`); `manage.py check` clean; `makemigrations --check` clean. Migration
`0009` was applied to the local DB (gitignored). No browser-level check was made; the queue and form are
test-verified only. Design note: `docs/AUTHORIZATION-STATE-MACHINE.md`.

**Not implemented in this slice:** auto-assignment/claiming, automatic trust promotion, an external policy engine,
the `withdrawn` state, appeal/dispute state machines, a trust-management UI beyond Django admin, per-reviewer
calibration, and identity verification or a reputation score.

**Limits:** the evaluator is a small, readable transition table, not a full policy engine; the quota numbers are
starting parameters, not calibration results; same-agent reviews are non-independent; the `created_by` authorship
test is conservative but incomplete. The publication policy minimums (D-19) and the identity direction (D-23) are
unchanged. No rename, no deployment, no production data change, no credentials.

**Next:** run E2/E3 to calibrate quotas and reviewer value (excluding same-agent reviews), then decide trust-promotion
rules; keep the human gate.

## Earlier pass — 2026-11-04: M0 publication/topic/watch slice (implemented, verified)

**Objective:** implement the first M0 slice from the extended specification — durable publication history, a
minimal topic object, and the start of the return loop — without changing the editorial gate, the API, quotas or
the project name.

**Implemented (workshop code):**
- `PublicationEvent` (append-only): per-article `sequence`; kinds `initial`/`publish`/`revert`/`import`;
  `published_at`/`published_by`, `previous_revision`, `policy_version`, `decision`, `reason`, `content_hash`
  (title/opening/blocks/claims/citations, now including claim-level structure and stance/strength);
  unique `(article, sequence)` and `(article, revision)`; event→article FK is `PROTECT`, so deleting an article
  cannot cascade-delete its history. `Article.published` is now a cache, not the history.
  `_record_publication` appends events from `publish()`, `revert()` and `create_published_revision()`.
- Minimal `Topic` (slug, title, scope statement, parent, disambiguation flag, `created_by`) and an `Article.topic`
  FK; 3 demonstration topics seeded and attached to the existing demo articles; `/topics/` and `/topics/<slug>/`
  list published articles only.
- Opt-in `Watch` (unique per user+article, `last_seen_at`); login-only `/watchlist/` with a **web-only digest, no
  email**; `POST /article/<slug>/watch/` toggle and `POST /watchlist/seen/` (one row or all).
- Reader surfaces: `/contributors/<username>/` public credit page (no private data), article-page
  byline/topic/provenance/watch block, and the history-page publication log.
- Migrations `0006_m0_publication_topics_watch`, `0007_backfill_publication_events` (backfilled 6 existing
  publication events on the local DB) and `0008_publication_event_protect_article` (protects history from article
  deletion).

**Verification:** `manage.py test` → **154 tests pass** (was 133; 21 new in
`core/tests/test_m0_publication_topic_watch.py`); `manage.py check` clean; `makemigrations --check` clean.
Migrations were applied to the local DB (gitignored). No browser-level check was made, so the new pages are
verified through the Django test client and checks rather than observed in a browser.

**Not implemented in this slice — do not read as done:** stable permalink/claim resolver, license/attribution
fields, SQLite backup/restore drill, FTS5, `Idempotency-Key`/`If-Match` (M0 remainder); correction intake, review
tiers, full `Topic` scope/coverage (M1); a designed public (anonymous) full-history page, email digest, and the
`View`/`Assertion` objects (later). This is a partial M0, not a launch product; the editorial gate, review roles,
quotas and API are unchanged. No rename, no deployment, no production data change, no credentials.

**Next:** finish the remaining M0 items (permalink + claim resolver, license fields, backup/restore drill, FTS5,
idempotency), then run E1/E4 per the briefing. Do not start M1 review tiers or correction intake before the
reader-task and correction-triage experiments.

## Earlier pass — 2026-11-04: extended product specification (proposal, no code change)

**Objective:** use the existing work, targeted external research and a critique pass to substantially extend the
product specification and launch plan — not to build another MVP.

**What changed:** added `docs/` with a current-state/gap assessment, an expanded product specification (v2.2), a
40-entry decision register with authority routes, worked examples (cardboard; invention of the telephone; a
hypothetical company/living person), a 15-item experiment backlog, a staged launch plan, a briefing, a change record
and three labelled research notes. `README.md` points to the new index. No application code, database, runtime,
deployment or name was changed; the earlier decision record in `~/projects/galactica` is preserved.

**Key findings that changed recommendations:** readers want clarity first and rarely click citations (0.29% of page
views); showing raw process can lower measured quality judgements; review capacity is the binding constraint and
review value decays with delay; a permalink is not a reproduction, so derived views need a manifest; publication
history needs an append-only event, not the mutable `Article.published` pointer. Two independent critiques are
preserved in `docs/critique/`; the revision narrows the public launch to **5–8 topics in one citation-costly
wedge**, tiers the review minimum, cuts new-account quotas to 1–2/day, moves the full `Assertion`/`View` objects
later (claim_key and revision-content views first), adds byline/watchlist, and replaces vanity metrics with four
primary metrics.

**Verification:** `manage.py test core` → 133 tests pass, system check clean (run 2026-11-04). The web server and
worker were not running during this pass; no browser-level verification was repeated. External claims are in
`docs/research/` with URLs and evidence labels; the policy lab's catch rates remain assumptions.

**Next:** read `docs/BRIEFING.md`; implement `PublicationEvent` + `Topic` first (done in the M0 pass above); run
reader-task and correction-triage experiments before expanding the surface; keep the human gate until measured
catch rates justify otherwise.

## Earlier pass — 2026-11-04: policy lab v1 (simulated)

**Objective:** make the autonomy question measurable instead of argued.


### Implemented

- `core/policy_lab.py` — pure simulation, no database, no model calls, no network. Scenarios carry planted defects
  (unsupported claim, overgeneralization, dropped qualification, number change, citation laundering, dead link, framing
  omission). Panels carry per-role catch rates plus a `correlation` factor: 1.0 means every reviewer sees the same
  signal, so adding roles adds no information. Policies are ordered rule lists with an objection budget. Every trial is
  deterministic for a seed.
- `manage.py run_policy_lab` writes `runtime/lab/latest.json` and a timestamped copy.
- `/lab/` renders the policy × risk-class matrix (escape rate and human reviews per 100 edits); nav link next to
  Test cases.
- 20 tests: rule matching, determinism, correlation, audit sampling, report aggregation, view rendering.

### Measured (300 trials per cell, seed 7, 12 scenarios, 6 policies, 3 panels)

- **one-model panel** (correlation 0.85, the current setup): publishing when no reviewer objects escapes **44.2%** of
  standard-risk and **57.2%** of high-risk defective edits.
- **mixed panel** (correlation 0.30): 22.3% and 44.0%.
- **weak panel**: 75.8% and 78.8%.
- Auditing half of standard edits does not rescue it: 44.8% escape at 78 human reviews per 100 edits, worse than
  reviewing all of them.
- Tiered policy (autonomy only for cosmetic/low) is 0% escape but 100 human reviews per 100 edits for standard — no
  better than human-all with today's panel.

### Interpretation

The lab does not say "agents cannot be trusted". It says the current panel, as configured, does not buy a safe
delegation cell for ordinary edits. Escape falls roughly with correlation, so the useful lever is reviewer
independence, not a cleverer rule list.

### Limitations

- Catch rates and correlation are assumptions, not measurements.
- 12 synthetic scenarios, one defect mix per risk class; no real model output feeds the lab yet.
- `human / 100` counts queued plus audited edits; block explanations are not counted as human work.
- No persistence beyond the JSON report; no shadow mode yet.

### Next

Measure catch rates from recorded review runs (the planted-defect evaluation already produces per-claim verdicts) and
replace the assumed numbers. Then re-run the matrix before proposing any auto-publication cell.

## Latest pass — 2026-10-28: claim-level citation enforcement (verified)

**Objective:** make factual claims identifiable and enforceable without turning the article into a claim ledger.

### Implemented

- New `Claim` model: stable UUID, block id, text, character offsets, `direct` / `partial` / `conflicting` / `absent`,
  support note. `Citation` now links to a claim with `stance` and `strength`; quotes are checked against preserved
  snapshots. `Review.claim_verdicts` stores per-claim verdicts.
- Agent writer must return `claims`; each is an exact substring of its block, with at least one citation. Uncited writer
  claims are rejected. The agent propose API now requires claims too.
- Reviewer prompts use claim IDs. Fact-check and citation must cover every claim; missing IDs fail the job. Claim
  verdicts include an issue code (`unsupported`, `overgeneralized`, `misattributed`, `quote_absent`,
  `conflict_flattened`).
- Article prose is unchanged; “Claims and evidence” expands per block. Proposal pages show a claim table with IDs,
  status, citation stance/strength, snapshot SHA-256, quotes and reviewer objections.
- `backfill_claims` migrated the existing AlterEgo revisions without editing text or dropping citations/reviews:
  - real proposal: 15 claims, 21 citations attached, 2 composite disagreement claims marked `conflicting`;
  - evaluation candidate: 16 claims (includes the uncited planted claim), 21 citations attached.

### Re-run of the planted evaluation (no new research)

- Job: `1015ac20-887c-4946-8cf7-465325b12d9d`
- Evaluation proposal: `c11c74b9-a17b-4e07-8d5a-f753ed76e325` (origin `evaluation`, pending, never publishable)
- Planted claim ID: `d10d7fc4-edd1-46cd-aa23-cfbc579eb6e2`
- Claim: “AlterEgo is already a widely deployed commercial product used by millions of people.”
- Claim status: `absent` (0 citations)
- Fact-check: overall **object**, exact claim `object / unsupported`
- Citation: overall **object**, exact claim `object / unsupported`
- Readability: overall support; per-claim abstain (it does not assess evidence support)
- Model route: `opencode-go/beam-free`; 3 application calls, all usage-measured.
- No publication, no approval, no auto-publication.

### Machine enforcement vs model judgment

Machine-enforced: claim text must be a stable substring; citation source must be preserved for the job; quote must
exist in the snapshot; citation stance/strength map to a computed support status; agent writer/API proposals without
claims are rejected; fact/citation reviewers must return every claim ID; uncited claims are marked `absent`.

Remains model judgment: whether the passage actually entails the claim, whether a claim overgeneralizes, whether a
citation is misattributed, and whether a conflict is genuine rather than merely textual. The live run shows the model
can point to the exact claim, but this is one model and one run—not independent corroboration.

Readable article experience survived: prose is untouched; provenance is collapsed. Article claim UI is covered by a
test that publishes claims and checks the expansion.

### Verification

- `.venv/bin/python manage.py check` — OK.
- `.venv/bin/python manage.py test core` — **113 tests pass**.
- `backfill_claims` is idempotent; `run_claim_evaluation` reuses existing snapshots and proposal.
- Rendered proposal/job pages 200; claim IDs, `conflicting`, `unsupported`, snapshot hashes and “No citation attached”
  visible. No server traceback.

### Actual processes (verified with `ps` at 2026-10-28 19:20 EDT)

- Web: PID **407586** — `.venv/bin/python manage.py runserver 127.0.0.1:8001 --noreload` → http://127.0.0.1:8001/
- Worker: PID **407588** — `.venv/bin/python manage.py run_worker`
- Logs: `/tmp/opencode/galactica-server.log`, `/tmp/opencode/galactica-worker.log`
- No queued/running jobs at verification. PIDs change on restart; check `ps -eo pid,args | grep manage.py`.
- Unrelated port 8000 belongs to other projects, not this app.

### Repository

- Local Git repository initialized on `main` (authorized in this pass).
- Private GitHub: <https://github.com/justinslud/galactica-workshop>
- Excluded: `.venv/`, `db.sqlite3`, `runtime/`, `__pycache__/`, logs, `.env`, generated staticfiles. The database and
  preserved runtime artifacts stay local; they are not in the repository.

### Usage status

- New evaluation job: 3/3 reviewer runs measured.
- Prior successful jobs: all previously empty rows were backfilled from OpenCode session message API; 16 of 19 total
  runs measured. The 3 unmeasured rows are earlier failed “Agent not found” attempts, not successful runs.
- `usage.calls` counts provider steps; `Job.model_calls` counts application calls.

### Limitations

- Claims are sentence/bullet units, not semantic entailment proofs.
- One model (beam-free) served writer and all reviewers; repeated reviews are not independent external corroboration.
- Human/demo revisions still lack claim rows until backfilled; the human editor does not yet create claims.
- Claim extraction for migration is deterministic and heuristic (bullets, then sentences); it does not parse tables,
  timelines or HTML details.
- No browser automation; pages checked through rendered HTML/test client.
- No publication or approval.

### Next single experiment (proposed)

Use two sources that genuinely contradict each other on the same narrow claim (not just different dates/scope), with
human-labelled claim verdicts, and measure whether the claim-level panel preserves the conflict and whether reviewers
avoid false support. That is the best next test before any low-risk publication discussion.

## Earlier pass — 2026-10-28: conflicting-evidence experiment (superseded status; kept for record)


**Objective:** test editorial judgment with at least two sources that differ materially, while preserving disagreement
and checking whether reviewers catch a planted overgeneralization. No new orchestration, no publication.

### What ran

- **Sources preserved separately:**
  - `https://en.wikipedia.org/wiki/Subvocal_recognition` — broad survey; says a 2019 AlterEgo study.
    sha256 `ef5b04ae70c03d96e44d04297caa84767a78cccb4160e542bcc8307f0708db29`.
  - `https://www.media.mit.edu/projects/alterego/overview/` — project page; says originated 2018, IUI 2018.
    sha256 `3fae53abc969a4ac4115bce0cf787b0d1235b536d69e3a6014b4256f9095514e`.
  - `https://www.media.mit.edu/publications/alterego-IUI/` — MIT publication page found by the researcher.
    sha256 `4b02cafa7803784d1ee27d1c71717fd7916438bff63d98da5cbcf256a5229805`.
- **Job:** `76b94791-6090-4ed7-b3bc-2171ec52bcc3`, succeeded, 8 application model calls (11 provider steps).
- **Model route:** `opencode-go/beam-free` for researcher, writer and all six reviewer sessions (three real, three
  evaluation). Catalog cost zero; no paid fallback.
- **Instructions:** provisional `instructions / disagreement-experiment` v1, which requires “Supported by both
  sources”, “Supported by one source”, and “Disagreement and scope”. Snapshot recorded on the job.
- **Real proposal:** `df03834d-2bb7-4a77-a791-509def204849`, article `alterego-silent-speech-project`, **pending**,
  article **not published**.
- **Real reviews:** fact_check support, citation support, readability support.
- **Separate adversarial evaluation candidate:** `628ee877-e0a1-4a6b-870d-d9ebd25e4126`, origin `evaluation`, never
  publishable. Planted claim: “AlterEgo is already a widely deployed commercial product used by millions of people.”
  Fact-check **object**, citation **object**, readability support. The claim was caught.

### Did it preserve disagreement?

Yes. The proposal says the MIT publication records IUI 2018 (5 March 2018) while Wikipedia describes a 2019 study by
Arnav Kapur; it also contrasts Wikipedia's field-level framing (brain-to-device communication, speech-muscle
stimulation) with the project page's natural-language/bone-conduction, assistive-scope framing. It did not resolve the
date conflict into a false consensus and did not convert the uncertainty into confident prose.

### Citation integrity

- 21 citations; every quote normalised to text in its preserved snapshot (machine check passed).
- 15 bullets; each has at least one citation support note whose wording overlaps the bullet.
- **Weakness:** the writer collapsed all sections into one markdown block. Citations therefore attach to the block, not
  to individual sentences. Support notes make the mapping inspectable, but it is not machine-enforced claim-level
  attachment. This is the highest-value next experiment.

### Usage bug: cause, fix, coverage

- Cause: OpenCode emits `step_finish` for tool-using calls but **not for text-only writer/reviewer calls**, so four of
  five earlier `AgentRun` rows had empty usage. The researcher also had three step events and only the last was kept.
- Fix: sum all `step_finish` events; fall back to `opencode api get /api/session/<id>/message` for measured tokens/cost;
  `AgentRun.usage_measured` / `usage_note` make absence explicit. Only numeric usage is read; message content is not
  stored by this path.
- Backfill: old job `b06e4856-d1c3-424c-a9d9-6e6fc115c3f0` was backfilled from its session ids. All five runs now show
  measured usage (job totals: 8 steps, 31,298 input, 1,048 output, 4,489 reasoning, 7,936 cache-read, reported cost 0).
- Regression tests: multiple step events summed, session-message fallback, explicit unmeasured note. Full suite now
  **106 tests pass**.

### Verification

```sh
.venv/bin/python manage.py check
.venv/bin/python manage.py test core          # 106 OK
.venv/bin/python manage.py run_agent_cycle --topic "AlterEgo silent-speech project" \
  --question "When was the AlterEgo silent-speech project presented at IUI, and how do a general survey and the project's own page describe its scope?" \
  --seed-url "https://en.wikipedia.org/wiki/Subvocal_recognition" \
  --seed-url "https://www.media.mit.edu/projects/alterego/overview/" \
  --instructions-family disagreement-experiment \
  --evaluation-claim "AlterEgo is already a widely deployed commercial product used by millions of people." --wait
```

Rendered checks: real proposal page 200 with agent banner and all three sections; evaluation proposal page 200 and
marked never publishable; job page 200 with adversarial result, agent runs and preserved evidence; no server traceback.

### Actual running processes (checked 2026-10-28 15:59 EDT)

- Web: PID **327354** — `.venv/bin/python manage.py runserver 127.0.0.1:8001 --noreload` → http://127.0.0.1:8001/
- Worker: PID **327356** — `.venv/bin/python manage.py run_worker`
- Logs: `/tmp/opencode/galactica-server.log`, `/tmp/opencode/galactica-worker.log`
- Unrelated: port 8000 has other project servers (not this app). No queued/running jobs after the experiment.

### Limitations and unresolved

- Citations are block-level, not sentence-level (see above).
- One model served writer and all reviewers; three reviews are not independent external corroboration.
- Reviewers share the same evidence packet.
- The real proposal includes a cited mention of ALS/MS as the project’s stated focus; it makes no medical efficacy or
  treatment claim. The topic was chosen as low-stakes publication/scope, not medicine.
- `websearch` remains unavailable in this environment; explicit `--seed-url` values were used for reproducibility, and
  the researcher added one extra MIT publication URL. Intake still validated/preserved all three.
- No browser automation; pages inspected via rendered HTML/test client.
- No approval, publication, auto-publication, Git init or commit.

### Next experiments (proposed, not accepted)

1. Sentence-level or section-block claim/citation attachment, then re-run the same two-source test.
2. A genuinely contradictory source pair (not just date/scope) to test whether reviewers reject forced synthesis.
3. Human audit of this pending proposal and the adversarial candidate to measure false-support/false-object rates.

## Earlier pass — 2026-10-28: bounded single-source cycle (superseded status; kept for record)


**Objective:** one real, bounded agent cycle — research a narrow topic, preserve snapshots, produce a cited proposal,
run isolated fact/citation/readability reviews, leave it pending. Not general publication.

### Accepted decisions this pass

- **Least-privilege profiles** in `core/agents.py`: `researcher` may use `websearch` and `webfetch` only for allowlisted
  HTTPS hosts; `writer` and `reviewer` have deny-all permissions. No subagents, shell, edits or reads. Each profile is a
  primary OpenCode agent with bounded `steps`.
- **Application intake is the trust boundary** (`core/research.py`): the researcher only suggests URLs; Django fetches.
  HTTPS only, allowlist, no credentials/IP literals/local names, all resolved addresses must be global, proxies disabled,
  redirects/time/bytes bounded, content types restricted. Failures are recorded as snapshots with no content.
- **Snapshots are raw evidence**, separate from interpretation: URL, final URL, retrieval time, status, content type,
  bytes, SHA-256, title, raw text, bounded excerpt, extraction notes, source link.
- **Writer is evidence-bound**: markdown only; citations must name a preserved source for that job; quotes must occur in
  the raw snapshot. The writer sees the packet, not the open web.
- **Three isolated reviewer sessions**: fact_check, citation, readability. Each receives candidate plus
  citation–evidence pairs and the packet; never another verdict. They are independent sessions over shared evidence, not
  independent evidence.
- **Agent identity distinct from operator** (`Agent`, `AgentCredential`, `AgentRun`). Tokens are scoped and stored as
  salted hashes with a lookup prefix. Audit records carry actor/operator, agent, model, configuration versions and job.
- **Small JSON API** with token auth: read, research, propose, review. No publish endpoint. `publish_low_risk` is a
  declared scope with no enforcement path.
- **Low-risk policy is a proposal, not policy**: `policy / low-risk-shadow-proposal`, non-default, proposal-only,
  shadow mode, `auto_publish: false`, 10% human audit starting point, promotion only from measured false-approval rates.
- **Default runner/reviewer versions moved to free `opencode-go/beam-free`** after the other free models hit quota. New
  provisional versions (runner opencode-free v2, reviewers panel-four v2); older versions kept unchanged.

### Verified

- Migrations `0002` and `0003` applied.
- `manage.py test core`: **103 tests pass**, including intake refusal, redirect allowlist, snapshot hash/raw preservation,
  failed fetch, malicious source instructions, quote-absence rejection, unpreserved source rejection, reviewer
  objection, profile permissions, API scopes/revocation, propose evidence checks, attribution, budget exhaustion, retry
  snapshot and SIMULATED refusal.
- Live bounded cycle succeeded in ~54 seconds, 5 model calls:
  - job `b06e4856-d1c3-424c-a9d9-6e6fc115c3f0`
  - proposal `7f29bd60-bc31-4e37-adfb-5c405fc40c0c`, status **pending**
  - article `silent-speech-interfaces`, provenance `agent`, **not published**
  - model route: `opencode-go/beam-free` for researcher, writer and all three reviewers (catalog cost zero)
  - source: `https://en.wikipedia.org/wiki/Subvocal_recognition`, 117,228 bytes,
    sha256 `ef5b04ae70c03d96e44d04297caa84767a78cccb4160e542bcc8307f0708db29`
  - 6 citations, every quote present in the snapshot; reviews: fact_check support, citation support, readability support
  - 5 `AgentRun` rows; audit event `agent_cycle_completed` has actor `admin`, agent `galactica-agent`, model, config
    versions and job
- Staff pages render the agent banner, proposal origin/model/job, job agent-run table and preserved-evidence block.
  Workshop shows the agent-cycle card and the low-risk policy as proposal-only, with Edit/Make default hidden/blocked.
- Anonymous `/article/silent-speech-interfaces/` shows "Pending; not published" and no staff controls.
- API without a token returns 401. Static assets 200. No server traceback.

### Failures and fixes

- **`Agent not found: researcher`** in the runner. Cause: inherited `PWD` pointed at the project root while the process
  ran in the sandbox, so OpenCode missed the sandbox `opencode.json`. Fixed by setting `PWD` to the sandbox and stripping
  inherited `OPENCODE_*` session variables. Fresh sessions are now genuinely fresh.
- Free `opencode/deepseek-v4.1-flash-free` and `opencode/glm-5.3-flash-free` returned `provider.free-limit` (429).
  `opencode-go/beam-free` worked. No paid fallback was attempted.
- `websearch` returned "Unable to search the web" during the live run; the researcher supplied the allowlisted URL from
  model knowledge. Intake, not search, is the trust boundary. Recorded as a limitation.
- One `arxiv.org` fetch timed out during manual intake testing; no source was silently substituted.
- DNS rebinding is only partially mitigated (pre-request resolution + redirect revalidation, proxies disabled).

### Running processes

- Web: `.venv/bin/python manage.py runserver 127.0.0.1:8001 --noreload` → http://127.0.0.1:8001/
- Worker: `.venv/bin/python manage.py run_worker`
- Logs: `/tmp/opencode/galactica-server.log`, `/tmp/opencode/galactica-worker.log`

### Exact commands

```sh
cd /home/justin/projects/galactica-workshop
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py runserver 127.0.0.1:8001
.venv/bin/python manage.py run_worker                      # second terminal
.venv/bin/python manage.py test core
.venv/bin/python manage.py check_runner
.venv/bin/python manage.py create_agent --name galactica-agent --operator admin
.venv/bin/python manage.py run_agent_cycle --topic "Silent speech interfaces" \
  --question "According to the Wikipedia summary, what input methods are used for silent speech interfaces?" --wait
```

API example (token issued once by `create_agent --issue-token`; keep it out of the repo):

```sh
curl -H "Authorization: Bearer $GALACTICA_AGENT_TOKEN" http://127.0.0.1:8001/api/v1/articles/
```

### Relevant files

`core/agents.py`, `core/research.py`, `core/agent_auth.py`, `core/api.py`, `core/reviewing.py` (`run_agent_cycle`),
`core/editorial.py` (attribution + allowed evidence), `core/prompts.py`, `core/configs.py`, `core/models.py`,
`templates/core/{proposal,job_detail,workshop,article}.html`, `core/tests/test_agents_and_research.py`.

### Next actions

1. Inspect the pending live proposal in the UI; decide manually (approve/reject/request revision). Do not auto-publish.
2. Re-run `check_runner` after quota windows; consider whether `beam-free` remains available/labeled.
3. If the cycle is repeated, add a second independent source and compare reviewer verdicts; current cycle has one source.
4. Measure false-approval rate against human audits before considering any low-risk promotion. No such measurement exists.
5. Add tests for fetch byte-limit/content-type responses if intake grows.

### Unresolved questions (not decisions)

- Should `propose` API candidates be diffs rather than whole-article markdown?
- Should reviewer panels see the base revision for improvements to existing articles? Current cycle creates new articles.
- Is `opencode-go/beam-free` acceptable as a sustained default, given it is external and free-tier terms can change?
- Should source snapshots be retained indefinitely or pruned? No retention policy yet.

### Proposals (not accepted)

- Add a low-risk shadow-mode evaluation harness with random human audits.
- Add multiple-source research with deduplication by content hash.
- Add an explicit `publish_low_risk` service only after measured false-approval data exists.

## Accepted decisions (implemented)

- **Stack:** Django 6.1 on Python 3.14, SQLite (WAL, `transaction_mode=IMMEDIATE`), Django templates, vanilla JS, no
  frontend framework. Dependencies: `Django`, `Markdown`, `nh3`.
- **Content model:** `Article` + immutable `Revision` + ordered typed `Block`s with stable `block_id` across revisions.
  Block kinds implemented: `markdown`, `image`, `table`, `timeline`. Whole-article revision is the publish/rollback unit.
- **Drafting:** one open draft per article; optimistic version check on save. Published revisions are never edited
  through services, admin or the editor.
- **Proposals:** created from a draft or candidate against the current published revision. Rationale required (20–2000
  chars). No-op proposals refused. Exact repeats of a rejected candidate are flagged `repeat_of`.
- **Reviews:** one review per role per proposal. Each reviewer receives only base, candidate, rationale and sources;
  verdicts are never passed to another reviewer. Panel outcome (`supported`/`contested`/`objected`/`incomplete`) is a
  summary, not a decision.
- **Decision/publication:** staff only. Approval enforces the active policy (minimum reviews, objection block).
  Publishing is a separate step, locks the article, rechecks the base and refuses stale proposals with an audit event.
  Evaluation proposals can never be approved or published.
- **Revert:** staff only, requires a reason and the expected current revision; creates a NEW published revision with
  `reverts` pointer. History is never erased. Stale revert attempts are refused.
- **Audit:** `AuditEvent` records actor, action, time, reason, revision/proposal/job and detail for every significant step.
- **Configuration:** versioned `ConfigVersion` for `instructions`, `reviewers`, `runner`, `policy`, `limits`. Editing
  creates a new version; duplicating creates a new family; one default per kind. Every job stores a resolved snapshot.
  Seeded presets are marked provisional.
- **Jobs:** DB-backed queue (`Job`, `JobEvent`) with `queued → running → succeeded|failed|cancelled|interrupted`.
  Separate `run_worker` command. Short write transactions; exclusive claim. Heartbeats and explicit stale recovery;
  no automatic retry. Cancel and retry are explicit. Model-call budget and job time limit enforced.
- **Runners:** `simulated` (offline, deterministic, labelled SIMULATED, no model calls) and `opencode` (CLI JSON
  stream). Adapter boundary in `core/runners/`. No automatic paid fallback.
- **OpenCode isolation:** sandbox dir with project `opencode.json` denying all permissions; fresh `--standalone`
  session per call; prompt attached as a file; subprocess in its own process group; timeout/cancel kills the group.
  Usage recorded only from OpenCode step events; cost never invented.
- **Safety:** `nh3` sanitisation; fixed tag/attribute allowlist; raw HTML/scripts/`javascript:` removed; image src must be
  `/static/` or `https://`; registered block types only; no arbitrary agent JavaScript.
- **Auth:** Django sessions. Staff = publish/decide/revert/config/job control. Any authenticated user can draft and
  propose. Reading is anonymous. Localhost-only `ALLOWED_HOSTS`.
- **Seed:** `seed_demo` is idempotent (one transaction for the build; get-or-create for sources/presets/cases). Three
  demonstration articles, sources with honest check status, six test cases, and jobs in every state.

## Verified in this pass

- `manage.py migrate` on a clean DB: OK.
- `manage.py seed_demo` twice: second run adds nothing; counts unchanged.
- `manage.py run_worker --once` processed the seeded queued eval job; afterwards 0 queued/running.
- `manage.py test core`: **77 tests pass** (editorial, permissions, stale publication/revert, job transitions,
  cancellation, interruption recovery, budget, watchdog, runner parsing/redaction, sanitisation, preview parity,
  config versioning, seed idempotency, seed content length).
- Staff pages return 200; anonymous editorial pages redirect to login; editor account gets 403 on staff actions.
- Static assets (CSS, JS, diagram) return 200. No server traceback in the log.
- Seed state: 3 demo articles + 1 research-draft article; published r1 for all demos; AlterEgo correction published;
  quadratic change published then reverted (r4 current, r1 restored as new revision); rejected unsupported proposal;
  pending stale proposal with contrasting verdicts; 6 test cases; 7 eval candidate results; jobs succeeded/failed/
  cancelled/interrupted plus the queued example (now run by the worker).
- Sources checked: Subvocal recognition and Encyclopedia Galactica and Quadratic voting Wikipedia pages opened
  2026-10-28; arXiv abstract read; AlterEgo (Kapur, Kapur & Maes, IUI 2018, pp. 43–53), Denby et al. 2010 and Pei et al.
  2011 DOIs resolved. Metadata-only sources are recorded as such.

## Running processes (this session)

- Web: `.venv/bin/python manage.py runserver 127.0.0.1:8001 --noreload` → **http://127.0.0.1:8001/**
- Worker: `.venv/bin/python manage.py run_worker` (background; log `/tmp/opencode/galactica-worker.log`)
- Logs: `/tmp/opencode/galactica-server.log`, `/tmp/opencode/galactica-worker.log`

## Exact commands

```sh
cd /home/justin/projects/galactica-workshop
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py runserver 127.0.0.1:8001
.venv/bin/python manage.py run_worker          # second terminal
.venv/bin/python manage.py test core
```

Logins: `admin` / `admin` (staff), `editor` / `editor` (non-staff). Local demo only.

## Failures and blockers

- **Live OpenCode run not completed:** free-model quota returned `provider.free-limit` (HTTP 429) during this session.
  The runner is implemented and tested against recorded event streams; a real run is unverified. No paid fallback used.
- Early failures fixed during the pass: stale `article` instance in `ensure_draft`/`open_proposal` (draft started from
  placeholder instead of published revision); evaluation candidate collided with the one-draft constraint; cancellation
  not checked before a handler started; default call budget too small for a full six-case panel; preview title was not
  escaped.
- No browser automation was available. Rendered HTML was inspected through the Django test client and `curl`; visual
  layout has not been checked in a real browser.

## Next actions

1. Open http://127.0.0.1:8001/ and walk the cycle in `README.md` ("What to click").
2. When free quota returns: `manage.py check_runner`, then run the `OpenCode, free model` runner from the Workshop and
   verify measured usage appears on the job page.
3. Decide whether the next increment is the agent JSON API (read articles/revisions, submit proposals, record reviews,
   check statuses, scoped credentials) — specified but not implemented.
4. Add human labels to test cases via admin once enough runs exist; the current expectations are simulated or unknown.

## Relevant files

- `core/models.py` — data model
- `core/editorial.py` — draft/proposal/publish/revert services and rules
- `core/jobs.py` — queue, claim, cancel, retry, recovery, execution
- `core/reviewing.py` — draft/propose/review/eval handlers
- `core/runners/` — runner boundary, SIMULATED runner, OpenCode adapter
- `core/configs.py` — presets, schemas/forms, model discovery, panel resolution
- `core/blocks.py`, `core/markup.py` — validation and the single renderer/sanitiser
- `core/prompts.py`, `core/scenarios.py`, `core/demo_content.py`, `core/seeding.py`
- `core/views.py`, `core/urls.py`, `core/admin.py`
- `templates/`, `static/css/galactica.css`, `static/js/editor.js`, `static/js/workshop.js`
- `core/tests/` — 77 automated checks
- `README.md` — setup, URLs, click path, gaps

## Unresolved questions (not decisions)

- Should agent-originated proposals share the human proposal queue, or have a separate agent inbox?
- Should automatic publication be implemented as an experimental policy (currently absent by design)?
- How much per-user visibility is needed for non-staff editors (currently they can see all proposals/jobs)?
- Should eval cases support human labels from a dedicated UI rather than Django admin?

## Proposals (not accepted)

- Add the JSON API with scoped agent credentials next.
- Add a small browser smoke check (Playwright) once available.
- Add uploaded media instead of path/URL images if the workshop is used beyond local demos.
