# Technical and operational implications, and launch/participation evidence

**Status:** research note for the 2026-11-04 product-specification pass. Not a spec.
**Scope:** what the workshop implies, what demonstrated systems do, and what a public launch would require.
Grounded in this repository (`core/models.py`, `core/editorial.py`, `core/api.py`, `core/jobs.py`,
`core/policy_lab.py`) and the sources below. **All sources accessed 2026-11-04.**

**Labels:** **[demonstrated]** I opened the spec, schema, manual, legal code or paper and verified the claim.
**[claimed]** an operator, vendor or preprint asserts it; untested here. **[historical/abandoned]** a project
that ran and declined. **[proposed adaptation]** my inference for Galactica/T5. **[open]** unverified.

**Method:** `web_search` unavailable as stated. Discovery used DuckDuckGo's HTML endpoint, which worked once and
then returned a bot challenge; remaining pages were fetched from canonical URLs. Every page in the table was
fetched and read, not summarised from a snippet. The two arXiv IDs were checked through the arXiv API.

---

## Top findings

1. **Immutable revisions are necessary but not sufficient.** Systems that answer "what did we believe on
   date X" keep immutable content *and* separate append-only publication events. The workshop has the first,
   plus a generic `AuditEvent` stream — but `publish()` mutates the previous revision's `state` to
   `superseded`, so state *as of* a date survives only as an audit side effect, and article deletion cascades
   those rows away. A publication-event table is the durable form. [demonstrated / proposed adaptation]

2. **A permalink is not a reproduction.** MediaWiki guarantees only a revision's *main text*; templates and
   images render live. Any derived view — snippet, PDF, API payload, static export — needs its own manifest.
   [demonstrated]

3. **Split content identity from record identity.** Git names objects by content hash; MediaWiki keeps
   `rev_id` for identity and `rev_sha1` for content, because review state and deletion change independently
   of text. Hash-only identity makes provenance unaddressable. [demonstrated]

4. **Structured records need an epistemic axis and a temporal axis, separately.** Wikidata ranks encode
   *current* confidence; correct historical values belong in start/end-time qualifiers, not the deprecated
   rank. [demonstrated]

5. **The mature API pattern is conditional writes plus explicit idempotency.** `If-Match` with a strong ETag
   prevents lost updates; an idempotency key plus payload fingerprint makes retries safe, with `409` for
   in-flight duplicates and `422` for key reuse with a different body. The workshop's write endpoints — the
   ones agents retry — have neither. [demonstrated spec / proposed adaptation]

6. **Optimistic concurrency with a manual 3-way merge works at small scale.** MediaWiki detects via base
   revision, refuses the save, shows both versions, makes the human merge. It can lose your own edits from a
   stale conflict page, but never silently overwrites. CRDTs buy convergence, not editorial judgement.
   [demonstrated]

7. **"Exactly once" is unavailable; aim for at most one visible effect per intent.** Unique constraints,
   compare-and-set on the publish pointer, and attempt fencing are what hold. A heartbeat-expiry race can
   hand one job to two workers, and the second publish is what readers see. [proposed adaptation]

8. **Backups fail as processes, not technologies.** GitLab's 2017 postmortem: five recovery mechanisms, all
   five failed at once — version-mismatched `pg_dump` writing nothing, cron alerts rejected by DMARC,
   snapshots never enabled for the database, staging snapshots used as disaster recovery, replication already
   broken. The fix is a restore drill. [demonstrated, first-hand]

9. **Licensing cannot be retrofitted.** CC BY-SA 4.0 requires creator identification, copyright and license
   notices, a URI, and indication of modification; §4 extends share-alike to a *database* built from a
   substantial portion of the contents. ODbL separates a "Produced Work" (notice only) from a "Derivative
   Database" (must stay ODbL). [demonstrated]

10. **Review capacity, not content supply, is the constraint.** Nupedia approved 24 articles in three years;
    Wikipedia produced 18,000 in its first year once friction dropped. Citizendium fell below 100 active
    members; Knol found no audience and deleted its content; Grokipedia launched 800,000 articles then sat
    effectively frozen for five months. [historical]

11. **The two arXiv IDs in the old notes are real.** `2605.25480` (LLM-Wiki) and `2607.26604` (WikiLoop)
    resolve, published 2026-05-25 and 2026-07-29, both about agent-native wikis. Their benchmark numbers are
    preprint claims. [claimed]

---

## 1. Versioning and provenance

**Findings.** MediaWiki separates four things the workshop mixes: the revision row (identity, parent,
timestamp, actor), the text (shareable after a rollback), deletion (rows move to an `archive` table), and the
page pointer (`page_latest`). Revisions are "retained permanently, unless the page is deleted"; `rev_id` is
"almost always" but not strictly monotonic, because imports can create revisions out of order and the
first-saved edit becomes the parent of the second on a conflict. Code that treats revision numbers as a total
order will eventually be wrong. [demonstrated] <https://www.mediawiki.org/wiki/Manual:Revision_table>

