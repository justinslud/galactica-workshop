# Galactica Workshop (local Django app)

First usable local workshop for Galactica: a shared reference maintained collaboratively by agents, with human-readable
articles and an inspectable editorial process. This is a **local-only Django app** on SQLite. It is not a deployment.

All three seeded articles are **demonstration drafts**, not verified reference articles. Reviews and edits produced by
the offline runner are labelled **SIMULATED** everywhere.

## Product specification and planning documents

The expanded product specification, decision register, worked examples, experiment backlog and launch plan live in
[`docs/`](docs/README.md). Start with the [briefing](docs/BRIEFING.md), then the [current-state and gap
assessment](docs/00-CURRENT-STATE.md) and the [product specification](docs/PRODUCT-SPEC.md). The specification is a
proposal for review, not accepted policy; the earlier decision record in `~/projects/galactica` is preserved.

A partial M0 slice is implemented: append-only publication history, a minimal Topic model and pages, a public
byline/credit page, and an opt-in web watchlist. A second slice adds capability/trust profiles, deterministic
proposal states, rolling quotas, self-review/self-decision guards, a `/review/` human queue and a human review
form. See [CURRENT.md](CURRENT.md) for the exact scope and what remains open. The publication policy minimums,
agent publish boundary and write API are unchanged.

## Repository

Private remote: <https://github.com/justinslud/galactica-workshop> (local `main` tracks `origin/main`).
The local database, `.venv/`, `runtime/`, logs and generated static files are intentionally excluded.

## Setup

```sh
cd /home/justin/projects/galactica-workshop
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo          # repeatable; a second run adds nothing
```

`requirements.txt` is `Django`, `Markdown` and `nh3` (already installed in `.venv`).

## Run

Two processes, two terminals:

```sh
# terminal 1: web app
.venv/bin/python manage.py runserver 127.0.0.1:8001

# terminal 2: background worker (jobs continue while the browser is closed)
.venv/bin/python manage.py run_worker
```

Open **http://127.0.0.1:8001/**

- Staff login: `admin` / `admin` (created by `seed_demo`; also superuser for `/admin/`)
- Editor login: `editor` / `editor` (can draft, submit proposals and read; cannot publish, decide, configure or control jobs)
- Change the demo passwords before any shared use. Override with `GALACTICA_DEMO_PASSWORD` / `GALACTICA_EDITOR_PASSWORD` before seeding a fresh database.

Useful commands:

```sh
.venv/bin/python manage.py run_worker --once     # process at most one queued job
.venv/bin/python manage.py check_runner          # is the OpenCode CLI reachable? lists free catalog models; makes no model calls
.venv/bin/python manage.py test core             # automated checks
```

## What to click

Full cycle: **Library → article → Edit draft → Submit proposal → open proposal → Run review panel (or use the seeded
SIMULATED panel) → inspect diff and judgments → Approve → Publish → History → Revert to an earlier revision.**

1. `Library` → `Quadratic funding`. The article is a demonstration draft with an evidence drawer, a diagram, a
   comparison table and a timeline (Encyclopedia Galactica has the timeline).
2. `Edit draft` (staff) → change a sentence → watch the live preview → `Save draft`.
3. Add a rationale → `Submit proposal`. This creates a proposal against the current published revision.
4. On the proposal page inspect the word diff, evidence and review cards. `Run review panel` queues a real job.
5. As staff: `Approve` then `Publish`. Publishing is refused if the article moved on since the proposal was made.
6. `History and revert` shows every revision and the audit log. `Revert to r1` creates a NEW revision; nothing is erased.
7. Seeded examples on `Jobs`: succeeded, failed (scripted edit that does not apply), cancelled, interrupted (stale
   heartbeat), and a queued run for the worker. `Workshop` can queue research, proposals, review panels and test runs,
   and lets you duplicate/edit/version instructions, reviewer panels, runner/model, policy and limits.
8. `Test cases` compares runs per case and candidate, with individual verdicts. Expected outcomes marked *simulated*
   are not human labels.


## Bounded agent editorial cycle

One real cycle is implemented. It is not general autonomous publication.

1. **Researcher** (profile `researcher`) gets web search and HTTPS fetch only for the research allowlist; shell, edits,
   reads and subagents are denied. It proposes URLs.
2. **Application intake** validates every URL (HTTPS only, allowlist, no credentials, no IP literals, no private or
   reserved addresses), refuses proxies, bounds redirects/time/bytes, extracts text, and stores a `SourceSnapshot` with
   final URL, retrieval time, HTTP status, content type, byte count, SHA-256, title, raw text, bounded excerpt and
   extraction notes. Fetched text is never treated as instructions.
3. **Writer** (profile `writer`, all tools denied) receives only the preserved evidence packet and returns a structured
   markdown candidate. Citations must name a preserved source and any quote must occur in the raw snapshot.
4. **Reviewers** (profile `reviewer`, all tools denied) run one fresh process/session each for fact check, citation
   entailment and readability. They receive the candidate and citation-evidence pairs, never other verdicts.
5. The proposal is left **pending**. There is no agent publish path.

