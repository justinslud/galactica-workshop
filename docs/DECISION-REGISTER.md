# Decision register

**Version:** 1.0, 2026-11-04. **Last update:** 2026-11-05 — see
[Decision updates — 2026-11-04](#decision-updates--2026-11-04) for the answers recorded from the product review,
[M0 implementation status](#m0-implementation-status-same-date-separate-pass) for the M0 slice, and
[Implementation update — 2026-11-05](#implementation-update--2026-11-05-authorization-state-machine-and-human-review-dashboard)
for the authorization/state-machine/review-dashboard slice (D-41, D-42) and the M0 remainder (D-43).
**Purpose:** one place to see what is decided, what is proposed, who can decide it, what evidence supports it, and
what would cause a revisit. It does not replace `~/projects/galactica/DECISIONS.md`; it extends the product
specification and preserves the earlier record.

**Status vocabulary**
- **accepted** — an existing dated decision, the 2026-10-27 course clarification, or an answer Justin gave in the
  2026-11-04 review (see [Decision updates — 2026-11-04](#decision-updates--2026-11-04)). Revisable, but a change
  must be recorded as a change.
- **proposed** — recommended in this specification; not ratified. Reversible unless marked otherwise.
- **experimental** — must be tested before adoption; the experiment and stopping rule are in
  [EXPERIMENTS.md](EXPERIMENTS.md).
- **open** — no recommendation yet, or the answer depends on a decision Justin has not made.
- **deferred** — deliberately not now; conditions for revisiting are stated.
- **ask Justin** — reserved for values, identity, major scope, irreversible commitments, spending, or tradeoffs
  where his preference materially matters.

**Authority routes**
- **A** — recommend a reversible default (with downside, reversal, revisit trigger).
- **B** — run an experiment (competing options, measurements, cost, stopping rule).
- **C** — obtain independent AI critique (advisory only; preserve dissent; not a ratification).
- **D** — ask Justin.
- **E** — defer or exclude.
Where a row shows two letters (e.g., `A+B`), the first is the primary route; the second is a required
complement (for example, a default that must be calibrated by an experiment). No decision is ratified by an AI
review; route C informs, it does not decide.

**Domain** distinguishes decisions about **building the product** from **governance decisions a future community
would make**. AI reviewers in this assignment are advisory; they do not ratify policy on Justin's behalf.
Decisions reserved for the future community are listed at the end of this document.

---

## Summary

| ID | Decision | Recommendation | Status | Route | Domain |
|---|---|---|---|---|---|
| D-01 | Name | Keep Galactica as working name; decide T5/t5.wiki before public beta | open — interim answer 2026-11-04: keep working name; T5 short-listed; no rename | D | identity |
| D-02 | Product center | Article-first, evidence-supported; assertions are stable support | accepted direction + proposed architecture | A | product |
| D-03 | Topic object | Add a stable Topic with scope, aliases, coverage checklist | proposed; **partial M0** (minimal `Topic` + `Article.topic`) | A | product |
| D-04 | Article variants | One canonical article; reading levels are views; translations are views until reviewed as editions | proposed | A | product |
| D-05 | Assertion model | Defer full assertions to M4; add `claim_key` + change diff at M2 | proposed (M4 trigger) | A+B | product |
| D-06 | Revision immutability | Keep immutable revisions as the publication/rollback unit | accepted (implemented) | A | product |
| D-07 | Block model | Extend typed blocks; add map/chart/data later; no arbitrary HTML | proposed | A | product |
| D-08 | View contract | Views pin base revisions, declare generator/reviewer, go stale automatically | proposed | A | product |
| D-09 | Source assessment | Per-use, per-topic assessment with reasons and expiry | proposed | A | product |
| D-10 | Machine checks vs judgment | Enforce quote/substring/snapshot/staleness; leave entailment/neutrality to review | accepted direction + proposed | A | product |
| D-11 | Neutrality | Specific reviewable checks, never a single score | proposed | A | product |
| D-12 | Negative information | Higher evidence bar, right of reply, no forced balance | proposed | A | product + governance |
| D-13 | Correction intake | Public correction form with tracked states and service levels | proposed | A | product |
| D-14 | COI/company submissions | Mandatory disclosure, verified org accounts, no self-publication | proposed | A | governance |
| D-15 | Anti-churn | Adequacy state; changes need a reason category; no taste-only rewrites | proposed | A | product |
| D-16 | Split/merge | Explicit proposal with scope, redirects, assertion mapping | proposed | A | product |
| D-17 | Review roles | Separate factual, source, coverage, readability, policy, translation, community | proposed | A | product |
| D-18 | Reviewer independence | Cross-model/provider panels where possible; record correlation | proposed | A+B | product |
| D-19 | Launch publication policy | Tiered review minimum + human publisher; no autonomy at launch | accepted direction + proposed policy | A | governance |
| D-20 | Autonomy | Only after measured shadow mode meets a published threshold | experimental | B | governance |
| D-21 | Appeals | 14-day window; one adjudicator at launch, 3-person panel at ≥30 contributors; public reasons | proposed | A | governance |
| D-22 | Disputes | Structured assertion/scope disputes, separate from conduct | proposed | A | governance |
| D-23 | Identity | Durable accounts; observed/self-declared/verified metadata; no global score | accepted direction + proposed detail | A | product + governance |
| D-24 | Sybil/coordination | Behavioral clustering, rate limits, human review; not viewpoint policing | proposed | A+B | governance |
| D-25 | Quotas | Start in stated ranges; calibrate to review capacity | proposed | B | governance |
| D-26 | Admission control | Capacity-based; pause onboarding before lowering review quality | proposed | A | governance |
| D-27 | API | Public read, scoped write, idempotency, ETags, cursor pagination, no publish | proposed | A | product |
| D-28 | Concurrency | Optimistic base checks; proposal branches; no silent CRDT merge of facts | proposed | A+B | product |
| D-29 | Search | SQLite FTS5 first; hybrid/embeddings later; evaluate recall@3 | proposed | A+B | product |
| D-30 | Licensing/exports | CC BY-SA 4.0 articles + CC0 identifiers/templates (not verbatim prose), subject to counsel; snapshots not bulk-redistributed | accepted 2026-11-04 (subject to counsel) | D | legal |
| D-31 | Reproducibility | Config/model/prompt/snapshot/seed recorded; replay tool | proposed | A | product |
| D-32 | Ops | SQLite + WAL, nightly backups + restore drill, cost caps, incident runbook | proposed | A | product |
| D-33 | Prompt injection | Sources are data; least privilege; schema validation; red-team | accepted direction + proposed | A | product |
| D-34 | Governance authority | Founder-stewarded now; publish the transition trigger; foundation deferred (may come earlier) | accepted 2026-11-04; foundation deferred | D/E | governance |
| D-35 | Policy lifecycle | Versioned policy, public comment, reasons, review, emergency clause | proposed | A | governance |
| D-36 | Seed corpus | 5–8 public anchor topics in one citation-costly wedge; 12-topic matrix as internal fixtures | accepted direction 2026-11-04 (real subjects; no hypothetical seed cases); wedge list still open | A | product |
| D-37 | Launch stages and public beta timing | Dogfood → private alpha → public read/correct → public contribute; timing gated on readiness, not a date | accepted 2026-11-04 (private alpha with friends/advisors, then gated public beta, no date); timing open | A/D | product |
| D-38 | Usefulness metrics | Task success, return, citation, correction, review health; no vanity metrics | proposed | A+B | product |
| D-39 | Languages | Independent articles, shared assertions, human translation review | deferred (pilot later) | E | product |
| D-40 | Personalization | Presentation only; transient explanations with citations, not published facts | proposed | A | product |
| D-41 | Authorization and editorial state machine | One deterministic evaluator for capabilities, derived proposal states, transitions, quotas and relationship guards; capability tiers are not identity verification | accepted direction + implemented v1 (2026-11-05); quota numbers are starting parameters, not measured | A+B | product + governance |
| D-42 | Human review dashboard | Shared `/review/` queue for standard/trusted/steward with state filters, counters, review coverage, objections and stale flags; no auto-assignment | accepted direction + implemented v1 (2026-11-05) | A | product + governance |
| D-43 | M0 remainder | Revision permalinks + revision-bound claim resolver; license fields with per-publication snapshot; FTS5 published-only search; local backup/restore drill; `Idempotency-Key`/`If-Match` on write API | implemented v1 (2026-11-05); no claim merge/alias or claim_key yet | A | product + ops |

---

## Decision updates — 2026-11-04

**Source:** the answers Justin gave in the 2026-11-04 product review, recorded here as the dated decision-update
layer over this register. Decision updates 2026-11-04 supersede the earlier `open` / `proposed` marking for the
entries listed below; the Summary table and the detailed entries have been edited to match. The decision-update
pass itself changed documentation only, not application code. A **separate M0 implementation pass on the same
date** implemented the append-only `PublicationEvent`, a minimal `Topic` with `Article.topic`, the opt-in `Watch`
and the reader surfaces listed under "M0 implementation status" below; **every other decision in this register
remains unimplemented**, and no M1+ item is complete.

### Accepted decisions

| ID | Question | Answer recorded 2026-11-04 | Resulting status |
|---|---|---|---|
| D-01 | Name | Keep the current working name (**Galactica**); the user's stated everyday label is **Galactic Hub**, recorded as usage, not a decision to rename the repository; keep **T5/t5.wiki** on the short list; **no repository rename**; **no final name decision**. | open — interim answer recorded; final choice still before public beta |
| D-30 | Licensing | Accept the recommendation: **CC BY-SA 4.0 for articles, CC0 for identifiers/templates (not verbatim prose)**, subject to counsel. | accepted (subject to counsel) |
| D-34 | Governance transition | Accept the **published-trigger** approach; a foundation can wait and **may be created earlier**; **do not create a foundation now**. | accepted |
| D-36 | Seed subjects | Use **real subjects, not hypothetical ones**; hypothetical company/person cases stay in **`/sandbox`**; the specific **wedge/subject list remains open**. | accepted direction (real subjects; hypothetical cases `/sandbox`); wedge list open |
| D-37 | Public beta | **Private alpha with friends/advisors first, then a gated public beta**; **no public beta date**. | accepted (stage order and gating); timing open |

**Notes on the accepted decisions**

- **D-01:** the working name stays Galactica, so all content, engineering and documents continue under it.
  "Galactic Hub" is recorded as the user's stated everyday label, not as a rename of the repository or product.
  T5/t5.wiki is short-listed, not chosen. The earlier reasons to keep D-01 open — "T5" collides with a well-known
  model name, "Truth Attractor" overclaims, domain/trademark checks unverified — are unchanged and are why no
  final name was recorded.
- **D-30:** this accepts the register's licensing *recommendation*; it does not complete counsel review or authorize
  public exports or API redistribution. Those remain gated on counsel (D-30, D-27).
- **D-34:** accepting the published-trigger approach settles the mechanism and defers foundation timing. It does not
  create a foundation, incorporate anything, or move authority; the steward model and published policies continue.
- **D-36:** "real subjects, not hypothetical ones" settles the real-vs-hypothetical question for the seed corpus.
  The **D-12 launch limit** on real living-person/company content (a named policy/legal reviewer and counsel must
  exist first) was not overridden by this answer and remains an unmet dependency for any living-person/company
  subject. The specific wedge and the 5–8 anchor topics are still to be chosen.
- **D-37:** the stage order and the gating are accepted; **no date is set or implied**. Readiness criteria in
  [PRODUCT-SPEC.md](PRODUCT-SPEC.md) §9.4 still govern the transition to public read/correct and public contribute.

### M0 implementation status (same date, separate pass)

Only the first M0 slice is implemented in the workshop, and only these parts of the register's roadmap are
therefore "implemented":

| Register entry | Implemented in M0 (2026-11-04) | Still open |
|---|---|---|
| D-03 Topic object | minimal `Topic` (slug, title, scope statement, parent, disambiguation flag, creator) + `Article.topic`; demo topic seeding; `/topics/` and `/topics/<slug>/` showing published articles | full scope/coverage checklist, aliases, split/merge, disambiguation behaviour, migration of all articles |
| D-04/D-08 views | — | `View` object and manifest, reading levels, translations |
| D-36 seed corpus | real-subject direction only as **3 demonstration topics** seeded locally (no public seed portfolio chosen) | the specific wedge and 5–8 anchor topics; real living-person/company subjects remain out of scope until a policy/legal reviewer and counsel exist |
| M0 publication history | append-only `PublicationEvent` (per-article sequence; kinds `initial`/`publish`/`revert`/`import`; previous revision, policy version, decision, reason, content hash; unique per article+sequence and article+revision; event→article FK is `PROTECT` so history is not cascade-deleted); written by `publish()`, `revert()` and `create_published_revision()`; history-page publication log; migrations `0006`/`0007`/`0008` (6 events backfilled locally); revision permalinks and the claim resolver added 2026-11-05 | a designed public (anonymous) full-history surface |
| M0 return loop | byline/credit page `/contributors/<username>/` (no private data), opt-in `Watch`, login-only `/watchlist/` web digest (no email), article-page byline/topic/provenance/watch block | scheduled digest, notifications, email |
| Other items listed as not implemented | — | **M0 remainder completed 2026-11-05 (D-43):** license/attribution fields, SQLite backup + restore drill, FTS5, `Idempotency-Key`/`If-Match`. Still open: correction intake, review tiers, full `Topic` scope/coverage (M1); `View`/`Assertion` objects (later) |

Tests at that point: **154 pass** (was 133; 21 new in `core/tests/test_m0_publication_topic_watch.py`); the current
suite is **190**. `manage.py check` and `makemigrations --check` clean. The local database was migrated; nothing was
deployed, no production data or
credentials changed, and no repository rename happened.

### Open questions (recorded, not decided)

These came out of the same review as unresolved design questions. They are **not** decisions, nothing below ratifies
a recommendation, and no answer should be inferred from the accepted decisions above.

| Ref | Open question | Why it stays open | Related decisions |
|---|---|---|---|
| OQ-1 | How an article-first article should reflect a claim ledger — and what claim-first would look like | The article-first direction (D-02) and the deferred assertion model (D-05) leave the article↔ledger bridge undesigned; this is the preserved disagreement, not a settled answer | D-02, D-05 |
| OQ-2 | Deterministic/state-machine authorization and quota policy — weaker identity but lower privileges | The identity direction (D-23) and the quota ranges (D-25, D-26) were proposed, but a deterministic authorization/privilege policy tying weaker identity to lower capability has not been designed or tested | D-23, D-25, D-26 |
| OQ-3 | Whether views are authored or generated, and how visual views work | The view contract (D-08) defines manifests and staleness but not the authoring model; charts/maps/data views (D-07) are future blocks with no design | D-04, D-07, D-08 |

**Status note (2026-11-05):** OQ-2 is now partly addressed — D-41 implements a first deterministic authorization
evaluator with starting quota parameters; quota calibration and trust-promotion rules remain open. OQ-1 and OQ-3
are unchanged.

**What this pass did not do:** it did not implement any decision in code, did not rename the project or repository,
did not commit changes, and did not promote the open questions above into decisions. It updated documentation only.
(The separate M0 implementation pass is recorded above; the 2026-11-05 authorization slice is recorded below.)

---

## Implementation update — 2026-11-05: authorization, state machine and human review dashboard

**Source:** a lead-authored design note, [AUTHORIZATION-STATE-MACHINE.md](AUTHORIZATION-STATE-MACHINE.md), plus its
implemented first slice in the workshop. This is an implementation record, not a new set of values decisions: it
routes existing editorial actions through one evaluator and adds a human queue. It does **not** change the
publication minimums in D-19 or turn capability tiers into identity verification under D-23.

**Implemented (v1, 2026-11-05):**
- `core/authorization.py`: capability/trust table; derived proposal states `submitted`, `under_review`, `approved`,
  `published`, `rejected`, `changes_requested`; one `can()` decision evaluator with reason codes;
  rolling 24-hour quotas; self-review, self-decision and self-publication guards; agent-scope checks.
- `ContributorProfile` (`new`/`standard`/`trusted`/`steward`; staff default `steward`, other accounts default
  `standard`; admin-editable) and `Review.reviewer`; migration `0009_contributor_profiles_reviewer`.
- Service enforcement in `open_proposal`, `submit_draft`, `save_draft`/`ensure_draft`, `record_review`, `decide`,
  `publish` and `revert`; the human review form records `origin=human` and the reviewer.
- `/review/` human queue (standard/trusted/steward; `new` and anonymous denied) with state filters, counters,
  review coverage, objections and stale flags; nav link; no auto-assignment (the queue is shared).

**Quotas (starting parameters, not measured):** `new` 1 proposal/day and 0 human reviews; `standard` 5/10;
`trusted` 10/25; steward unlimited; all rolling 24 hours; human reviews counted only where `origin=human`. These
numbers are policy parameters, not calibration results; E2/E3 and the review-hour ratio should set them.

**Same-agent caveat:** a same-agent review is allowed in v1 but is recorded in the audit detail as
`same_agent: true` and is **not independent evidence**. Do not count same-agent reviews when measuring reviewer
value (E2/E3).

**Tests:** **171 pass** (was 154; 17 new in `core/tests/test_authorization_dashboard.py`); `manage.py check` and
`makemigrations --check` clean. No browser-level check was made; the queue and form are test-verified only.

**Not implemented:** auto-assignment, automatic trust promotion, an external policy engine, the `withdrawn` state,
appeal/dispute state machines, a trust-management UI beyond Django admin, and per-reviewer calibration.

**Open calibration questions (recorded, not decided):**
- How does an account move `new` → `standard`/`trusted`? A steward action plus audit is the current mechanism;
  automatic promotion is not implemented and is open.
- Should `new` accounts see the queue after a first accepted review? The slice blocks `new`; the promotion path is open.
- Are the quota numbers right? They are starting parameters, not measured; E2/E3 and the review-hour ratio should
  calibrate them (see D-25/D-26).
- Should a steward decide a human proposal they edited but did not author? The `created_by` authorship test is
  conservative but incomplete.
- Should a withdrawn proposal keep its candidate public? Withdrawal is not implemented.

**Decision statuses:** D-41 (authorization and editorial state machine) and D-42 (human review dashboard) are
recorded as **accepted direction + implemented v1** with the calibration questions above still open. D-43 (M0
remainder) is **implemented v1**; its limits are in the entry. D-19 (publication policy minimums) and D-23 (identity
verification) keep their own statuses unchanged; this slice is the mechanism, not a ratification of either policy.

---

## What the research changed

These are the findings that materially altered a recommendation. They are recorded here so the register can be
read against the evidence in `docs/research/`.

1. **Reader clarity outranks provenance in readers' own ratings, and citations are rarely clicked.** Clarity
   (4.43) and structure (4.37) scored above "adequate number of references" (4.06) and "high-quality references"
   (3.97); about 0.29% of page views produce a reference click (R1). This changed the reader design from
   "evidence-first" to "clarity first, evidence one step away", and added the summary/quick-fact surface.
2. **Showing raw process can lower measured quality judgements even while readers report higher trust.** The
   CSCW experiment found that surfacing deliberation lowered quality ratings, conflict lowered them further, and
   resolved conflict removed the penalty; participants were unaware and said the discussion raised their trust
   (R1). This changed the dispute design from "show the thread" to "show adjudication, link the record".
3. **Derived views should follow through, not duplicate citations.** Wikipedia's portal practice is that derived
   reader surfaces carry no references and link to the sourced article (R1). This became view contract V10.
4. **A permalink is not a reproduction.** MediaWiki guarantees only main text; templates and images render live
   (R3). This added the view manifest and the "rendered artifact" requirement.
5. **Publication history needs an append-only event, not a mutable pointer.** `Article.published` is overwritten
   on every publish; "what was published on date X" cannot be reconstructed (R3). This added `PublicationEvent`
   as the first implementation slice.
6. **Review value decays with delay, and review capacity is concentrated.** 90% of ever-detected hoaxes are
   flagged within an hour; a month-old review catches almost nothing new. English Wikipedia has 887 New Page
   Reviewers, but one account logged 21,658 reviews in a year (R2). This added review-at-creation as the launch
   policy (not an invariant), with the newcomer-retention tension preserved, and the capacity warning.
7. **Technical sybil detection is weak, and the attack targets the review pipeline.** CheckUser calls its own
   conclusions limited; Orangemoody combined technical and behavioural evidence and still found the scheme
   fortuitously; a sock marking another sock's article reviewed is not caught by content checks (R2). This
   changed sybil defence from identity verification to review-capacity protection and sampled re-review.
8. **Licensing cannot be retrofitted, and CC BY-SA §4 reaches databases.** ODbL distinguishes a Produced Work
   from a Derivative Database (R3). This made D-30 an explicit "ask Justin + counsel before public exports" item
   and added license fields to the schema.
9. **"T5" and "Truth Attractor" carry avoidable risk.** "T5" is strongly associated with a well-known model name;
   "Truth Attractor" overclaims a product that is built on verifiability and uncertainty, not truth. This kept
   D-01 open rather than treating the rename as a formality.

---

## Detailed entries

### D-01 — Name

**Recommendation:** keep **Galactica** as the working name for now. Evaluate **T5 / t5.wiki** ("Truth Attractor")
as a candidate before public beta. Do not rename the repository, package, database or URLs as part of this
assignment.
**Status:** open — **interim answer 2026-11-04:** keep the current working name (Galactica); the user's stated
everyday label is **Galactic Hub**, recorded as usage, not a decision to rename the repository; keep T5/t5.wiki on
the short list; no repository rename; no final name decision (see
[Decision updates — 2026-11-04](#decision-updates--2026-11-04)). **Route:** D (identity). **Domain:** identity.
**Evidence / considerations:** "T5" is strongly associated with Google's Text-to-Text Transfer Transformer model,
which hurts search distinctiveness and may imply a model rather than a reference. "Truth Attractor" is memorable
but overclaims: the product's credibility rests on uncertainty and evidence, not on possessing truth. Domain
availability, trademark clearance and audience testing are unverified.
**Downside:** keeping Galactica preserves continuity but may be confused with the earlier prototype and with
science-fiction references; T5 may be more distinctive but carries collision and overclaim risk.
**Reversal / revisit:** before any public beta, after a 5-question naming test with target readers and a
trademark/domain check. The name can change without changing the product model; it is a branding layer.

### D-02 — Product center

**Recommendation:** the **article revision is the publication unit**; the claim/evidence ledger supports it. A
topic's assertions are stable, but the reader-facing artifact is an editorially reviewed article.
**Status:** accepted direction (2026-10-27 clarification) + proposed architecture. **Route:** A. **Domain:** product.
**Evidence:** the clarification explicitly says explanations and diagrams are substantive and that the claim
ledger does not replace article authorship; the workshop is already article-first; `docs/model.md`'s "claim ledger
with page views" framing is the outlier.
**Downside:** less structured reuse than an assertion-first product; harder to expose a clean claim graph.
**Reversal:** if downstream agent demand for structured assertions dominates, promote assertions to a
first-class API surface while keeping articles as the publication unit. Revisit after 100 articles or 10 API
consumers.

### D-03 — Topic object

**Recommendation:** add a stable `Topic` object separate from `Article`, with canonical title, aliases, scope
statement, coverage checklist, risk class, maturity, languages, parent/related topics and merge target.
**Status:** proposed; **partial M0** — a minimal `Topic` (slug, title, scope statement, parent, disambiguation
flag, creator) and `Article.topic` are implemented with demo topic seeding; aliases, scope/coverage checklist,
risk class, maturity, languages and split/merge are not (see
[M0 implementation status](#m0-implementation-status-same-date-separate-pass)). **Route:** A. **Domain:** product.
**Evidence:** before M0 the app used `Article` as the de facto topic; split/merge, aliases and cross-language
identity still have no home beyond the minimal M0 fields. Wikipedia's summary-style and merge practices show the
need for a stable scope unit; the TS prototype already has topic rename/alias/merge concepts.
**Downside:** schema and UI complexity; migration of existing articles; risk of two competing "topic" notions.
**Reversal:** keep `Article` as the canonical content object and add topic metadata as fields first; split only
when a second article per topic (language/reading level) exists. Revisit at the first split/merge or language
pilot.

### D-04 — Article variants

**Recommendation:** one canonical article per topic per language (standard reading level). **Reading-level
variants are views over one claim base**, not separate wikis; **translations are views of a source revision**
until a human reviewer in the target language promotes an edition. A language edition, once reviewed, becomes an
article with its own revisions, sharing topic/assertion IDs.
**Status:** proposed. **Route:** A. **Domain:** product.
**Evidence:** Simple English Wikipedia is a separate edition with ~4% of English Wikipedia's articles (286,395
vs 7,259,287), and its own policy says most articles are simplified copies of other editions — a fork with a
permanent drift problem. Wikimedia's Content Translation tracks the modification ratio and warns that unmodified
MT is likely to be deleted. The current app has one article per slug. (R1)
**Downside:** translation review capacity; a view/edition boundary that contributors must understand.
**Reversal:** start with reading levels as views and one language; promote a view to an edition only after a
named reviewer and a maintenance plan exist. Revisit after the first language pilot.

### D-05 — Assertion model

**Recommendation:** **defer the full `Assertion` object to M4.** At launch, add a stable `claim_key` to the
existing `Claim` (a hash/identity for substantive claims) plus a "this claim changed" diff. This delivers most of
the cross-revision value at a fraction of the cost. Introduce topic-scoped `Assertion` records only when a claim
has been corrected twice across revisions and a reader/agent asks what we used to say.
**Status:** proposed (M4 trigger). **Route:** A + B. **Domain:** product.
**Evidence:** current claims are revision-bound; cross-revision tracking, dispute pages and views need stable
identity. Wikidata statements and micropublication/nanopublication models demonstrate statement-level
provenance; the risk is over-structuring every sentence.
**Downside:** more schema/editorial overhead; semantic matching is error-prone; risk of re-pointing a claim to
the wrong assertion.
**Reversal:** if the overhead is not justified, keep assertions only for disputed/high-value claims and leave
ordinary claims revision-bound. Revisit after 50 articles or the first dispute that requires cross-revision
tracking.

### D-06 — Revision immutability

**Recommendation:** keep immutable revisions as the publication and rollback unit; every change is a new
revision; published revisions are never edited.
**Status:** accepted (implemented and tested). **Route:** A. **Domain:** product.
**Evidence:** `core/editorial.py` enforces this; tests cover stale publication and revert; the TS prototype used
append-only claims and dated states.
**Downside:** storage growth; more revisions; editors must understand the model.
**Reversal:** none recommended; this is a foundational invariant. Revisit only if a different content model
(e.g., CRDT documents) is adopted, which would be a major rewrite.

### D-07 — Block model

**Recommendation:** keep typed blocks; add `heading`, `map`, `chart`, `data`, `quote`, `callout` later; no
arbitrary HTML or agent JavaScript.
**Status:** proposed. **Route:** A. **Domain:** product.
**Evidence:** current `markdown`/`image`/`table`/`timeline` blocks are sanitised and stable; the TS MVP's caps
were an MVP forcing function, not a product decision. Structured blocks are needed for views and exports.
**Downside:** each new block type needs validation, rendering, accessibility and export support; map/chart
maintenance is expensive.
**Reversal:** add block types behind feature flags; remove unused types. Revisit when a view type is requested by
multiple readers/contributors and has a maintenance owner.

### D-08 — View contract

**Recommendation:** adopt the view contract (V1–V12) for **derived artifacts** (translation, audio, chart,
generated explainer), with a manifest: no new facts, pinned base/assertions/source snapshots, attributed
generation, immutable versions, staleness on any basis change, review before citable publish, omitted-topic list
(no coverage ratio), license inheritance, follow-through, stable citation, accessible degradation, owner and
expiry. **Lead, at-a-glance, timeline and table are revision content**, not `View` objects; they are reviewed
with the article and do not go stale on every edit.
**Status:** proposed (M3). **Route:** A + B. **Domain:** product.
**Evidence:** the current app has no view object; summaries/timelines/tables are blocks or prose. The TS
prototype's dated page states and deterministic export show the value of pinning. MediaWiki's permalink only
guarantees main text; templates and images render live, so a view needs a manifest (R3). Wikipedia's portal
practice is "follow through" — derived surfaces carry no references and link to the sourced article (R1).
Wikidata ranks/references and stable-version systems show provenance patterns. **This is the highest-consequence
product design addition.**
**Downside:** review cost for every view; staleness can proliferate; readers may ignore badges; coverage
percentages can invite false precision.
**Reversal:** start with summary/timeline/table only; if staleness is unmanageable, reduce to views that are
generated on read from the current revision (with no independent review) and label them "generated, not
reviewed." Revisit after the first view pilot.

### D-09 — Source assessment

**Recommendation:** assess sources per use and per topic, with dimensions and reasons; record shared origin
**assigned by the application** (not the proposer); include a scope-match dimension (population/region/period);
allow `unassessed`; expire assessments; allow challenge.
**Status:** proposed. **Route:** A. **Domain:** product.
**Evidence:** Wikipedia's reliable-sources guidance is context-dependent and revisable; perennial-sources pages
show repeated community arguments; the TS prototype already has confidence classes and shared-origin downgrade.
**Downside:** assessment labor; inconsistent judgments; potential for bias in ratings.
**Reversal:** start with a lightweight rubric and only assess sources used in disputed/high-risk claims; expand
if useful. Revisit after 100 source assessments or the first source-rating dispute.

### D-10 — Machine checks vs judgment

**Recommendation:** machine-enforce quote-in-snapshot, claim-substring, snapshot presence, source-preserved-for-job,
stale base, duplicate hash, citation schema, and view base pin. Leave entailment, overgeneralization,
misattribution, neutrality and proportion to review.
**Status:** accepted direction (implemented for quotes/substrings) + proposed expansion. **Route:** A. **Domain:**
product.
**Evidence:** `core/editorial.py` already enforces quote/substring/snapshot; the 2026-10-28 note explicitly
distinguishes machine enforcement from model judgment. Crossref exposes 81,345 retraction records with
`update-to` links, so DOI retraction status is machine-checkable (R2). Shared-origin detection is partly
computable from publisher/author/DOI metadata; the residual is judgment. (R2)
**Downside:** false confidence that "machine-checked" means true; reviewers may rubber-stamp.
**Reversal:** keep the distinction visible in the UI; never label a claim "verified" from machine checks alone.
Revisit if a machine check proves unreliable.

### D-11 — Neutrality

**Recommendation:** split the checks: **four mandatory sentence-level checks** (attribution, labeling, scope,
language) any trained reviewer can do, plus **five coverage judgments** (proportion, framing, omission, false
balance, sourcing symmetry) requiring recorded domain competence or a `coverage` reviewer. Record the anchor and
"not assessed, because…" for each skipped check; no single score. Reader-takeaway is a usability test, not a
review criterion.
**Status:** proposed. **Route:** A. **Domain:** product.
**Evidence:** Wikipedia NPOV/due-weight/fringe guidance is procedural and argued, not a score; the current
workshop's readability reviewer is too narrow for framing/proportion.
**Downside:** reviewer time; inconsistent application; checklists can become ritual.
**Reversal:** start with 4 checks (proportion, attribution, omission, false balance) for contested topics; expand
if calibration shows value. Revisit after 50 contested reviews.

### D-12 — Negative information

**Recommendation:** higher evidence bar; label allegations; include a substantive right of reply; no forced
balance; privacy/legal review; do not remove well-sourced negative information because the subject objects.
**At launch, real living-person/company content is out of scope** until a named policy/legal reviewer and
counsel exist; the review system's measured escape rate cannot support the promise.
**Status:** proposed; launch scope limited. **Route:** A. **Domain:** product + governance.
**Evidence:** Wikipedia BLP and NPOV/due-weight practices; COPE/retraction norms; the workshop has no BLP-specific
flow. The BLP default is asymmetric: contentious material that is unsourced or poorly sourced is removed
immediately and without discussion; the three-revert rule does not apply; no-consensus defaults to removal for
living people, not retention. Companies are not BLP subjects; for a company the shield is due weight and
sourcing quality (R2).
**Downside:** legal risk; subject pressure; reviewer discomfort; potential for harm if handled badly.
**Reversal:** require a second reviewer and legal check for BLP/high-risk; if incidents occur, tighten to a
pre-publication legal review for all living-person content. Revisit after the first BLP case or legal review.

### D-13 — Correction intake

**Recommendation:** public correction form with tracking code, states, service levels, public notice, link to
proposal/decision; no account required.
**Status:** proposed. **Route:** A. **Domain:** product.
**Evidence:** Wikimedia VRT and Wikipedia correction/OTRS practices show demand; the current app has no reader
correction path; the TS prototype has no correction flow.
**Downside:** spam/abuse; handling volume; privacy of reporters; expectation management.
**Reversal:** start with a simple form + staff triage; add automation only after volume. Revisit after 100
corrections or the first legal request.

### D-14 — COI and company submissions

**Recommendation:** mandatory disclosure; verified organization accounts; labeled "provided by"; independent
review; no self-publication; recusal; company corrections treated as correction reports.
**Status:** proposed. **Route:** A. **Domain:** governance.
**Evidence:** Wikipedia COI/paid-contribution disclosure and Terms of Use; the decisions explicitly allow
organization factual material with attribution but not advertising.
**Downside:** verification cost; deterrence of legitimate orgs; enforcement difficulty.
**Reversal:** start with disclosure + manual verification for orgs; if abuse is low, simplify. Revisit after the
first company case.

### D-15 — Anti-churn

**Recommendation:** define `stable` adequacy; require a reason category for changes; refuse taste-only/no-op
proposals; track churn/rework; allow "adequate; no change needed."
**Status:** proposed. **Route:** A. **Domain:** product.
**Evidence:** the current app refuses exact no-ops and flags repeats; Wikipedia's editing policy and ownership
guidance show the endless-rewording failure; the TS MVP's caps were an earlier attempt.
**Downside:** may entrench errors or bias; "stable" can become ownership; contributors may feel shut out.
**Reversal:** keep an appeal path and periodic re-review; if stable articles drift stale, shorten the stability
window. Revisit after 6 months or a disputed stability decision.

### D-16 — Split/merge

**Recommendation:** explicit `split_topic`/`merge_topic` proposals with scope statements, coverage checklists,
redirects and assertion mapping; preserve IDs and history.
**Status:** proposed. **Route:** A. **Domain:** product.
**Evidence:** Wikipedia summary style/merges; the TS prototype has topic merge schema but no behavior; the
workshop now has only the minimal M0 topic object (no scope/coverage or merge behaviour).
**Downside:** complex review; redirect/ID management; disputes about scope.
**Reversal:** start with manual steward decisions recorded as proposals; automate later. Revisit after 20
split/merge cases.

### D-17 — Review roles

**Recommendation:** separate `factual`, `source`, `coverage`, `readability`, `policy`, `translation`, `community`;
each review records scope and reasons; aggregation is deterministic and not a decision.
**Status:** proposed. **Route:** A. **Domain:** product.
**Evidence:** the current panel has fact_check/citation/readability/skeptic, which conflates source quality and
framing; Wikipedia separates content policies, noticeboards and ArbCom; the policy lab models roles.
**Downside:** more reviewers per proposal; coordination cost; role confusion.
**Reversal:** start with factual + source + coverage for standard/high; keep readability for all; add roles as
capacity allows. Revisit after 50 proposals.

### D-18 — Reviewer independence

**Recommendation:** factual reviewers should be on different models/providers where possible; record model,
provider, evidence packet hash and relationship to author; treat same-model roles as correlated; do not claim
independence without evidence.
**Status:** proposed. **Route:** A + B (measure correlation). **Domain:** product.
**Evidence:** the policy lab's one-model panel (correlation 0.85) escapes 44.2% of standard defects; mixed panel
(0.30) escapes 22.3%; the live runs used one model for all roles. This is the lab's main finding, but the
catch rates are assumptions.
**Downside:** cost and availability of diverse models; cross-provider evidence packets may differ; complexity.
**Reversal:** if cross-model review is too costly, use same-model review only for cosmetic/low and require human
review for standard/high. Revisit after measuring actual catch rates.

### D-19 — Launch publication policy

**Recommendation:** `human-gate-v0` — a **tiered review minimum** at launch: low/standard = 1 role review
(factual or source) + human publisher; high/contentious = 2 reviews (factual + source/policy) + publisher;
cosmetic = 1 lightweight review + sampled audit. Objections block. No automatic publication. The universal
two-review rule is a target for a larger reviewer corps, not a launch requirement.
**Status:** accepted direction (human review at start) + proposed policy detail. **Route:** A. **Domain:**
governance.
**Evidence:** the current default policy is min 2 reviews, block on objection, staff publish; the policy lab
shows no safe autonomy cell with the current panel; the decisions say human review at the very start. Hoax data
supports review at creation (90% caught within an hour, R2), but the same speed is implicated in newcomer
retention collapse, and a solo steward cannot staff two reviews on every edit. The tiered minimum is a
resourcing compromise, published as such.
**Downside:** lower-risk edits get one reviewer; a single reviewer can miss a defect; the tier boundary is a
judgment.
**Reversal:** policy versions are reversible; raise to two reviews for standard once capacity exists; tiered
autonomy only after D-20. Revisit when review capacity and measured catch rates support a change.
**Implementation note (2026-11-05):** all proposal transitions now pass through the D-41 evaluator, but the
published review minimums, objection blocking and human-publisher rule are **unchanged**; D-41 is the mechanism,
not a revision of this policy.

### D-20 — Autonomy

**Recommendation:** no auto-publication at launch. Run a shadow-mode evaluation: compute what would have
auto-published, compare to human decisions, measure false-approval and escape rates; only then consider a
tiered policy for cosmetic/low with audit.
**Status:** experimental. **Route:** B. **Domain:** governance.
**Evidence:** policy lab v1; the existing low-risk policy is proposal-only; no measured false-approval data
exists.
**Downside:** slower; may never be safe; opportunity cost.
**Reversal:** any autonomy policy is a `PolicyVersion` with a kill switch and audit sampling. Revisit after the
shadow experiment meets a published threshold (e.g., false-approval ≤ 1% over ≥ 500 edits, with confidence
interval).

### D-21 — Appeals

**Recommendation:** 14-day window; written grounds; at launch **one uninvolved adjudicator** with public
reasons; a 3-person panel with no original decision-maker once there are ≥30 active contributors. Outcomes
uphold/reverse/remand/modify; one appeal per decision, new-evidence exception. At launch the adjudicator is
advisory unless Justin adopts binding appeals in writing.
**Status:** proposed. **Route:** A. **Domain:** governance.
**Evidence:** Wikipedia dispute resolution/ArbCom and unblock appeals show the need for an independent body;
the current app has no appeal path.
**Downside:** panel time; inconsistent standards; gaming; delay.
**Reversal:** start with a single appeals reviewer + steward review; move to a panel as volume grows. Revisit
after 20 appeals or the first appeal controversy.

### D-22 — Disputes

**Recommendation:** structured disputes about assertions, terminology, scope or weight; separate from conduct;
positions with evidence; article states weight of evidence; dispute page persists.
**Status:** proposed. **Route:** A. **Domain:** governance.
**Evidence:** Wikipedia dispute resolution and talk-page practices; the TS prototype has dispute pages; the
workshop has none.
**Downside:** forums can become toxic; time; false balance risk.
**Reversal:** restrict disputes to assertions with at least two sources; close/archive with reasons. Revisit
after 10 disputes.

### D-23 — Identity

**Recommendation:** durable accounts for humans, agents, organizations; rotatable credentials; verification
levels with methods; observed/self-declared/verified metadata; topic-scoped track record; no global trust score.
**Status:** accepted direction (durable accounts, keys not identity) + proposed detail. **Route:** A. **Domain:**
product + governance.
**Evidence:** `DECISIONS.md` identity answers; the current `Agent`/`AgentCredential`/`AgentRun` model; Wikipedia
sockpuppetry/meatpuppetry experience shows identity is not independence.
**Downside:** verification friction; privacy; exclusion; false sense of security.
**Reversal:** start with contact verification + optional org verification; add identity verification only where
needed (BLP/legal). Revisit after the first abuse incident or privacy review.
**Implementation note (2026-11-05):** `ContributorProfile` trust levels (`new`/`standard`/`trusted`/`steward`)
are editorial capability tiers enforced by D-41; they are **not** verification levels, real-name checks or a
reputation score, and do not answer this decision's identity questions.

### D-24 — Sybil/coordination

**Recommendation:** behavioral clustering (operator, source overlap, timing, text similarity) **plus
review-graph monitoring** (reviewer–author pair frequency, approval-rate deviation, assignment diversity,
rotation), rate limits, additional review, campaign labels, suspension for inauthentic behavior, human review,
appeal. Do not infer coordination from agreement alone; do not claim a specific attacker cost that the research
has not measured.
**Status:** proposed. **Route:** A + B (simulation). **Domain:** governance.
**Evidence:** Wikipedia sockpuppetry/meatpuppetry/canvassing policies and investigations; the decisions
explicitly ask for sybil/collusion limits; the current app has no clustering.
**Downside:** false positives; privacy; adversarial adaptation; resource cost.
**Reversal:** start with transparent heuristics and human decisions; no automated bans. Revisit after a
coordinated campaign exercise.

### D-25 — Quotas

**Recommendation:** start in the ranges in §6.10 (new human 1–2 proposals/day; new agent 1–2; established
5–10; trusted 20–30; burst 3/min); calibrate to **measured reviewer-hours**, not headcount; publish the
parameters and the weekly review-hour budget.
**Status:** proposed. **Route:** B. **Domain:** governance.
**Evidence:** the current app has no quotas beyond job budgets; the TS prototype had daily quotas; platform
practice (GitHub/Wikimedia API etiquette) supports explicit limits. Review capacity is concentrated: English
Wikipedia has 887 New Page Reviewers but the top ~100 logged ~77,600 actions in 30 days, and one account logged
21,658 article reviews in a year (~59/day); the unreviewed backlog was 31,105 on 2026-09-01 (R2). Quotas must be
set against active reviewer time, not headcount.
**Downside:** too tight loses contributors; too loose floods review; gaming.
**Reversal:** quotas are policy parameters; adjust monthly. Revisit after 4 weeks of measured review demand.

### D-26 — Admission control

**Recommendation:** expected review demand ≤ 80% of measured weekly capacity; waitlist/application for public
beta; pause onboarding before lowering review quality; circuit breaker at 2× backlog.
**Status:** proposed. **Route:** A. **Domain:** governance.
**Evidence:** Wikipedia pending-changes trial and editor-decline research show review capacity and newcomer
handling are decisive; Nupedia's slow review is a cautionary case; the project is solo-stewarded.
**Downside:** slower growth; exclusivity perception; missed contributors.
**Reversal:** raise/lower the threshold with measured capacity. Revisit monthly during beta.

### D-27 — API

**Recommendation:** public read API with ETags/cursor pagination; scoped write API with `Idempotency-Key` and
`If-Match` base hash; async jobs; no publish endpoint; stable error codes; OpenAPI; MCP facade later.
**Status:** proposed. **Route:** A. **Domain:** product.
**Evidence:** the current API has read/research/propose/review with token auth and no publish; RFC 9110 defines
`ETag`/`If-Match` and `412` for a failed precondition; the IETF `Idempotency-Key` draft specifies `409` for an
in-flight duplicate, `422` for key reuse with a different payload, and a published expiry policy; `429` with
`Retry-After` is RFC 6585. MediaWiki's `baserevid` shows conditional writes in practice (R3). `core/api.py` has
none of this today — the largest gap for outside callers.
**Downside:** design/maintenance; abuse; versioning.
**Reversal:** keep v1 read-only if write abuse is high; add write later. Revisit after 5 API consumers.

### D-28 — Concurrency

**Recommendation:** optimistic base checks; one draft per article for v1; proposal branches + three-way merge at
block/claim level for multi-contributor; no silent CRDT merge of factual disagreements; stale proposals refused.
**Status:** proposed. **Route:** A + B. **Domain:** product.
**Evidence:** current `save_draft` version check and stale publish refusal; Git/CRDT patterns show merge is
possible but semantic conflicts need humans.
**Downside:** merge UI complexity; lost work if conflicts are frequent.
**Reversal:** if conflicts are rare, keep the simple model; add branching only when measured. Revisit after 10
concurrent-edit incidents.

### D-29 — Search

**Recommendation:** SQLite FTS5 + filters first; evaluate recall@3/MRR on a query set; add dedicated search or
hybrid/embeddings only when needed; always return citations/revision IDs.
**Status:** proposed. **Route:** A + B. **Domain:** product.
**Evidence:** current library search is title/opening `icontains`; SQLite FTS5 is built-in; the TS prototype had
no search; MediaWiki CirrusSearch shows faceted search at scale.
**Downside:** relevance; multilingual tokenization; operational cost.
**Reversal:** start with FTS5; keep the index rebuildable. Revisit when recall@3 < 80% or latency > 500ms.

### D-30 — Licensing and exports

**Recommendation:** articles CC BY-SA 4.0; **CC0 for identifiers, schemas and fact templates, not verbatim
prose extracted from CC BY-SA articles**; source snapshots retained for verification but not
bulk-redistributed; API terms with attribution/rate limits; counsel review before public exports.
**Status:** accepted 2026-11-04 (subject to counsel) — the recommendation above was accepted; counsel review, and
therefore public exports and API redistribution, are still outstanding (see
[Decision updates — 2026-11-04](#decision-updates--2026-11-04)). **Route:** D (legal/identity) + C (critique).
**Domain:** legal.
**Evidence:** Wikimedia Terms of Use and CC licenses; the decisions say "base knowledge open and portable" but
do not choose a license; source snapshots may be copyrighted. CC BY-SA 4.0 requires creator identification,
copyright and license notices, a URI, and indication of modification; §4 extends share-alike to a database
containing a substantial portion of the contents — but not its individual contents. ODbL distinguishes a
"Produced Work" (notice only) from a "Derivative Database" (must stay ODbL) (R3). Licensing cannot be
retrofitted; it must be chosen before public exports.
**Downside:** CC BY-SA limits some commercial reuse; CC0 may reduce reciprocity; snapshots create legal risk.
**Reversal:** licenses are hard to reverse for published content; choose before public launch. Revisit with
counsel.

### D-31 — Reproducibility

**Recommendation:** record config snapshot, model/provider/version, prompt/template hash, source snapshot
hashes, seed, cost; store review evidence packet hash; build a replay tool; pre-register experiments.
**Status:** proposed. **Route:** A. **Domain:** product.
**Evidence:** current `Job.config_snapshot` and `AgentRun` usage; the policy lab is deterministic per seed; ACM
artifact badging/NeurIPS checklist show the norm.
**Downside:** storage; complexity; model drift makes exact replay impossible.
**Reversal:** start with recorded inputs + output hash; add replay for high-risk jobs. Revisit after the first
replay audit.

### D-32 — Operations

**Recommendation:** SQLite WAL + single worker for beta; nightly backups + WAL streaming; weekly automated
restore check + quarterly full restore drill; cost caps/alerts; incident runbook; status page; moderation
workload tracking.
**Status:** proposed. **Route:** A. **Domain:** product.
**Evidence:** current stack and job model; SQLite WAL/Litestream; Wikimedia/GitHub postmortem practice; the
factory notes flag backup/restore as a commissioning gap.
**Downside:** single point of failure; solo on-call; cost.
**Reversal:** move to Postgres/object storage when triggers hit (D-32 scale path). Revisit after beta load
measurements.

### D-33 — Prompt injection

**Recommendation:** treat all source text as untrusted data; delimit; no tools for writer/reviewer; application
fetches sources; schema validation; no secrets; red-team; incident process.
**Status:** accepted direction (implemented in prompts/intake) + proposed hardening. **Route:** A. **Domain:**
product.
**Evidence:** `core/prompts.py` SAFETY block and `core/research.py` intake; OWASP LLM01 and NIST AI 100-2.
Indirect prompt injection is structural: Greshake et al. show LLM applications blur data and instructions and
demonstrate remote attacks against real systems; spotlighting and CaMeL reduce attack success in benchmarks,
but the 2023 assessment that effective mitigations are lacking has been narrowed, not refuted in deployment (R2).
**Downside:** no defense is complete; over-restriction limits useful research.
**Reversal:** keep least privilege; add tools only with sandboxing and review. Revisit after a red-team exercise.

### D-34 — Governance authority

**Recommendation:** founder-stewarded now, with published rules and a stated transition to a foundation and
eventually community governance; do not pretend decentralization before the model works.
**Status:** accepted 2026-11-04 — the published-trigger approach is accepted; a foundation can wait and may be
created earlier, and **no foundation is created now** (see
[Decision updates — 2026-11-04](#decision-updates--2026-11-04)). **Route:** D + E. **Domain:** governance.
**Evidence:** `DECISIONS.md` operating model; Wikimedia movement governance/UCoC as a reference, not a template.
**Downside:** legitimacy concerns; founder bottleneck; unclear path.
**Reversal:** publish a transition trigger (e.g., 3 years or 10k active contributors) and a draft charter.
Revisit at public beta and annually.

### D-35 — Policy lifecycle

**Recommendation:** versioned policies; public proposal/comment/decision; reasons and dissent; effective dates;
6-month review; emergency clause with 7-day ratification.
**Status:** proposed. **Route:** A. **Domain:** governance.
**Evidence:** Wikipedia RfC/policy proposal processes; Wikimedia UCoC; the current `ConfigVersion` policy kind.
**Downside:** slow; capture; low participation.
**Reversal:** start with a lightweight written process; formalize as volume grows. Revisit after 2 policy
changes.

### D-36 — Seed corpus

**Recommendation:** public launch corpus = **5–8 topics in one narrow, citation-costly domain** (a regulated
technical domain, methods/statistics, or an ecosystem's operational knowledge), with a named expert reviewer.
The 12-topic capability matrix is for internal fixtures and `/sandbox`, not the public corpus. Hypothetical
company/person cases are `/sandbox`-only, excluded from search/exports.
**Status:** accepted direction 2026-11-04 (real subjects, not hypothetical; hypothetical company/person cases stay
in `/sandbox`); the specific wedge/subject list is still open. The D-12 launch limit on real living-person/company
content is unchanged and remains a dependency (see [Decision updates — 2026-11-04](#decision-updates--2026-11-04)).
**Route:** A (with Justin input on the domain). **Domain:** product.
**Implementation note (M0):** the real-subject direction exists only as **3 demonstration topics** seeded in the
local database; no public seed portfolio, expert reviewer or wedge has been chosen. Do not read the demo topics as
a seed-corpus decision.
**Evidence:** R3 recommends a domain where being wrong has a cost, a few identifiable experts exist, and sources
are open enough to cite; a broad sampler competes with Wikipedia on its strongest ground. The current demo corpus
is narrow and sometimes fictional.
**Downside:** narrow corpus may not generalize; a wedge may be too small; real subjects create legal/PR risk.
**Reversal:** expand from the wedge after the trust loop is measured. Revisit after reader interviews and the
first external citations.

### D-37 — Launch stages and public beta timing

**Recommendation:** dogfood → private alpha → public read/correct → public contribute → expansion; gate each on
observable readiness criteria (spec §9.4). **Do not set a public beta date until the readiness criteria are met**;
the date is a commitment decision for Justin.
**Status:** accepted 2026-11-04 for the stage order and gating — private alpha with friends/advisors first, then a
gated public beta; **timing is still open and no public beta date is set** (see
[Decision updates — 2026-11-04](#decision-updates--2026-11-04)). **Route:** A + D. **Domain:** product.
**Evidence:** Nupedia/Citizendium/Knol outcomes; Wikipedia growth/editor decline; the project's solo capacity.
**Downside:** slow; opportunity cost; momentum.
**Reversal:** stages are reversible; do not skip the review-capacity gate. Revisit at each gate and before any
public announcement.

### D-38 — Usefulness metrics

**Recommendation:** four primary metrics with n and baseline: external citation durability, p90 correction
latency, review-hour ratio, reader task success (≥24 participants). Supporting indicators only; no article
count, edits/day, tokens, launch-week visitors, or self-selected survey return as gates.
**Status:** proposed. **Route:** A + B. **Domain:** product.
**Evidence:** platform growth research; the current app has no reader metrics; the policy lab measures review
load.
**Downside:** measurement cost; privacy; Goodhart risk.
**Reversal:** start with a small set (task success, correction time, review backlog, citations); add as needed.
Revisit after beta.

### D-39 — Languages

**Recommendation:** defer full multilingual support; pilot one language with a named reviewer. A translation is
a **view of a source revision** until a fluent reviewer promotes it to a reviewed **language edition** (an
article with its own revisions and review, sharing topic/assertion IDs). Reading levels are views over one claim
base. Label machine translation; record the modification ratio.
**Status:** deferred. **Route:** E. **Domain:** product.
**Evidence:** WikiProject Medicine translation and Simple English; Content Translation's modification-ratio gate;
the decisions defer language governance; the current app has no language field. (R1)
**Downside:** missing readers; inconsistent facts; review cost.
**Reversal:** pilot after the English anchor corpus is stable. Revisit when a language partner/reviewer is
identified.

### D-40 — Personalization

**Recommendation:** presentation-only personalization (font, density, saved topics, language); transient
explanations with citations; no personalized facts; no published variant per reader.
**Status:** proposed. **Route:** A. **Domain:** product.
**Evidence:** the decisions mention reading levels/personalized explanations as open; the risk is silently
changing the factual basis; the view contract applies.
**Downside:** less "magic"; users may expect personalization.
**Reversal:** add a reading-level view if readers ask, with review. Revisit after reader research.

### D-41 — Authorization and editorial state machine

**Recommendation:** keep one small, deterministic evaluator (`core/authorization.py`) as the only place that
answers "is this transition legal for this actor now?" — capability/trust table, derived proposal states, ordered
checks (state → capability → relationship → quota → policy), explicit reason codes, rolling 24-hour quotas, and
self-review / self-decision / self-publication guards. Capability tiers are editorial capacity, **not identity
verification, expertise or a reputation score**.
**Status:** accepted direction + **implemented v1 (2026-11-05)**; quota numbers are starting parameters, not
measured, and calibration/promotion rules are open (see
[Implementation update — 2026-11-05](#implementation-update--2026-11-05-authorization-state-machine-and-human-review-dashboard)).
**Route:** A + B (quota calibration). **Domain:** product + governance.
**Evidence:** the workshop previously used scattered `is_staff` checks and had no single answer for state,
transition legality or quota; the policy lab and review-capacity evidence (R2) motivate quotas; the
[design note](AUTHORIZATION-STATE-MACHINE.md) is the readable transition table. The 2026-11-05 slice enforces it in
`open_proposal`, `submit_draft`, `save_draft`/`ensure_draft`, `record_review`, `decide`, `publish` and `revert`,
with 171 tests (17 new).
**Downside:** a new place that can drift from the prose spec; quotas may frustrate legitimate contributors; the
`created_by` authorship test is conservative but incomplete; same-agent reviews remain non-independent.
**Reversal:** tables are policy parameters and versioned code; lower or raise a tier/quota without schema change.
Revisit after E2/E3 and 4 weeks of measured review demand. If the evaluator and the design note disagree, the note
and the code must be reconciled in the same change.
**Explicitly distinct from:** D-19 (the publication policy minimums are unchanged and still a proposed policy) and
D-23 (this is capability, not identity verification). The slice does not define a new review minimum.

### D-42 — Human review dashboard

**Recommendation:** a shared human queue at `/review/` (any `standard`/`trusted`/`steward` actor) that shows
submitted, under-review, approved-awaiting-publish, changes-requested and stale approvals, with review coverage by
role, visible objections, origin, age and filters; actions are rendered only when the evaluator allows them and
rechecked server-side. No auto-assignment and no implied ownership. The proposal page adds a human review form that
records the reviewer.
**Status:** accepted direction + **implemented v1 (2026-11-05)**. **Route:** A. **Domain:** product + governance.
**Evidence:** review capacity is the binding constraint (R2); reviewers had no single place to see what needs a
human now; the dashboard is a view over authorization decisions, not a second permission system. Implemented with
`/review/` and templates; 171 tests (17 new).
**Downside:** a shared queue can be ignored (no assignment); coverage signals are only as good as the role list;
reviewer workload is visible only for the current reviewer's last 7 days.
**Reversal:** it is a view plus routes; remove or redesign without data loss. Revisit when assignment/claiming or
per-reviewer calibration is built (both explicitly not in v1).



### D-43 — M0 remainder: permalink, claim resolver, license, search, backup, idempotency

**Recommendation:** finish M0 with explicit, small mechanisms rather than a larger object model:
- **Permalink:** `/article/<slug>/r/<n>/` is the canonical public URL for a published/superseded revision; the
  citation carries revision id, content hash, licence and access date. Drafts stay login-only.
- **Claim resolver:** `/claims/<uuid>/` (HTML) and `/api/v1/claims/<uuid>/` (token JSON) always resolve the named
  occurrence, return `resolution` (`current`/`superseded`/`unpublished`) and `valid_to`, and link the current
  revision. Claim ids remain revision-bound; no merge/alias map or `claim_key` until M2.
- **License:** `Article.license` defaults to CC BY-SA 4.0 (D-30, subject to counsel), with `attribution`;
  `Source.license`/`attribution`; and `PublicationEvent.license` records the licence in force at publication so a
  later relicensing does not rewrite history.
- **Search:** `SearchDocument` + external-content FTS5 triggers; only published articles are indexed; `/search/`
  shows BM25 rank, match fields and a plain snippet; `rebuild_search`/`check_search` repair and verify.
- **Backup:** `scripts/backup.sh` uses the online backup API and writes a checksum/row-count manifest;
  `scripts/restore_drill.sh` verifies a restore in a temp dir. Local-only, unscheduled; not disaster recovery.
- **Write API:** `Idempotency-Key` required on proposal/review/research writes; completed duplicates replay, an
  in-flight duplicate is `409`, key reuse with a different payload is `422`; keys expire after 24h. `If-Match` is
  required on agent proposal writes (`428` missing, `412` stale with current revision). Reads use ETag/304.
**Status:** **implemented v1 (2026-11-05)**; 190 tests. **Route:** A. **Domain:** product + ops.
**Evidence:** the M0 ladder and the technical research on permalinks, FTS5 drift, conditional writes and
idempotency; implementation is in `core/licensing.py`, `core/search.py`, `core/idempotency.py`, migrations
`0010`–`0012`, templates, and `scripts/`. The backup drill is recorded in [OPERATIONS.md](OPERATIONS.md).
**Downside:** claim ids do not survive a revision (a downstream citation to a claim is tied to that revision);
FTS5 is single-language and can drift if bypassed; backups are local and manual; idempotency covers the JSON API,
not web forms; the license defaults are not counsel-approved.
**Reversal:** each piece is separable. Removing search is dropping a derived table; removing idempotency is
removing the wrapper; license fields can be left unused without changing publication history. Do not retroactively
rewrite a `PublicationEvent.license`.
**Revisit:** M2 adds `claim_key`/change diffs and a merge/alias map; multilingual search and off-host/scheduled
backup are separate; E6 (retry storm) should test the API contract before public write access.

---

## Decisions requiring Justin

| ID | Question | Why it is his | What can proceed without it | Answered 2026-11-04 |
|---|---|---|---|---|
| D-01 | Name: Galactica vs T5/t5.wiki | Identity/brand; irreversible-ish | Everything; use working name | Partly: keep Galactica as working name; T5 short-listed; no rename; final name still open |
| D-30 | Licensing: CC BY-SA + CC0? | Legal/irreversible; affects reuse/funding | Internal content; no public exports | Yes: recommendation accepted, subject to counsel |
| D-34 | Governance transition: when/how | Values/authority; major commitment | Current steward model; draft charter | Yes: published-trigger approach accepted; foundation deferred, not created |
| D-36 | Real vs hypothetical seed subjects | Risk appetite/PR/legal | Hypothetical cases; ordinary topics | Partly: real subjects, hypothetical cases stay `/sandbox`; wedge list open |
| D-37 | Public beta timing/identity | Commitment/spending | Private alpha; readiness work | Partly: private alpha then gated public beta; no date |

These answers are recorded in full, with their open remainders, in
[Decision updates — 2026-11-04](#decision-updates--2026-11-04). The three open questions from the same review are
listed there and are **not** decisions. D-41 and D-42 are not Justin-decisions: they are accepted direction with
an implemented v1 and open calibration questions recorded in
[Implementation update — 2026-11-05](#implementation-update--2026-11-05-authorization-state-machine-and-human-review-dashboard).

**AI critique (route C) candidates:** D-08 view contract, D-18 independence, D-19/D-20 publication policy,
D-24 sybil, D-30 licensing. Reviews are advisory and should be independent before synthesis; preserve dissent.

---

## Decisions reserved for the future community

The assignment asked to distinguish decisions about **building the product** from **governance decisions its
future community would make**. These are not Justin's to settle unilaterally, and they are not the AI's to
ratify. The current steward can set an interim rule under the published policy process; the long-term authority
belongs to the community/foundation that the project intends to become.

| Question | Interim authority (now) | Future authority | Why it is reserved |
|---|---|---|---|
| Which sources are reliable for a topic | Reviewers under the source policy | Topic community / noticeboard | It is a recurring, argued judgment; a fixed list would freeze bias |
| What topics are in scope / how to name them | Topic steward + scope policy | Topic community + language community | Scope and naming are community preferences, not facts |
| Who becomes a reviewer/admin | Steward appointment against published criteria | Community election/confirmation | Authority over the review layer must be accountable to it |
| What sanctions are proportionate | Moderator + appeals panel | Community conduct policy / independent panel | Sanctions are coercive; they need a legitimate process |
| Which languages launch and who reviews them | Steward + named reviewer | Language community | Language governance was explicitly deferred |
| How policies change | Policy steward with comment period | Community consensus / foundation board | The policy process is the constitution, not a product feature |
| How the project decentralizes | Founder/foundation | Foundation board + community | A major, irreversible identity commitment |
| Commercial API / funding model | Justin/foundation | Foundation board | Spending and mission tradeoffs are fiduciary |
| Content license changes | Justin + counsel | Foundation board + community | Retroactive license changes are not possible for copies already made |

**What AI may not decide:** the name, licensing, governance transition, sanctions, whether a real person/company
is a subject, or whether a policy is legitimate. AI can draft, critique, summarize, run experiments and propose
reviews. Multiple instances of one model are not independent evidence and do not constitute community consent.

**What the 2026-11-04 passes did and did not do:** the statuses changed in
[Decision updates — 2026-11-04](#decision-updates--2026-11-04) record answers **Justin gave himself** in the product
review; nothing else was ratified on his behalf. The decision-update pass did not treat his silence on any other
item as consent and did not promote the three open questions (OQ-1, OQ-2, OQ-3) into decisions. The **separate M0
implementation pass** implemented only `PublicationEvent`, the minimal `Topic` + `Article.topic`, `Watch` and the
reader surfaces listed above. `accepted` status is used only for Justin's dated answers, earlier dated decisions, or
implemented behavior.

**What the 2026-11-05 pass did:** it implemented the D-41/D-42 authorization/state-machine/review-dashboard slice
(171 tests; 17 new) and recorded its open calibration questions. A second 2026-11-05 pass implemented the M0
remainder (D-43; 190 tests) and prepared the E1/E4 kits. It did not change D-19 or D-23, did not ratify anything
on Justin's behalf, did not run human experiments, and did not complete any M1+ item. No other decision status
changed.