The workshop's split is partial: revisions are immutable and `content_hash` exists, but `publish()` sets the
previous revision's `state` to `superseded`, and the only trace of the transition is an `AuditEvent` row whose
article FK cascades on delete. "What was published on date X" is therefore a reconstruction from a generic
stream, not a record.

Git goes the other way: identity *is* content — blobs hashed, trees referencing blobs by hash, commits
referencing trees and parents — and there is nowhere to record approval. [demonstrated]
<https://git-scm.com/book/en/v2/Git-Internals-Git-Objects>

Wikidata adds the epistemic layer: `normal` "provides no judgement", `preferred` is the current best
consensus, `deprecated` marks known errors or outdated knowledge, is excluded from queries by default, and is
explicitly *not* for correct historical values. Each statement also carries its own qualifiers and references,
so evidence attaches to a value rather than to the page. [demonstrated]
<https://www.wikidata.org/wiki/Help:Ranking>

The permalink evidence is the sharpest warning: a permanent link "does not show exactly the same page"; only
the main text is guaranteed, while images and transclusions update live. MediaWiki promises text stability,
not reproduction; a reference promising "the article as of 2026-03" must do better or promise less.
[demonstrated] <https://en.wikipedia.org/wiki/Help:Permanent_link>

CRDTs fit published prose worst: convergence "in a self-stabilising manner, despite any number of failures"
means replicas agree, not that the agreement is correct or reviewed. [demonstrated]
<https://inria.hal.science/hal-00932836>

**Borrow.** Three tiers: content (hash-addressed, immutable), record (revision ID, parent, actor, status,
review links), pointer (published revision, open draft). The workshop has the second and
`Revision.content_hash`; expose the hash as the content address and ETag. Keep deleted revisions archived,
with a separate "suppressed" state for legal/privacy cases. Store ranks as a closed set plus valid-time
fields, so "outdated" and "was true then" stay distinct.

**Do not borrow.** Hash-only identity for reviewed content; rank-as-truth for prose (ranks are per-statement;
prose claims rarely have one preferred value); CRDT merge for published text.

**Implications for the spec.** Name four objects and their mutability: content blob, revision, publication
event, view manifest. Promote the audit `published` rows into a first-class publication-event table (PROTECT,
not CASCADE). Answer in one sentence each: what was published on date X (publication events), what was asserted
on date X (revision/claim timestamps), which revision a view uses (manifest). Confident on the split; less sure
claim-level versioning is needed at launch rather than at the first structured-record feature.

**Open.** Bitemporality at claim level in v1, or later? Is a translation a revision sibling or a child of its
source revision (adapted material needs the source revision ID)?

---

## 2. API access for agents and downstream reference users

**Findings.** RFC 9110: ETags are opaque; `If-Match` uses strong comparison and is "most often used with
state-changing methods ... to prevent the 'lost update' problem"; a failed precondition is `412`; `409` is for
a conflict "the user might be able to resolve and resubmit", with a body that "SHOULD" carry enough to
recognise the source — for a wiki, the current revision ID and hash. [demonstrated]
<https://www.rfc-editor.org/rfc/rfc9110.html>

The IETF `Idempotency-Key` draft (version 08, Internet-Draft, expires 2027-04-25) defines the shape: unique per
operation, never reused with a different payload; a fingerprint detects that; a completed duplicate returns
the original result; an in-flight duplicate returns `409`; reuse with a different payload returns `422`; a
missing required key returns `400` with `problem+json`; and resources "MUST publish an idempotency-related
specification" with an expiry policy. [demonstrated as a draft]
<https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/>

Stripe shows the trade-offs: V4 UUIDs recommended, response (including 500s in API v1) saved once execution
begins, keys pruned after 24 hours, parameters compared against the original. The trap in "cache the 500": a
transient failure is replayed for that key until pruning, so retrying *transport* reuses the key and retrying
*work* needs a fresh one. [claimed — vendor docs] <https://docs.stripe.com/api/idempotent_requests>

GitHub covers client behaviour reference users will exercise: obey `retry-after`, else wait at least a minute
then back off exponentially and give up; hammering a limit "may result in the banning of your integration";
serial, not concurrent requests; `304` responses do not count against the primary limit; follow the `Link`
header rather than constructing pagination URLs. Conditional requests on unsafe methods are generally
unsupported — hence `If-Match`, not `If-None-Match`, on writes. [claimed — vendor docs]
<https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api>