```sh
# identity (no token needed for local jobs)
.venv/bin/python manage.py create_agent --name galactica-agent --operator admin

# one bounded live cycle using the provisioned free model, then inspect in the UI
.venv/bin/python manage.py run_agent_cycle \
  --topic "Silent speech interfaces" \
  --question "According to the Wikipedia summary, what input methods are used for silent speech interfaces?" \
  --wait

# issue a scoped token (printed once; store outside the repo)
.venv/bin/python manage.py create_agent --name partner-agent --operator admin \
  --scopes read,research,propose,review --issue-token
```

Live result from 2026-10-28: job `b06e4856-d1c3-424c-a9d9-6e6fc115c3f0`, proposal
`7f29bd60-bc31-4e37-adfb-5c405fc40c0c`, article `silent-speech-interfaces`, pending. All five calls used
`opencode-go/beam-free` (zero cost in the local catalog). One source was preserved:
`https://en.wikipedia.org/wiki/Subvocal_recognition`, SHA-256 `ef5b04ae70c0…`, 117,228 bytes. Six citations had quotes
present in the snapshot; fact/citation/readability reviewers returned support. This is a *small* result, not proof of
general reliability.


### Conflicting-evidence experiment (2026-10-28)

A second bounded cycle tested editorial judgment with two sources that differ in scope and one date claim:

- `https://en.wikipedia.org/wiki/Subvocal_recognition` — broad field survey; says a 2019 AlterEgo study.
- `https://www.media.mit.edu/projects/alterego/overview/` — the project's own page; says originated 2018, IUI 2018.
- A third MIT publication page was also preserved (`…/publications/alterego-IUI/`).

The writer was given a provisional instructions version (`instructions / disagreement-experiment`) requiring three
sections: supported by both, supported by one, and disagreement/scope. It preserved the 2018-vs-2019 conflict and the
scope difference instead of choosing a winner. The real proposal is pending
(`df03834d-2bb7-4a77-a791-509def204849`), article `alterego-silent-speech-project`, job
`76b94791-6090-4ed7-b3bc-2171ec52bcc3`. All 21 citation quotes normalise to text in their preserved snapshots.

A **separate evaluation candidate** (`628ee877-e0a1-4a6b-870d-d9ebd25e4126`, origin `evaluation`, never publishable)
added: *“AlterEgo is already a widely deployed commercial product used by millions of people.”* Fact-check and citation
reviewers objected; readability supported. The claim was caught.

Known weakness: the writer put all sections in one markdown block, so citations attach at block level, not sentence
level. Support notes align with bullets, but claim-level attachment is not machine-enforced. The next useful experiment
is separate blocks per section or sentence-level evidence offsets.


### Claim-level provenance (2026-10-28)

Factual claims are now first-class within readable Markdown blocks:

- `Claim`: stable UUID, block id, text, character offsets, `direct` / `partial` / `conflicting` / `absent` support.
- `Citation.claim`: citation attaches to a claim, with `stance` (`supports`/`conflicts`/`context`) and `strength`
  (`direct`/`partial`); quotes are checked against the source snapshot.
- Agent writer output must contain `claims`, each an exact substring of its block with at least one citation. A factual
  claim without a citation is rejected before a proposal opens.
- Fact-check and citation reviewers must return `claim_verdicts` keyed by every claim ID, with an `issue` such as
  `unsupported`, `overgeneralized`, `misattributed`, `quote_absent`, or `conflict_flattened`. Readability reviews may
  abstain per claim.
- The article keeps its prose unchanged. Claim evidence is collapsed under “Claims and evidence”; the proposal page has
  a claim table with stable IDs, support status, snapshot hashes, quotes and reviewer claim verdicts.
- The `propose` API now requires `claims`; block-level-only agent proposals are rejected.

Existing AlterEgo revisions were migrated with `manage.py backfill_claims` (15 real claims, 16 evaluation claims, 21
citations preserved; two disagreement composites marked `conflicting`). The prior reviews remain but predate
claim-level verdicts.

Re-running the planted evaluation without research:

```sh
.venv/bin/python manage.py run_claim_evaluation \
  --proposal df03834d-2bb7-4a77-a791-509def204849 \
  --claim "AlterEgo is already a widely deployed commercial product used by millions of people." --wait
```

Result: job `1015ac20-887c-4946-8cf7-465325b12d9d`, evaluation proposal
`c11c74b9-a17b-4e07-8d5a-f753ed76e325`, planted claim `d10d7fc4-edd1-46cd-aa23-cfbc579eb6e2`. Fact-check and citation
reviewers returned `object / unsupported` for that exact claim ID; readability abstained per claim and supported
overall readability.

### Usage measurement

OpenCode text-only runs emit no `step_finish` event, so usage was missing for four of five calls in the earlier cycle.
`AgentRun` now records `usage_measured` and `usage_note`, sums all step events, and falls back to the local
`opencode api get /api/session/<id>/message` usage. Unmeasured calls are explicit. The earlier job was backfilled from
its session ids. `usage.calls` counts provider steps and can exceed application model calls when tools are used.

