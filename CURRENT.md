# CURRENT — Galactica Workshop

**Updated:** 2026-10-28 (latest pass: claim-level citation enforcement)
**Location:** `/home/justin/projects/galactica-workshop` (separate Django app; the TypeScript project at
`/home/justin/projects/galactica` is untouched)

## Objective

Build the first usable local Galactica workshop: editable, versioned articles; proposals with evidence and independent
reviews; human publication, correction and revert; configurable runner/reviewer/policy versions; background jobs; and
repeatable editorial test cases. Django + SQLite, localhost only, no Docker/Redis/SPA.

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