MediaWiki's edit API has carried `baserevid`/`basetimestamp` since 1.35 to detect conflicts, and documents the
self-conflict exception: `baserevid` fails on a self-conflict unless `basetimestamp` is set. [demonstrated]
<https://www.mediawiki.org/wiki/API:Edit>

**Borrow.** `ETag: "<content_hash>"` on revisions and articles; `If-Match` on writes to an existing revision or
proposal; `412` with the current hash. Idempotency keys on create-proposal, record-review, start-job, stored as
`(key, endpoint, fingerprint, status, body, created_at)`, pruned at 24–72 h. Opaque cursor pagination on
`(updated_at, id)`. One `application/problem+json` envelope with stable codes (`stale_base`, `duplicate_key`,
`rate_limited`, `quota_exhausted`). `429` with `Retry-After` [demonstrated: RFC 6585 §4]
<https://www.rfc-editor.org/rfc/rfc6585.html>, per token and per agent. MediaWiki's etiquette page adds the
low-tech norms that keep agent fleets from becoming incidents: serial requests, batching, `maxlag` for
non-interactive jobs, and a mandatory User-Agent. [demonstrated]
<https://www.mediawiki.org/wiki/API:Etiquette>

**Do not borrow.** Stripe's "cache the 500" for agent writes. Concurrency as the default client mode — an agent
fanning out 50 parallel writes is a self-inflicted incident. Batches returning 200 with per-item errors.

**Implications for the spec.** One table: endpoint, required headers, idempotent or not, precondition, error
codes, promised retry policy. Plus a deprecation policy, because reference users cache responses. Today
`core/api.py` has token auth and a `409` for a missing runner, but no ETag, idempotency, rate limit or problem
envelope — the largest gap between the workshop and something an outside agent can safely call in a loop.

**Open.** Does a review need an idempotency key, or is "one review per role per proposal" the natural
constraint? Are reads unmetered for reference use while writes are quota'd?

---

## 3. Concurrent edits, retries, recovery

**Findings.** At small scale the working mechanisms are boring: one writer, a transaction, a row lock, a unique
constraint, a compare-and-set. The workshop already does this in `publish()` — `select_for_update()` plus a
stale-base refusal. SQLite WAL supports the shape (readers don't block the writer, the writer doesn't block
readers) but "there can only be one writer at a time", `SQLITE_BUSY` still surfaces in edge cases (exclusive
connections, WAL cleanup on last close, post-crash recovery), and WAL does not work on a network filesystem.
[demonstrated] <https://sqlite.org/wal.html>

Concrete failure modes:

- **Retry after commit, before response.** The agent times out and creates a second proposal. A unique
  constraint on `(article, candidate_hash, base)` catches exact duplicates, not a regenerated candidate
  differing by one word. An idempotency key catches both.
- **Long write transactions.** A model call inside `transaction.atomic()` holds the single writer lock and
  every other agent gets `SQLITE_BUSY`. Never call out inside a transaction.
- **Heartbeat expiry during a pause.** A frozen VM or long GC pause lets stale-recovery re-claim the job; two
  workers act on one proposal. Without attempt fencing the second publish is visible — the workshop's most
  plausible double-publish path.
- **Merging structured content.** Merging claim *offsets* as numbers produces claims pointing at the wrong
  span, so citations appear to support the wrong sentence. Recompute offsets from merged text.
- **Self-conflict.** A slow save plus another edit by the same user conflicts with itself; saving from the
  stale conflict page can lose earlier edits. [demonstrated]
  <https://www.mediawiki.org/wiki/Help:Edit_conflict>

Exactly-once does not exist across an HTTP client, a queue and a database. The achievable property is at most
one visible effect per intent: key on ingest, unique constraint on the effect, fence on the worker, and a
visible "duplicate suppressed" record so operators see it rather than infer it.

**Borrow.** The idempotency table above. An `attempt` counter incremented on claim, with side effects guarded
by `WHERE job.attempt = :attempt`. Publish as `UPDATE article SET published_id = :new WHERE published_id =
:expected` plus a `PublicationEvent` row in the same transaction. Reviews append-only, so a replayed decision
is a new row citing the old one. A rebase path returning the current revision and the diff from the client's
base.

**Do not borrow.** Distributed locks as the primary mechanism (one writer, one database). Last-write-wins on
timestamps (clock skew makes it quietly wrong). Server-side automatic retry of writes.

**Implications for the spec.** Define the conflict taxonomy once: `stale_base` (412), `duplicate_in_flight`
(409), `duplicate_completed` (200, original body), `payload_mismatch` (422), `rate_limited` (429),
`quota_exhausted` (403 or 429 — pick one). State that review and publication are append-only and job side
effects attempt-guarded. State the SQLite envelope (single host, WAL, `busy_timeout`, no network filesystem) so
horizontal scaling is a decision, not a surprise.

