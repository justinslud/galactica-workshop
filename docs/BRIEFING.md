# Briefing for Justin

**Date:** 2026-11-04. **Prepared by:** research and product lead.
**Updated:** 2026-11-04 — your answers from the product review are recorded in
[Decision updates — 2026-11-04](DECISION-REGISTER.md#decision-updates--2026-11-04) and summarised at the end of
this briefing. **2026-11-05:** the authorization/state-machine and human review dashboard slice is implemented
(171 tests); see the implementation update at the end and [the design
note](AUTHORIZATION-STATE-MACHINE.md).
**What this is:** the short version. The full material is in [the spec](PRODUCT-SPEC.md), [decision
register](DECISION-REGISTER.md), [worked examples](WORKED-EXAMPLES.md), [experiments](EXPERIMENTS.md),
[launch plan](LAUNCH-PLAN.md), [current-state assessment](00-CURRENT-STATE.md) and [research notes](research/).

---

## The short version

The project has a working editorial loop and a credible evidence model. It does **not** yet have the product
surface that would make a reader choose it, the review capacity to accept agent-scale contribution, or the
operational pieces (publication history, API idempotency, backups, licensing) that a public reference needs.
The biggest risk is not content generation. It is **review capacity and correction credibility**. The revised
launch is deliberately narrower than the first draft: **5–8 anchor topics in one citation-costly wedge**, not
12–20 showcase topics.

Three findings changed my recommendations:

1. **Clarity beats provenance with readers, and citations are rarely clicked.** Readers rate clarity (4.43) and
   structure (4.37) above reference counts (4.06/3.97), and about 0.29% of page views produce a reference click
   (R1). The design should be clarity-first with evidence one step away, not an evidence-first article with a
   reading layer.
2. **Showing raw process can lower measured quality judgements** even while readers say it raises trust; a
   resolved conflict removes the penalty (R1). Disagreement should be shown as **adjudication**, not as the raw
   talk thread.
3. **Review capacity is the binding constraint, and review value decays fast.** 90% of ever-detected hoaxes are
   caught within an hour; Wikipedia has 887 New Page Reviewers but one account logged 21,658 reviews in a year;
   German Wikipedia runs sighted revisions on 99.99% of articles while English uses pending changes on under
   0.05% (R1, R2). We cannot open contribution faster than review.

Two findings changed the architecture:

4. **A permalink is not a reproduction.** MediaWiki guarantees only main text; templates and images render live.
   Every derived view needs a manifest (base revision, hash, claim IDs, generator, reviewer, `as_of`,
   staleness). This is the highest-consequence product addition (R3).
5. **Publication history needs an append-only event.** The `Article.published` pointer was overwritten
   on every publish, so "what was published on date X" was lost; `PublicationEvent` became the first
   implementation slice and is now implemented at M0 (2026-11-04) (R3).

## What is supported by evidence vs still proposed

**Supported by evidence (external research + the existing app):**
- The reader task split and the low citation click-through (R1).
- The process-transparency penalty and the value of resolved conflict (R1).
- Review-at-creation value and capacity concentration (R1, R2).
- Technical sybil detection weakness and the review-pipeline attack (R2).
- Permalink/reproduction limits, ETag/idempotency patterns, backup failure modes, licensing constraints (R3).
- The existing app's immutable revisions, claim-level evidence, stale-base refusal, revert-as-new-revision and
  audit trail, plus the M0 append-only publication history, minimal topic pages, byline/credit page and watchlist,
  and the 2026-11-05 authorization evaluator and human review queue (verified by 171 passing tests — 154 before
  the authorization slice, 133 before M0 — and code reading).

**Proposed (not decided, reversible):**
- Article-first with stable assertions as support (D-02/D-05).
- The view contract and manifest (D-08).
- The topic object and scope/coverage model (D-03).
- Review roles and independence requirements (D-17/D-18).
- Human gate at launch, shadow-mode autonomy later (D-19/D-20).
- Correction, dispute and appeal procedures (D-13/D-21/D-22).
- Quotas and admission control (D-25/D-26).
- The API contract and ops plan (D-27/D-32). The licensing recommendation (D-30) is no longer proposed: it was
  accepted on 2026-11-04, subject to counsel.

**Still open / requiring you:** the final name (interim: keep Galactica, T5/t5.wiki short-listed), the specific
wedge and 5–8 anchor topics, and the public beta date. Licensing, the governance-transition approach, real-vs-
hypothetical seed subjects and the private-alpha → gated-public-beta order were answered on 2026-11-04 (see the
[decision updates](DECISION-REGISTER.md#decision-updates--2026-11-04) below and in the register). The claim-ledger /
claim-first design and authored-vs-generated views remain open questions, not decisions; deterministic authorization
now has an implemented v1 (D-41) with quota calibration and trust-promotion rules still open, and the human review
queue (D-42) has no auto-assignment.

## Important disagreements (preserved, not flattened)

- **Article-first vs claim-ledger-first.** The 2026-10-27 clarification says article-first; `docs/model.md` still
  says "claim ledger with page views." I recommend article-first, with assertions as stable support. The
  disagreement is real: an assertion-first product would be more reusable for agents but less readable.
- **Human gate vs agent review.** The decisions allow later agent review; the lab shows the current one-model
  panel is unsafe for autonomy. I recommend a human gate at launch and a shadow-mode experiment before any
  autonomy. A reasonable person could argue for a faster tiered policy for cosmetic edits; the evidence does not
  support it yet.
- **Open contribution vs admission control.** The mission implies broad participation; the capacity evidence
  implies gating. I recommend gating on review health and publishing the rule. This will feel slower than the
  mission promises.
- **Verification vs pseudonymity.** Durable accounts and optional verification improve accountability; strong
  identity requirements exclude contributors and are not supported by the sybil evidence. I recommend
  observed/self-declared/verified metadata, no global score.
- **Views: generate vs author.** Generated views are cheap but risk unreviewed facts; authored views are better
  but expensive. I recommend reviewed, pinned views with follow-through, starting with summary/timeline/table.
- **Name.** "T5" collides with a well-known model name; "Truth Attractor" overclaims a verifiability model.
  Galactica is generic but continuous. I have not decided this. (2026-11-04: working name retained, T5 short-listed,
  final decision deferred — see the decision updates.)

## What I recommend doing next

1. **M0 slice — partly done (2026-11-04): `PublicationEvent`, a minimal `Topic`, the byline/credit page and the
   opt-in watchlist are implemented and tested (154 tests, 21 new).** `PublicationEvent` is a correctness fix, not a
   feature; the byline and watchlist are the return loop the research says matters. **Remaining M0 work is still
   open:** stable permalink + claim resolver, license/attribution fields, SQLite backup + restore drill, FTS5,
   `Idempotency-Key`/`If-Match`, and a designed public (anonymous) full-history page.
2. **Run E1 (reader task success) and E4 (correction triage)** in parallel (2–3 weeks). These decide the reader
   surface and the correction SLA before more building.
3. **Run E2/E3 (review at creation; reviewer independence)** on the existing policy lab and live review runs.
   Do not propose autonomy until these produce measured catch rates. The 2026-11-05 human review queue records the
   reviewer, but same-agent reviews are flagged `same_agent` and are not independent evidence — exclude them when
   computing catch rates.
4. **Write the contributor/reviewer/correction/source/API docs** and run E13 (restore drill) and E14
   (accessibility audit). These are launch blockers.
5. **Pick the wedge and the 5–8 anchor topics** with you, then start the private alpha (the working name stays
   Galactica; the final name can wait until before public beta). Do not open
   public contribution until the review backlog is <1 week for 4 consecutive weeks and the review-hour ratio is
   ≤80%.

## Five consequential questions for you

Each has my recommendation, the alternative, the practical consequence, and what can proceed without an answer.
Your answers from the 2026-11-04 review are recorded under each question (and in the [decision
updates](DECISION-REGISTER.md#decision-updates--2026-11-04)); the remaining open questions are listed at the end.

### Q1 — Name: Galactica, T5/t5.wiki, or something else?

**Recommendation:** keep **Galactica** as the working name through private alpha; decide before public beta.
**Alternative:** adopt T5/t5.wiki now for distinctiveness.
**Consequence:** T5 collides with a well-known model name and "Truth Attractor" implies a truth claim the product
cannot support; Galactica is generic but continuous. A rename later touches branding, domains, docs and external
citations, but not the product model.
**Can proceed:** all content and engineering under the working name. **Needed by:** before public beta branding.
**Route:** D.
**Answer (2026-11-04):** keep Galactica as the working name ("Galactic Hub" was conversational, not an adopted
name); T5/t5.wiki stays on the short list; no repository rename; the final name decision is still open and is due
before public beta.

### Q2 — Licensing: CC BY-SA 4.0 for articles + CC0 for structured data, or something else?

**Recommendation:** CC BY-SA 4.0 for articles, CC0 for structured assertions/data where legally sound, source
snapshots retained but not bulk-redistributed; counsel review before public exports.
**Alternative:** CC BY-SA for everything; or a more permissive article license.
**Consequence:** CC BY-SA §4 extends share-alike to databases built from a substantial portion of the content;
CC0 maximizes reuse but may reduce reciprocity; snapshots may be copyrighted. Licensing cannot be retrofitted.
**Can proceed:** internal content, private exports, schema license fields. **Needed by:** before public exports
or API redistribution. **Route:** D + counsel.
**Answer (2026-11-04):** recommendation accepted — CC BY-SA 4.0 for articles, CC0 for identifiers/templates (not
verbatim prose), subject to counsel. Counsel review, and therefore public exports and API redistribution, is still
outstanding.

### Q3 — Governance: founder-stewarded now, foundation later — when and how?

**Recommendation:** publish a transition trigger (e.g., 3 years or a defined contributor/usage threshold) and a
draft charter at public beta; do not pretend decentralization before the model works.
**Alternative:** incorporate a foundation earlier; or stay founder-stewarded indefinitely with published rules.
**Consequence:** early foundation adds legitimacy and cost; late transition risks capture and legitimacy debt.
**Can proceed:** steward model, published policies, appeals. **Needed by:** before Stage 3/public contribution.
**Route:** D.
**Answer (2026-11-04):** the published-trigger approach is accepted. A foundation can wait and may be created
earlier, but **no foundation is created now**; the steward model and published policies continue.

### Q4 — Seed subjects: real company/living-person cases, or hypothetical first?

**Recommendation:** public launch corpus = **5–8 topics in one citation-costly wedge**; hypothetical
company/person cases live in `/sandbox`; real living-person/company content is out of scope until a named
policy/legal reviewer and counsel exist.
**Alternative:** use real public companies/people to demonstrate the product's strength; or a broad 12-topic
sampler.
**Consequence:** a wedge gives a reader a reason to choose the site and an expert a reason to contribute; a broad
sampler competes with Wikipedia on its strongest ground. Real cases are more compelling but create legal/PR risk.
**Can proceed:** ordinary and historical topics in the wedge; hypothetical cases in `/sandbox`. **Needed by:**
before alpha content. **Route:** D (risk appetite + domain choice).
**Answer (2026-11-04):** use real subjects, not hypothetical ones; hypothetical company/person cases stay in
`/sandbox`; the specific wedge and anchor-topic list remains open. The D-12 limit on real living-person/company
content (a named policy/legal reviewer and counsel must exist first) is unchanged and still applies.

### Q5 — Public beta timing and identity: when do we open reading and corrections?

**Recommendation:** open public reading + correction intake after the private alpha meets the readiness criteria
(5–8 anchor-quality articles in the wedge, review backlog <1 week, review-hour ratio ≤80%, correction SLA
measured, restore drill passed, accessibility audit passed). Do not tie it to a date.
**Alternative:** open earlier for feedback; or stay private longer.
**Consequence:** earlier means more feedback but a higher chance of a public error or an unmanageable queue;
later means less momentum.
**Can proceed:** private alpha, docs, experiments, ops. **Needed by:** before public read. **Route:** D.
**Answer (2026-11-04):** private alpha with friends/advisors first, then a gated public beta; **no public beta date**
is set or implied. The readiness criteria above still gate the transition.

---

## Decision updates — 2026-11-04

What you answered in the product review, and what stayed open. The full record, with status tables and the detailed
entries, is in [the decision register](DECISION-REGISTER.md#decision-updates--2026-11-04).

**Accepted decisions**
- **Name (D-01, partly):** keep Galactica as the working name; you said your everyday label is "Galactic Hub",
  recorded as usage rather than a repository rename; T5/t5.wiki stays short-listed; the final decision is open.
- **Licensing (D-30):** CC BY-SA 4.0 for articles and CC0 for identifiers/templates (not verbatim prose) accepted,
  subject to counsel.
- **Governance transition (D-34):** the published-trigger approach is accepted; the foundation is deferred and is
  not created now.
- **Seed subjects (D-36, partly):** real subjects, not hypothetical; hypothetical company/person cases stay in
  `/sandbox`; the wedge and anchor-topic list is still open.
- **Public beta (D-37, partly):** private alpha with friends/advisors first, then a gated public beta; no date.

**Open questions — recorded, not decided**
- **OQ-1:** how an article-first article should reflect a claim ledger, and what claim-first would look like.
- **OQ-2:** deterministic/state-machine authorization and quota policy — weaker identity but lower privileges.
- **OQ-3:** whether views are authored or generated, and how visual views work.

The decision-update pass itself changed no code; the separate M0 implementation pass on the same date is below.

### Implementation update — M0 slice (2026-11-04)

A separate implementation pass landed **only the first M0 slice**:
- append-only `PublicationEvent` (per-article sequence; kinds `initial`/`publish`/`revert`/`import`; previous
  revision, policy version, decision, reason, content hash; unique per article+sequence and article+revision);
- a minimal `Topic` plus `Article.topic`, seeded with 3 demonstration topics;
- an opt-in `Watch` with `last_seen_at` (web-only digest, no email);
- reader surfaces: `/topics/`, `/topics/<slug>/`, `/contributors/<username>/` (public credit page, no private
  data), `/watchlist/`, the watch toggle and mark-seen endpoints, the article-page byline/topic/provenance block,
  and the history-page publication log;
- migrations `0006`/`0007`/`0008` (`0007` backfilled 6 existing publication events on the local DB; `0008` makes
  the publication event→article FK `PROTECT`, so deleting an article cannot erase its history).

154 tests pass (21 new, was 133); `manage.py check` and `makemigrations --check` are clean. The DB was migrated
locally; nothing was deployed and no browser-level check was run. **Not implemented in this slice — do not read
as done:** stable permalink / claim resolver, license/attribution fields, SQLite backup + restore drill, FTS5,
`Idempotency-Key`/`If-Match` (M0 remainder); correction intake, review tiers, full `Topic` scope/coverage (M1);
a designed public (anonymous) full-history page, email digest, `View`/`Assertion` objects (later). No M1+ item is
complete.

### Implementation update — 2026-11-05: authorization, state machine and human review dashboard

A second slice landed: `core/authorization.py` is one deterministic evaluator for capabilities and transitions —
trust levels (`new`/`standard`/`trusted`/`steward`), derived proposal states (`submitted`/`under_review`/`approved`/
`published`/`rejected`/`changes_requested`), explicit reason codes, rolling 24-hour quotas, and self-review /
self-decision / self-publication guards. `ContributorProfile` and `Review.reviewer` (migration `0009`) make the
reviewer a real actor; `open_proposal`, `submit_draft`, `save_draft`/`ensure_draft`, `record_review`, `decide`,
`publish` and `revert` all pass through the evaluator. `/review/` is the shared human queue (standard/trusted/
steward; `new` and anonymous denied) with state filters, counters, review coverage, objections and stale flags, and
the proposal page now has a human review form that records the reviewer.

Quotas are **starting parameters, not measured**: `new` 1 proposal/day and 0 reviews; `standard` 5/10; `trusted`
10/25; steward unlimited. Same-agent reviews are allowed but flagged `same_agent` and are not independent evidence.

171 tests pass (17 new in `core/tests/test_authorization_dashboard.py`, was 154); `check` and `makemigrations
--check` are clean; the migration was applied locally; no browser-level check was run. **Not implemented:**
auto-assignment, automatic trust promotion, an external policy engine, the `withdrawn` state, appeal/dispute state
machines, a trust-management UI beyond admin, per-reviewer calibration, and identity verification. The publication
policy minimums (D-19) and identity direction (D-23) are unchanged; the trust levels are capability, not identity.
D-41 and D-42 are recorded as accepted direction + implemented v1 with open calibration questions in the
[decision register](DECISION-REGISTER.md#implementation-update--2026-11-05-authorization-state-machine-and-human-review-dashboard).

## What I would not do yet

- Do not open public contribution or auto-publication.
- Do not build maps/charts/personalized explanations before the view contract and review capacity are proven.
- Do not launch a second language without a named reviewer.
- Do not rename the project or reorganize the repository as part of this pass.
- Do not treat the policy lab's assumptions as measured catch rates.
- Do not treat `ContributorProfile` trust levels as identity verification, expertise or a reputation score; they
  are editorial capability tiers.
- Do not use AI reviewers as ratification for governance decisions.