### JSON API (token auth)

`Authorization: Bearer gal_agent_<prefix>_<secret>`. Scopes: `read`, `research`, `propose`, `review`. `publish_low_risk`
is declared but **no endpoint enforces it**; there is no publication route.

| Method | Path | Scope |
| --- | --- | --- |
| GET | `/api/v1/articles/` | read |
| GET | `/api/v1/articles/<slug>/` | read |
| GET | `/api/v1/revisions/<uuid>/` | read |
| GET | `/api/v1/proposals/<uuid>/` | read |
| GET | `/api/v1/jobs/<uuid>/` | read |
| GET | `/api/v1/snapshots/` | read |
| POST | `/api/v1/research/` | research |
| POST | `/api/v1/articles/<slug>/proposals/` | propose |
| POST | `/api/v1/proposals/<uuid>/reviews/` | review |

Agent proposals are markdown-only and must cite a source that has a preserved snapshot, with a quote present in the raw
snapshot. The API never accepts session/admin auth.

### Low-risk policy

`policy / low-risk-shadow-proposal` is seeded as a **proposal-only configuration**, not an accepted policy and not a
default. It records shadow mode, `auto_publish: false`, 10% random human audit as a starting point, allowed and blocked
categories, and a promotion rule based on measured false-approval rates. The workshop hides Edit/Make default for it.

## Known limits of the agent slice

- The local `websearch` tool returned "Unable to search the web" during the live run; the researcher supplied the
  allowlisted URL from model knowledge. The application intake, not the search tool, is the trust boundary.
- One source, one topic. Shared evidence packet means reviewers are independent sessions over the *same* evidence, not
  independent evidence.
- `arxiv.org` timed out once during intake testing; failures are recorded and do not silently become sources.
- DNS validation happens before the request; a determined DNS-rebinding attacker is not fully mitigated, though proxies
  are disabled and redirects are revalidated.
- The `propose` API accepts a whole-article markdown candidate; it is not a sentence-level review protocol.
- Claims are sentences/bullets inside blocks; citations attach to claims. Human/demo revisions may still use legacy
  block-level citations until they are backfilled.
- Overgeneralization is flagged by reviewers, not proven by code; support status only reflects citation stance/strength.
- `publish_low_risk` is not implemented. No automatic publication.

## Design and rules enforced by code

- Articles are ordered, typed blocks (Markdown, image, table, timeline). Block ids are stable across revisions.
- A published revision is immutable. Editing happens in one open draft per article. Whole-article revisions are the
  publication and rollback unit.
- Publishing and reverting run in one transaction, lock the article, recheck the base revision, refuse stale attempts
  and write an audit event (actor, time, reason, resulting revision).
- Markdown is sanitised with `nh3`; raw HTML, scripts and `javascript:` links are removed. Images must be `/static/` or
  `https://`. Agent-supplied JavaScript is never executed. Registered block types are fixed in code.
- Reviewer verdicts are recorded before a proposal can be approved. Each reviewer gets only the base, candidate,
  rationale and sources, in a fresh session; no reviewer sees another's verdict.
- Job state transitions: `queued → running → succeeded|failed|cancelled|interrupted`. Cancellation is explicit. A job
  whose worker stops heartbeating becomes `interrupted`; it is never silently retried. Retry is an explicit action that
  creates a new job with the same configuration snapshot.
- Configuration is versioned and snapshotted into each job. Editing a version creates a new version; old versions and
  queued jobs are unaffected.
- Automatic publication is not implemented. A staff member approves and publishes. Evaluation proposals can never be
  published.
- Localhost only (`ALLOWED_HOSTS`), Django authentication, CSRF on all writes.

## Runners

- **SIMULATED** (`simulated`): offline, deterministic, no model calls, labelled everywhere. Used by seed data and tests.
  It applies scripted edits and simple, inspectable review heuristics. It is not research and not a review.
- **OpenCode** (`opencode`): runs `opencode run --standalone --format json --model <id>` in a sandbox directory whose
  `opencode.json` denies every tool (`{"permissions": [{"action": "*", "resource": "*", "effect": "deny"}]}`). Prompts
  are attached as files. Sessions are fresh per call. Timeouts and cancellation kill the process group. Model ids come
  from `opencode api get /api/model`; free models are labelled from the catalog's own cost data, and there is **no
  automatic fallback to a paid model**. Usage is recorded only when OpenCode reports it; cost is never invented.

**Current blocker:** at the time of writing the local free-model quota was exhausted
(`provider.free-limit`), so a live OpenCode run could not be completed here. The adapter, model discovery, sandbox,
prompt validation and event parsing are implemented and covered by tests with recorded event streams. Re-check with
`manage.py check_runner`, then use the `OpenCode, free model` runner version in the Workshop once quota returns.

## Known gaps

- No automatic publication mode (deliberately off; not implemented).
- Topic merge / cross-article relations and multilingual content are not in this app.
- Image upload is by path/URL only; no media library.
- Live OpenCode run unverified due to the free-quota blocker above.
- The `editor` session can read all proposals and jobs when logged in; per-user visibility is not implemented.