**Open.** At what write rate does SQLite stop being defensible? Measure p99 write wait under realistic job load
before claiming headroom. Do agents need a draft lease, and does that not reintroduce fencing?

---

## 4. Reproducible experiments and replayable review decisions

**Findings.** NeurIPS makes its checklist mandatory, reviewer-visible, and published with the paper; "no" is
acceptable *with justification*, and omitting it is a desk reject. Mandatory, low-friction,
justification-friendly is the design that survives contact with authors. [demonstrated]
<https://neurips.cc/public/guides/PaperChecklist>

The policy lab already has the right shape: pure simulation, planted defects, seeded trials, JSON report plus a
timestamped copy. The gap is that review decisions are not replayable in the same sense. Two claims must not be
conflated: **deterministic replay** (stored verdicts + stored policy version → recomputable panel outcome,
achievable today, should be a test) and **re-execution** (re-running the model and getting the same verdict — a
probability, not a guarantee; store temperature, seed, model ID, prompt hash and label it a new sample).

ACM's artifact-badging policy could not be checked (bot-verification page); the NeurIPS checklist covers the
same ground here.

**Borrow.** A run record per evaluation: seed, scenario-set hash, policy version, panel config, model IDs,
prompt hashes, code commit, timings, full per-trial output. The lab report is close; add commit and config
hashes. One seeded RNG threaded through everything. Store raw model output, not just parsed fields — parsing
bugs are the usual reason old results cannot be re-derived. A review-decision replay test over N stored
proposals. A short mandatory human checklist (claim support, quote present, source independence, conflict of
interest) with "justify any no".

**Do not borrow.** Full environment capture at launch — right long term, wrong first answer; a commit hash, a
requirements lock and stored output catch most drift. And do not call model re-runs "reproduction".

**Implications for the spec.** Define what a review run is, what is stored with it, and which replay guarantee
applies. Require that every published claim's evidence chain (source → snapshot hash → quote offsets → claim →
revision) is reconstructible from the database alone, which the workshop largely satisfies.

**Open.** Is the unit of reproducibility the proposal, the panel or the evaluation case? How long do raw model
outputs need retaining if they contain quoted copyrighted text?

---

## 5. Search, retrieval, exports, licensing

**Findings.** FTS5 is a credible launch choice: external-content tables index an existing table without
duplicating text, BM25 is built in, and tokenizers cover Unicode, ASCII, Porter (English) and trigram
(substring, CJK-ish). The cost is real: with `content=` the user must keep the index in sync via triggers; drift
makes query results "unintuitive and appear inconsistent"; external-content tables do not support `REPLACE`;
and `integrity-check` exists because drift happens. [demonstrated] <https://sqlite.org/fts5.html>

Wikipedia runs dedicated search and documents the expectations: the index is "updated in near real time",
changes appear within minutes, and "30 minutes is still considered normal operation". `insource:` regex scans
text and is "interrupted if it runs for more than twenty seconds" — the powerful QA queries are the expensive
ones. [demonstrated] <https://www.mediawiki.org/wiki/Help:CirrusSearch>

Exports are a product surface. Wikimedia dumps are monthly, volunteer-mirrored, and described plainly as "not
backups, not consistent, and not complete" — the model is an export contract with manifest, schema version, and
a statement of what it omits. [demonstrated] <https://meta.wikimedia.org/wiki/Data_dumps>

Three licensing obligations are easy to conflate:

- **Prose** (CC BY-SA 4.0): retain creator identification, copyright notice, license notice, warranty
  disclaimer, URI; indicate modifications; the adapter's license must use the same elements, this version or
  later, or a compatible license. §4 adds that a database containing a substantial portion of the contents is
  Adapted Material — "but not its individual contents". [demonstrated]
  <https://creativecommons.org/licenses/by-sa/4.0/legalcode.en>
- **Database rights** (ODbL): a Produced Work needs only a notice ("Contains information from DATABASE NAME,
  which is made available here under the Open Database License"); a Derivative Database must be ODbL, and
  publicly using a Produced Work derived from one triggers share-alike. [demonstrated]
  <https://opendatacommons.org/licenses/odbl/1-0/>
- **Reuse mechanics**: credit via a link to the page, a link to a stable copy, or an author list; indicate
  modifications (page history suffices in a wiki); every copy carries a license notice and URL; import only
  from compatible licenses; a contributor "can never retract or alter the license" for copies already made.
  [demonstrated] <https://en.wikipedia.org/wiki/Wikipedia:Copyrights>
- **Structured metadata** (CC0 1.0): waives copyright and related rights and expressly includes "database
  rights" and rights protecting "the extraction, dissemination, use and reuse of data" — maximal reuse, at the
  cost of the share-alike and attribution levers. [demonstrated]
  <https://creativecommons.org/publicdomain/zero/1.0/legalcode.en>

**Borrow.** FTS5 over *published* revisions with a deterministic rebuild, `integrity-check` in CI, and a
projection keyed by `(revision_id, block_id, lang)` so an external engine can replace it without changing the
API. A nightly export (JSONL of revisions, claims, citations, sources, licenses) with manifest, row counts,
per-file SHA-256 and schema version — explicitly not called a backup. License fields on revisions and sources
from day one, including API responses. Snapshots private by default, exporting metadata, hash and a short quote,
because a fetched copy of a copyrighted page is not redistributable.

**Do not borrow.** Elasticsearch at launch (cluster, schema, reindex pipeline, second ranking authority, for a
corpus that fits in one file). Wikimedia's GFDL dual licensing (legacy debt). ODbL for the whole corpus.

**Implications for the spec.** Pick one license per layer: CC BY-SA 4.0 for prose; CC0 if the aim is maximal
reuse of records, ODbL if the aim is to keep derived databases open. State export format and manifest fields;
define "attribution" in an API response (a revision URL, not a list of names); state a search-freshness
promise, because a reference returning stale results silently is worse than one returning none.

**Open.** Is a translation Adapted Material requiring attribution to the source revision (almost certainly)? Do
imported tables and images need per-block licensing, or can one article-level field carry exceptions?

---

## 6. Cost limits, backups, incident handling, moderation workload

**Findings.** *Backups.* GitLab's postmortem is the best account of how backup systems fail: five mechanisms —
nightly `pg_dump` to S3, LVM snapshots copied to staging, Azure disk snapshots, streaming replication, and the
assumed ability to restore — all failed at once. `pg_dump` 9.2 against a 9.6 database aborted, leaving the S3
bucket empty; cron failure emails were rejected because DMARC was not configured; Azure snapshots were never
enabled for database servers; LVM snapshots were staging artefacts; replication had already broken. About six
hours of writes and roughly 5,000 projects were affected; repositories survived because they lived elsewhere.
[demonstrated] <https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/>

*Incidents.* Google SRE: define triggers before an incident, write blamelessly, require review — "An unreviewed
postmortem might as well never have existed" — and keep a searchable repository. [demonstrated]
<https://sre.google/sre-book/postmortem-culture/>

*Moderation.* English Wikipedia's New Pages Patrol has 887 reviewers (1,703 accounts with the permission) and
states that new articles "will not appear in Internet searches until they are passed". It encodes triage: wait
at least an hour before nominating new articles for deletion, and prioritise with ORES scores. [demonstrated]
<https://en.wikipedia.org/wiki/Wikipedia:New_pages_patrol>

*Cost.* The workshop has a per-job call budget, timeout and explicit retry. Missing: a per-agent daily ceiling
and spend visibility by agent. The expensive failure is fifty agents each making one reasonable request.

**Borrow.** SQLite's online backup API (or `VACUUM INTO`), not `cp` of a live file. [demonstrated]
<https://sqlite.org/backup.html> Nightly backup plus a weekly restore drill that boots the app against the
restored copy and checks row counts and a content hash; alert on "backup older than 26 hours" and "drill
failed", not on exit code 0. Off-host copy with a separate credential
and a runbook someone other than its author has executed. Per-agent daily and global monthly caps enforced
server-side. Four incident classes — availability, data loss, content harm (defamation, privacy, unsafe claim),
security — with content incidents on a fast suppression path separate from the publish queue. Moderation
metrics first-class: queue depth, median time-to-first-review, age of oldest unreviewed item, reviewer
throughput, revert/appeal rate.

**Do not borrow.** Snapshots without a restore test. Email as the only backup-failure alert. "More reviewers"
without queue instrumentation — Nupedia's problem was a process that could not clear work at arrival rate.

**Implications for the spec.** State RPO/RTO (24 h / 1 day is honest for a small team), drill cadence, and which
incident classes require a written postmortem. State the admission-control rule tying participation to review
capacity (§7): a product decision, not an ops detail.

**Open.** Who is on call at launch? If the answer is "the founder, best effort", the reliability language must
say so. Is a content incident a disclosable security incident? Legal review needed.

---

## 7. Launch and participation evidence

**Findings.** *Nupedia (2000–2003).* Seven-step expert approval, expert-written articles: 24 approved in its
lifetime, 21 in the first year, against Wikipedia's 200 in its first month and 18,000 in its first year. The
review process was the product and the bottleneck. [historical/abandoned] <https://en.wikipedia.org/wiki/Nupedia>

*Citizendium (2007–).* Real names, "gentle expert oversight", approved articles. Contributors peaked in Q1 2008
and declined; fewer than 100 active members by October 2011. It ratified its charter in September 2010, three
and a half years after launch; the editor-in-chief stepped down the same month. [historical/abandoned]
<https://en.wikipedia.org/wiki/Citizendium>

*Knol (2008–2012).* Author-owned articles, optional ads and revenue share, default CC BY 3.0 with per-author NC
or all-rights-reserved options. It "did not find a significant audience", closed 2012-04-30, and deleted content
after 2012-10-01. [historical/abandoned] <https://en.wikipedia.org/wiki/Knol>

*Everipedia (2014–).* A Wikipedia fork; "the majority of Everipedia's articles were copied from Wikipedia and
promotional material about cryptocurrency". Pivoted to crypto (IQ.wiki); the encyclopedia became a read-only
archive in October 2022. [historical/abandoned] <https://en.wikipedia.org/wiki/Everipedia>

*Grokipedia (2025–).* Launched 2025-10-27 as "v0.1" with 800,000+ articles; articles "cannot be directly
edited", suggestions are approved or declined by the model, which also edits autonomously. Traffic peaked at
460,000+ US visits on 2025-10-28 and settled near 35,000/day by 2025-11-08/11. A 2026-03-14 rewrite broke
anchors, so previously accepted suggestions were "erroneously retrospectively labeled as rejected". Editing
stopped around late April 2026, leaving content effectively frozen until September 2026. [claimed — secondary
reporting; traffic from Similarweb] <https://en.wikipedia.org/wiki/Grokipedia>

*Retention (Wikimedia, 2011).* New-editor one-year retention "dropped dramatically from mid 2005 to early 2007,
and has since remained low", during the largest influx of new editors in the project's history; long-tenure
editors retained at about 75–80%. The study calls its measures approximations and does not establish causes.
[demonstrated, official study] <https://strategy.wikimedia.org/wiki/Editor_Trends_Study/Results>

*Agent-native wikis (2026).* LLM-Wiki compiles documents into linked pages with search/read/link-following
tools and an "Error Book", claiming 2.0–8.1 F1 over HippoRAG 2, LightRAG and GraphRAG on three multi-hop QA
sets; WikiLoop couples a Builder that proposes edits to a Navigator whose downstream performance scores them,
claiming +6.3 answer correctness on one benchmark. The architecture signals are relevant (compiled views, edit
utility measured downstream); the numbers are preprint claims on QA benchmarks, not evidence about a public
reference's trustworthiness. [claimed] <https://arxiv.org/abs/2605.25480> <https://arxiv.org/abs/2607.26604>

### Launch evidence

Lowering review friction produced supply (Nupedia → Wikipedia), but not quality or retention (Editor Trends).
Participation models that fragmented authorship failed to accumulate a corpus (Knol's many articles per topic;
Everipedia's fork rather than writing). Content that cannot be exported dies (Knol deleted its corpus;
Everipedia archived its). AI-only review is fast and visibly shallow, and its correction loop produced a
five-month freeze rather than a maintained corpus — the failure was not "too few articles" but "no reliable
path from a wrong sentence to a fixed sentence". The launch-traffic shape to expect is the Grokipedia curve:
460k visits, then 35k/day; the interesting question is who returns in week six.

Confounds are large: Wikipedia had a unique era, search position and no serious competitor; Knol and Grokipedia
evidence here is secondary; Citizendium's decline has several plausible causes (real-name policy, founder
dependency, governance delay) that this note does not isolate. The direction of the evidence is consistent; the
magnitudes are not transferable.

**First readers and contributors.** Pick a domain where being wrong has a cost, a few identifiable experts
exist, and sources are open enough to cite. A general encyclopedia competes with Wikipedia on its strongest
ground; a narrow citation-grade reference (methods and statistics, a regulated domain, an ecosystem's
operational knowledge) gives agents a job currently done badly and humans a reason to correct them.

**What makes them return.** A recurring task, a visible correction history, notification when a claim they care
about is challenged, fast review turnaround, and a stable permalink they can cite. Attribution and a citable
revision URL are the currency for expert contributors.

**Strong launch beyond article count.** Time-to-first-review; share of proposals reviewed within a stated
window; latency to correct a planted error; share of articles with an independent reviewer; 30/90-day return
rate; external citations to specific revision permalinks; reader corrections acted on. All measurable at small
scale; none gameable by generating articles.

**Do not open participation faster than review capacity.** Make admission a function of queue health: when
unreviewed backlog exceeds N or median time-to-first-review exceeds T, throttle new agent accounts and proposal
volume automatically, and publish the rule and current state. This is NPP's insight applied to participation.
Sequence: read-only corpus → invited agents propose → open proposals with quotas → agent review for low-risk
classes only after measured catch rates justify it.

**Usefulness, not activity.** Useful: external permalink citations, return visits to the same article,
correction reports citing a specific sentence, persistent downstream API consumers, proposals accepted without
rewriting. Misleading: edits/day, new articles/day, tokens generated, launch-week uniques.

---

## Minimum reliable core at launch vs. deliberately later

**Must be reliable at launch**

| Item | Why it cannot wait |
|---|---|
| Immutable revisions, content hash, stable permalink | Citation, correction and export all depend on a citable address; retrofitting breaks existing citations. |
| Append-only publication events | Otherwise "published on date X" is destroyed by the next publish and cannot be reconstructed. |
| Claim/citation bound to revision, snapshot hash | The core promise is inspectable evidence; a hash added after sources rot is meaningless. |
| Optimistic concurrency with explicit stale-base error | Concurrent agents are the normal case; silent overwrite is unrecoverable trust damage. |
| Idempotency keys on proposal/review/job creation | Retries are guaranteed; duplicates are visible to reviewers and poison the queue. |
| Nightly backup, off-host copy, restore drill | The first data loss is the last chance to have tested recovery. |
| Nightly export with manifest | The only independent copy, and it forces serialisability before the schema ossifies. |
| License and attribution fields | Cannot be asked retroactively; reusers need a clean answer. |
| FTS5 over published revisions, rebuild + integrity check | Search is the primary read path; a drifted index teaches users the site is unreliable. |
| Rate limits, `Retry-After`, problem+json | External agents find limits anyway; undocumented limits produce bans and bug reports. |
| Moderation queue metrics and incident log | Launch is where actual review capacity is learned. |

**Deliberately later**

| Item | Why it can wait |
|---|---|
| CRDT co-editing | Only pays off with many simultaneous editors of one draft; adds merge semantics nobody reviews. |
| Dedicated search cluster | One SQLite file holds the launch corpus; the projection keeps migration open. |
| Streaming replication / multi-region | Single-host SQLite is the stated envelope; replication without tested failover is decoration. |
| Ranks/qualifiers UI | Store fields now if cheap; the editorial workflow is a second product. |
| Public dumps with mirrors and torrents | Wikimedia-scale distribution; a signed nightly export suffices until demand exists. |
| Agent auto-publication | The policy lab shows escapes at current panel correlation; promotion needs measured catch rates. |
| External reproducibility audit | High cost, small launch audience; the internal replay test buys most of the value. |
| Multi-language editions | Each language multiplies review load; one language with a translation-ready schema first. |

---

## Sources checked

All accessed 2026-11-04.

| URL | What it is | Label | Lesson borrowed | Accessed |
|---|---|---|---|---|
| https://www.mediawiki.org/wiki/Manual:Revision_table | MediaWiki schema manual | demonstrated | Immutable rows, parent tree, content hash, archive-on-delete | 2026-11-04 |
| https://www.mediawiki.org/wiki/Help:Edit_conflict | MediaWiki help | demonstrated | Manual 3-way merge; stale conflict page can lose edits | 2026-11-04 |
| https://www.mediawiki.org/wiki/API:Edit | Action API reference | demonstrated | `baserevid` conditional writes since 1.35 | 2026-11-04 |
| https://www.mediawiki.org/wiki/API:Etiquette | API usage policy | demonstrated | Serial requests, `maxlag`, mandatory User-Agent | 2026-11-04 |
| https://www.mediawiki.org/wiki/Help:CirrusSearch | Search help | demonstrated | Near-real-time index (30 min normal); regex capped at 20 s | 2026-11-04 |
| https://en.wikipedia.org/wiki/Help:Permanent_link | Wikipedia help | demonstrated | Permalink guarantees main text only | 2026-11-04 |
| https://www.wikidata.org/wiki/Help:Ranking | Wikidata help | demonstrated | Ranks encode current confidence, not history | 2026-11-04 |
| https://git-scm.com/book/en/v2/Git-Internals-Git-Objects | Pro Git, Git Internals | demonstrated | Content-addressed blobs/trees/commits | 2026-11-04 |
| https://inria.hal.science/hal-00932836 | Shapiro et al., CRDT paper | demonstrated | Strong eventual consistency; convergence | 2026-11-04 |
| https://www.rfc-editor.org/rfc/rfc9110.html | IETF HTTP Semantics | demonstrated | ETags; `If-Match` prevents lost updates; 409 vs 412 | 2026-11-04 |
| https://www.rfc-editor.org/rfc/rfc6585.html | IETF 429 | demonstrated | 429 and optional `Retry-After` | 2026-11-04 |
| https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/ | IETF draft 08 | demonstrated (draft) | Fingerprint; 400/409/422; expiry policy | 2026-11-04 |
| https://docs.stripe.com/api/idempotent_requests | Stripe API reference | claimed | Key retention; response stored incl. 500s | 2026-11-04 |
| https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api | GitHub REST guidance | claimed | Backoff, serial requests, 304 free, follow `Link` | 2026-11-04 |
| https://sqlite.org/wal.html | SQLite WAL docs | demonstrated | Single writer; BUSY edges; no network FS | 2026-11-04 |
| https://sqlite.org/fts5.html | SQLite FTS5 docs | demonstrated | External-content sync burden; drift; BM25 | 2026-11-04 |
| https://sqlite.org/backup.html | SQLite backup API | demonstrated | Online backup instead of file copy | 2026-11-04 |
| https://creativecommons.org/licenses/by-sa/4.0/legalcode.en | CC BY-SA 4.0 legal code | demonstrated | Attribution; adapter license; database rights (§4) | 2026-11-04 |
| https://opendatacommons.org/licenses/odbl/1-0/ | ODbL 1.0 | demonstrated | Produced Work vs Derivative Database | 2026-11-04 |
| https://creativecommons.org/publicdomain/zero/1.0/legalcode.en | CC0 1.0 legal code | demonstrated | Waives copyright and database rights; max reuse, no share-alike | 2026-11-04 |
| https://en.wikipedia.org/wiki/Wikipedia:Copyrights | Wikipedia policy | demonstrated | Reuser attribution; modification notice | 2026-11-04 |
| https://meta.wikimedia.org/wiki/Data_dumps | Wikimedia dumps docs | demonstrated | Monthly; "not backups, not complete" | 2026-11-04 |
| https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/ | GitLab postmortem | demonstrated | Five recovery mechanisms failed together | 2026-11-04 |
| https://sre.google/sre-book/postmortem-culture/ | Google SRE ch. 15 | demonstrated | Pre-set triggers; blameless; review required | 2026-11-04 |
| https://neurips.cc/public/guides/PaperChecklist | NeurIPS checklist | demonstrated | Mandatory, visible, "no" with justification | 2026-11-04 |
| https://en.wikipedia.org/wiki/Wikipedia:New_pages_patrol | Wikipedia NPP | demonstrated | Review gates search indexing; ORES triage | 2026-11-04 |
| https://en.wikipedia.org/wiki/Nupedia | Encyclopedia article | historical/abandoned | 24 articles in ~3 years vs 18,000 in one year | 2026-11-04 |
| https://en.wikipedia.org/wiki/Citizendium | Encyclopedia article | historical/abandoned | <100 active by 2011; real names plus expert approval | 2026-11-04 |
| https://en.wikipedia.org/wiki/Knol | Encyclopedia article | historical/abandoned | No audience; closed; content deleted | 2026-11-04 |
| https://en.wikipedia.org/wiki/Everipedia | Encyclopedia article | historical/abandoned | Fork of copied content; crypto pivot | 2026-11-04 |
| https://en.wikipedia.org/wiki/Grokipedia | Encyclopedia article | claimed | 460k → 35k visits/day; 5-month freeze | 2026-11-04 |
| https://strategy.wikimedia.org/wiki/Editor_Trends_Study/Results | Wikimedia study | demonstrated | Retention fell 2005–07 and stayed low | 2026-11-04 |
| https://arxiv.org/abs/2605.25480 | Preprint, LLM-Wiki | claimed | Compiled wiki pages; QA benchmark gains | 2026-11-04 |
| https://arxiv.org/abs/2607.26604 | Preprint, WikiLoop | claimed | Builder/Navigator scores edits by utility | 2026-11-04 |

---

## What I could not verify

- **ACM artifact badging** — `acm.org` served a bot-verification page, not the policy. No claim is made about
  its badges; the NeurIPS checklist is the substitute.
- **Halfaker et al., "The Rise and Decline of an Open Collaboration System"** (DOI 10.1177/0002764212469365) —
  metadata confirmed via Unpaywall and Semantic Scholar; the paper is closed access with the abstract elided.
  Nothing is taken from it; the Wikimedia Editor Trends Study is cited instead. The two are related but not
  interchangeable.
- **Meta's Editor Trends Study page** returned no extract via the API; I read the raw wikitext of its Results
  subpage on the read-only strategy wiki. Figures are from that page.
- **DuckDuckGo HTML search** worked once, then returned a bot challenge; later discovery used known canonical
  URLs. This narrows the source set, not the verification of what is listed.
- **The Turing Way** landing page rendered only navigation, so nothing is cited from it.
- **Grokipedia and Everipedia traffic/outcomes** are secondary reporting, not primary analytics.
- **No load test, cost measurement or restore drill was run.** Claims about where SQLite or the job queue break
  are reasoning from documented semantics, not measurement on this workshop.
