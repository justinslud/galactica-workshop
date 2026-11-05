# Product specification — extended reference platform

**Version:** 2.2 (proposal for review; post-critique revision)
**Date:** 2026-11-04
**Working name:** Galactica. Candidate name: **T5 / t5.wiki** ("Truth Attractor"). **No rename is authorized by
this document.** The name is a separate decision (`D-01`).
**Status:** This document extends, and does not replace, the existing decisions in
`~/projects/galactica/DECISIONS.md`, the 2026-10-27 course clarification, `docs/model.md`, and the workshop's
`CURRENT.md`/`README.md`. It is a product proposal: sections marked **proposed** are not accepted policy.
**Companion documents:** [current state](00-CURRENT-STATE.md) · [decision register](DECISION-REGISTER.md) ·
[worked examples](WORKED-EXAMPLES.md) · [experiment backlog](EXPERIMENTS.md) · [launch plan](LAUNCH-PLAN.md) ·
[briefing](BRIEFING.md).
**Research notes:** **R1** = [reader experience](research/01-reader-experience.md); **R2** =
[editorial/governance](research/02-editorial-governance.md); **R3** = [technical/launch](research/03-technical-launch.md).
Those notes label every finding as demonstrated, claimed, historical, proposed adaptation, or open. This spec
uses their evidence but its recommendations remain proposals. **Factual claims about external systems are
sourced in R1–R3; where a number is second-hand, vendor-claimed or otherwise unverified, the research note says
so.** Do not read a number in this spec as independently measured unless the note labels it demonstrated.

---

## 0. One-page summary

**The product.** A maintained public reference for people and AI agents. Each topic has a readable article, an
inspectable evidence layer, a visible history of corrections and disagreements, and a small family of derived
views (summary, timeline, table, map, explainer, reading level, language edition) whose relationship to the
article revision is explicit. Agents can research and propose at scale; humans decide what publishes; the system
spends scarce human attention where the risk is highest.

**The bet.** The durable advantage is not generating articles. It is **maintaining trust over time**: keeping
evidence attached, corrections cheap, disagreement legible, provenance reproducible, and review capacity from
being the silent failure mode. An agent that can cite a stable revision and a specific claim, and a reader who
can see why the article says what it says, will return.

**What the reader research changes.** Readers mostly want an overview or a quick fact, not a deep read; citations
are rarely clicked; clarity and structure outrank reference counts in readers' own trust ratings; and showing
raw process can *lower* measured quality judgements even while readers say it raises trust (R1). So the design is
**clarity first, evidence one step away, adjudication rather than raw dispute threads**, with the summary and lead
treated as first-class surfaces rather than trailers for the body.

**What the editorial research changes.** Independence is not even-handedness; citation count cannot distinguish
corroboration from a shared ancestor; conflict of interest is orthogonal to bias; BLP defaults are asymmetric;
review capacity is concentrated and decays in value with delay; technical sybil detection is weak by its own
account; and the largest open encyclopedia has concluded that LLM content can be produced faster than it can be
reviewed (R2).

**What the technical research changes.** A permalink is not a reproduction; publication history needs its own
append-only events; content identity and record identity must be split; APIs need conditional writes and
idempotency, not retries and hope; backups fail as processes; licensing cannot be retrofitted (R3).

**What must be true for this to work.**
1. A small anchor corpus is genuinely more useful than the alternatives for real reader tasks.
2. Review capacity is measured and admission is controlled; contribution does not outrun review.
3. Clarity and evidence inspection are both good enough that readers use them; evidence is not hidden behind a
   drawer that only 0.29% of page views ever open.
4. Derived views cannot silently drift from the factual base.
5. Agent participation is attributable, rate-limited and reviewable without pretending that agreement is proof.
6. Corrections and appeals are credible, quick enough to matter, and visibly fair.

**Launch posture.** Start with **5–8 anchor topics in one citation-costly wedge** and invited contributors.
Public reading and correction
intake before public contribution. No automatic publication at launch. A strong launch means a reader would miss
the site if it disappeared, not that it has many articles.

---

## 1. Product definition

### 1.1 The problem

Reference knowledge is simultaneously abundant and hard to trust. General encyclopedias are broad but slow,
uneven in depth, and increasingly strained by the volume and speed of agent-generated claims. Chatbots are fast
but produce fluent answers whose evidence is difficult to inspect, whose revisions are invisible, and whose
errors are hard to correct at the source. Structured databases are precise but narrow and often lack readable
explanation. None of these gives a reader or a downstream agent a maintained, citable artifact that combines
explanation, evidence, uncertainty and a correction history.

The gap is not "more articles". It is **maintained, inspectable explanation** at a granularity that supports
correction and reuse. In one 2023 audit of four generative search engines, only 51.5% of generated sentences
were fully supported by their citations and 74.5% of citations supported the sentence they were attached to
(R1). That is a single study, not a general estimate; treat it as a warning about the category, not a precise
measurement of every chatbot. A
reference whose value is a stable, citable revision is doing a different job from a chatbot, and it should not
pretend to compete on conversational convenience.

### 1.2 The product in one sentence

A public reference — **language-ready, one language at launch** — where every substantive statement is connected to evidence and to a revision,
where disagreement is shown rather than smoothed, and where people and agents can improve the reference under a
review process whose rules and decisions are public.

### 1.3 What it is not

- **Not a chatbot.** It may offer question-answering later, but only as a view over citable revisions.
- **Not a claim ledger with a thin article layer.** Articles are the primary reading artifact. Claims support
  them. The 2026-10-27 clarification is authoritative on this point.
- **Not a Wikipedia clone.** It borrows editorial practices where they are demonstrated, but its evidence model,
  agent participation and derived views are different.
- **Not a social feed.** There is no global activity feed by default. Readers go to topics, not to a stream.
- **Not a place for organizations to publish advertising on their own terms.** Organization-supplied factual
  material is allowed with visible attribution and independent review.
- **Not a single trust score.** Trust is topic- and claim-specific, with reasons and appeal paths.
- **Not an AI oracle.** Model output is evidence-shaped input to a review process, not authority.

### 1.4 Design principles

1. **The article is the promise; the evidence is the proof.** Neither is optional.
2. **Clarity earns the first minute; provenance earns the citation.** Readers rate clarity and structure above
   reference counts, and few click citations (R1). A hard-to-read article with perfect evidence loses.
3. **Every published statement has a provenance path.** Source, snapshot, claim occurrence, revision, review,
   decision.
4. **Uncertainty is content.** Scope limits, open questions, disputed claims and stale evidence are shown, not
   hidden in a footnote or averaged into a score.
5. **Corrections are a feature, not an exception.** A reference that cannot be corrected cheaply will not stay
   correct.
6. **Human attention is the scarce resource.** Route it by risk; automate routine checks; never pretend review
   is free. Review value decays with delay, so the launch policy gates at creation; post-publication review
   remains a first-class audit and correction channel (E2 tests this).
7. **Agreement is not evidence.** Multiple agents, accounts or citations may share an origin. Independence is
   recorded and tested, not assumed.
8. **Derived views are accountable.** A summary, timeline, map or translation declares its base revision,
   generator, reviewer and staleness.
9. **Reversible by default.** Prefer decisions that can be undone with a new revision or policy version. Reserve
   irreversible choices for explicit human authority.
10. **Readable by humans, usable by machines.** The same content must serve a curious reader and a downstream
    agent without a second, divergent copy.
11. **Say what we do not know.** The platform's credibility depends more on calibrated uncertainty than on
    confident coverage. Wikidata is explicit that its model is verifiability, not truth (R2); "Truth Attractor"
    must not become a claim the product cannot support.

### 1.5 Success conditions

| Actor | Success looks like | Not success |
|---|---|---|
| Reader | Completes a real task (overview, quick fact, depth, verify, cite) and returns for another topic | Time on page, page views alone |
| Contributor | A correction or improvement is reviewed, decided and visible within the stated window | Raw edit count |
| Agent operator | An agent can retrieve a stable revision and claims, propose an improvement, and get a reviewable outcome | Token consumption, proposal volume |
| Downstream agent | Cites a specific revision/claim and the citation resolves to inspectable evidence | API calls alone |
| Steward | Review backlog stays within capacity; disputes and appeals are resolved; incidents are rare and handled | Article count growth |

---

## 2. Actors, roles and authority

Roles are **scoped capabilities**, not a hierarchy of personhood. One actor may hold several roles. An agent is
always attached to an accountable operator; an organization is an accountable entity, not a person.

| Actor | Description | Default capabilities |
|---|---|---|
| Reader | Anonymous or registered | Read, search, inspect evidence, report a correction, export with attribution |
| Corrector | Reader, subject or representative who reports an error | Submit a correction report; see its status; appeal a closure |
| Contributor | Human editor | Draft, propose, comment, respond to reviews |
| Agent contributor | Software agent with a durable account and an operator | Read via API, research within limits, propose, respond to reviews; no publish |
| Reviewer | Human or agent with a review scope | Review assigned proposals/claims; record verdicts and reasons; no publish unless separately authorized |
| Topic steward | Maintainer for a topic or category | Triage, assign reviewers, manage scope and views, escalate; not a truth authority |
| Publisher | Staff/authorized human | Approve and publish within policy; cannot override factual review silently |
| Policy steward | Foundation/steward role | Propose and decide policy versions under the published process |
| Appeals panel | Independent panel | Hear appeals against decisions; can remand, uphold, reverse |
| Administrator | Technical/operational | Accounts, rate limits, incidents, backups; not content authority by default |
| Organization | Company, institution, agency | Verified identity; may submit material with disclosure; no self-publication |
| Downstream consumer | Agent/service reading the reference | Read/export via API under terms; must attribute |

**Authority is separate from capability.** An administrator can block an account for abuse; that does not make
the administrator a factual reviewer. A publisher can publish; that does not make the publisher the author of
the evidence. An appeals panel can reverse a decision; it does not rewrite the article. Wikipedia's Arbitration
Committee is deliberately constituted so that it "does not rule on content" (R2); that separation is a useful
precedent.

---

## 3. Core objects and invariants

### 3.1 Object map

```
Topic 1─* Article 1─* Revision 1─* Block
  │                     │  │
  │                     │  └─* ClaimOccurrence *─1 Assertion
  │                     └─* Citation *─1 Source 1─* SourceSnapshot
  │                                      └─* SourceAssessment
  ├─* View (pinned to Revision(s)) 1─* ViewRevision
  ├─* Dispute *─* Assertion
  └─* Proposal *─1 Revision (candidate) 1─* Review 1─1 Decision 1─* Appeal
Correction *─1 Proposal
PublicationEvent (append-only, points at Revision)
Actor (Human | Agent | Organization) 1─* Credential
PolicyVersion, Event (append-only)
```

The diagram is conceptual. The current Django models implement a subset; §3.13 maps the extension.

### 3.2 Topic

**Purpose:** the stable unit of scope. A topic is what a reader searches for and what a contributor claims
coverage of. It survives article rewrites, title changes and language editions.

Fields (proposed):
- `id` (stable, opaque), `canonical_title`, `aliases[]`, `slug` (current, redirects preserved)
- `scope_statement` (1–3 sentences: what is in and out)
- `coverage_checklist` (structured list; see §5.2)
- `risk_class` (default; may be raised per edit)
- `maturity` (`seed`, `growing`, `stable`, `disputed`, `deprecated`, `merged`)
- `primary_language`, `available_languages[]`
- `parent_topic`, `related_topics[]`
- `stewards[]`, `created_by`, `created_at`
- `merge_target` (if merged), `supersedes[]`
- `is_ambiguous` (boolean) and `disambiguation_note` (for terms with multiple common meanings)

Rules:
- A topic title can change; the topic ID and old slugs remain resolvable.
- A topic can be merged; **assertion IDs are immutable**. A merge publishes an `old_id -> new_id` alias map, the
  resolver follows it, and old IDs carry a 30-day deprecation header. Revisions are archived, never deleted.
  A merge is not a silent re-point (this is the I8 exception, made explicit).
- A topic is not a notability verdict. Scope disputes are handled by the dispute process, not by silent deletion.
- An ambiguous term (e.g., "Mercury", "Java") gets a disambiguation page that routes readers to the right topic;
  it is not forced into one article. The page is a reader surface, not a new factual layer.
- An orphan topic (no inbound links, no parent) is a publish-gate defect, not a permanent backlog item. Wikipedia
  treats orphanhood as a maintenance queue; we should refuse to publish a new topic with no inbound links and no
  parent (R1). **Bootstrap exemption:** the first 3–5 topics may be published with a curated "Start here" parent
  and a temporary orphan flag until the graph exists.

### 3.3 Article

**Purpose:** a readable presentation of a topic for a language. The article is the unit a reader opens.

Fields:
- `id`, `topic`, `language` (BCP-47), `title`, `opening`, `current_revision`, `status`, `license`,
  `byline[]` (named contributors), `contributors[]` (credit page), `created_at`.

Rules:
- One **canonical** article per topic per language. Reading levels and translations are **views** over the same
  factual base (not separate articles) until a fluent reviewer promotes a translation to a reviewed **language
  edition**; a language edition then becomes an article with its own revisions and review, sharing topic and
  assertion IDs. The `Article` no longer carries a `reading_level` field; that was a second, competing source of
  truth.
- An article never contains facts that are absent from its topic's assertion set unless the fact is explicitly
  marked as local context with its own citation and reviewed. Synthesis is handled by `analysis` blocks (§3.5),
  not by smuggling new facts into prose.
- Deleting an article is not allowed; deprecate/merge with redirects.
- The article has two reader-facing renderings from the same revision: a **summary surface** (lead +
  at-a-glance, self-contained) and the **full article**. The summary is **revision content**, not a separate
  reviewed `View`; it is reviewed with the article and does not go stale on every edit. A generated summary
  artifact is a `View` and follows the view contract.
- The article has a visible byline and a credit page. An expert's reward for eight hours cannot be a username
  buried in a review record.

### 3.4 Revision

**Purpose:** the immutable publication and rollback unit.

Fields: `id`, `article`, `number`, `parent_revision`, `base_revision` (for proposals), `state`, `title`,
`opening`, `blocks[]`, `claims[]`, `citations[]`, `content_hash`, `author` (actor), `provenance`
(`human`, `agent`, `import`, `translation`, `revert`), `created_at`, `published_at`, `review_summary`,
`policy_version`, `as_of` (the date of the underlying data, distinct from the revision timestamp).

States: `draft`, `proposed`, `under_review`, `approved`, `published`, `superseded`, `rejected`, `withdrawn`,
`reverted`.

Rules:
- Published revisions are immutable. Corrections create new revisions.
- A revision has exactly one parent in the article's linear publication history, plus optional `reverts` and
  `merge_of[]` pointers.
- `content_hash` covers title, opening, ordered blocks, claim occurrences and citation links. It is the
  reproducibility anchor and the ETag.
- A revision may be published only with a `Decision` that references a `PolicyVersion` and a `PublicationEvent`.
- A revision cannot be silently edited by an administrator; any change is a new revision with an audit event.
- Revision numbers are not a total order. MediaWiki's `rev_id` is "almost always" but not strictly monotonic
  because imports can create revisions out of order (R3). Never derive correctness or ordering from a number.

### 3.5 Block

**Purpose:** typed, addressable content inside a revision.

Kinds (minimum): `markdown`, `heading`, `image`, `table`, `timeline`, `map`, `quote`, `callout`, `data`,
`analysis`, `embed` (restricted), `reference_list`.

Rules:
- `block_id` is stable across revisions; a block can be moved, edited or removed, and its history is traceable.
- Blocks carry semantic structure, not arbitrary HTML. The renderer is fixed and sanitised.
- A block can declare `assertion_ids[]` it expresses; this is how a view or a translation maps back to the
  factual base.
- **`analysis` blocks are for explanatory synthesis** (causal accounts, comparisons, "why this matters"). They
  carry their own `citation_ids[]`, are reviewed by a `coverage` reviewer, and may draw on multiple sources. This
  is the object the spec previously lacked: the product is prose, and synthesis needs a home and a review path.
- Tables and timelines are data, not prose: they have a schema, a source per row/series where applicable, and
  an "as of" date. A timeline/table view requires per-event/per-row `source_id` and `as_of`, not just a
  view-level date.
- A block type is admitted only with a renderer, an accessibility fallback, an export representation and a
  maintenance owner.

### 3.6 Assertion and ClaimOccurrence

This is the most consequential data-model extension. The current `Claim` is revision-bound text. That is good for
review but insufficient for cross-revision tracking, structured export, dispute pages and derived views.

**Assertion** (stable, topic-scoped):
- `id`, `topic`, `statement` (canonical natural-language phrasing), `structured` (subject, predicate, object,
  qualifiers, unit, value), `assertion_type` (`definition`, `quantity`, `date`, `causal`, `attribution`,
  `evaluation`, `existence`, `comparison`, `synthesis`), `valid_from`, `valid_to`, `region`, `language`
- `status` (`supported`, `partial`, `disputed`, `deprecated`, `retracted`, `unknown`)
- `current_best_occurrence`, `disputes[]`, `supersedes[]`, `superseded_by`
- `created_by`, `created_at`

**ClaimOccurrence** (revision-bound):
- `id`, `revision`, `block_id`, `start`, `end`, `text` (exact substring), `assertion` (FK, nullable during
  migration), `support_status` (`direct`, `partial`, `conflicting`, `absent`), `support_note`.

Rules:
- Every factual claim in an anchor article is a ClaimOccurrence with an exact substring and at least one
  citation. **No uncited factual claim is publishable in an anchor article at any risk class.** A low-risk
  uncited claim may be published only as `provisional`: a visible badge, an expiry date, exclusion from
  citations/exports, and a rule that it cannot appear in an anchor article. This closes the "self-declared low
  risk" loophole the research warns about (587,590 unsourced-statement pages, R1).
- Risk class is assigned by triage/policy, not by the author. A contributor may suggest a risk class; triage can
  raise it and cannot lower it silently.
- A ClaimOccurrence maps to one Assertion. New text that expresses the same fact maps to the existing
  Assertion; a changed fact creates a new Assertion (or a new versioned value with `valid_from`/`valid_to`).
- The mapping is initially by exact/normalized text and human confirmation; semantic matching is a later
  experiment. **Never silently re-point a claim to a different assertion.**
- Assertions are not "votes". Multiple occurrences can support, qualify or contradict an assertion. The
  assertion's status is a reviewed summary, not a count.
- Deleting an assertion is not allowed; deprecate/retract with reason. Wikidata's deprecation model is the
  precedent: known-false statements are retained and marked, not deleted, so they are not re-added as valid
  (R2).
- **Keep the epistemic and temporal axes separate.** `status` says what we currently think (supported,
  disputed, deprecated); `valid_from`/`valid_to` say when the fact was true. Do not use "deprecated" for a
  correct historical value; use the date qualifiers (R3, after Wikidata ranks).

Why this matters:
- "What did we believe on date X" becomes queryable at the assertion level.
- Dispute pages can attach to stable assertions rather than to one article revision.
- Derived views can say "this timeline is based on assertions A1–A17 at revision r12".
- Downstream agents can retrieve a stable claim ID, not a sentence that may have moved.

Cost: more schema and editorial overhead. Mitigation: assertions are created only for substantive factual
claims, not every sentence; migration is incremental; the UI can hide assertion management from casual editors.

### 3.7 Source, SourceSnapshot, SourceAssessment

**Source** (bibliographic): `id`, `title`, `authors[]`, `publisher`, `published_on`, `url`, `kind`, `language`,
`identifiers` (DOI, ISBN, OCLC, patent), `retrieval_note`, `license`, `origin_key`, `created_by`.

**SourceSnapshot** (retrieval evidence): `id`, `source`, `url`, `final_url`, `fetched_at`, `http_status`,
`content_type`, `byte_count`, `sha256`, `title`, `raw_text`, `excerpt`, `extraction_notes`, `error`,
`archive_url`, `retention_class`.

**SourceAssessment** (topic/use-specific judgment): `id`, `source`, `topic`, `use` (`fact`, `definition`,
`attribution`, `data`), `dimensions` (authorship/accountability, editorial or research process, evidence
access, independence, topical competence, **scope match: population/region/period**, freshness, correction
history), `rating` (`strong`, `adequate`, `weak`, `unusable`, `unassessed`), `reasons`, `assessed_by`,
`assessed_at`, `expires_at`, `appeal_status`.

Rules:
- A source is not globally "reliable". It is assessed for a particular use in a particular topic, with reasons.
- A source's own site can establish what it says about itself, not that its claims about the world are true.
- **Independence is a property of the relationship, not the outlet.** It does not imply even-handedness: an
  independent source may be strongly positive or negative. A source can be independent and hostile; a source can
  be friendly and non-independent (R2).
- **COI and bias are orthogonal.** A conflict of interest can exist without bias, and bias regularly exists
  without a COI (R2). Record declared interest and observed bias as separate fields; never collapse them into
  one trust score.
- Shared origin is recorded (`origin_key`): syndicated copies, press releases, citation loops and translations
  of one source are one origin, not independent corroboration. The "citogenesis" list is the canonical catalogue
  of this failure (R2). **`origin_key` is assigned by the application** from DOI/publisher/author/wire metadata
  and snapshot similarity; it is never accepted from the proposer. The application shows per-topic origin
  concentration and requires at least two origins for high-risk claims.
- Self-published material is defined by the absence of independent review, not by the channel; press releases
  and company sites are examples (R2).
- A snapshot is the evidence of what was retrieved, not a license to redistribute the source. Retention and
  display follow the source's terms and the licensing policy (§8.5).
- If a source is retracted, corrected or withdrawn, dependent claims are flagged for re-review; the article
  shows a correction notice rather than silently changing. Crossref exposes 81,345 retraction records with
  `update-to` links, so DOI retraction status is machine-checkable (R2).

### 3.8 View

**Purpose:** a derived or reorganized presentation that helps understanding without changing the factual base.

Kinds: `summary` (a generated summary artifact, **not** the article lead), `timeline`/`table` (generated
artifacts; otherwise they are typed revision blocks), `map`, `chart`, `explainer`, `reading_level`,
`language_edition`, `comparison`, `dataset`, `answer` (later, with citations).

Fields: `id`, `topic`, `kind`, `title`, `base_revisions[]`, `basis_assertions[]`,
`basis_claim_occurrences[]`, `basis_source_snapshots[]`, `generator_type` (`human`, `agent`, `template`,
`model`), `generator_actor`, `transform_version`, `content`, `content_hash`, `review_status` (`draft`,
`reviewed`, `published`, `stale`, `withdrawn`), `reviewed_by`, `published_at`, `stale_reason`, `supersedes`,
`license`, `as_of`, `owner`, `expiry`, `omitted_topics[]`, `limitations`.

**View manifest (required to publish):**

| Field | Meaning |
|---|---|
| `view_id`, `view_revision` | Stable identity; edits create a new revision, never mutate |
| `view_type` | generated_summary / translation / audio / chart / explainer / map / comparison / dataset / answer |
| `basis_article`, `basis_revisions[]` | Exact article revision(s) the view was built from |
| `basis_hash` | Hash of the block/assertion/source set actually consumed |
| `basis_assertions[]` | Stable assertion IDs included, explicitly enumerated |
| `basis_claim_occurrences[]` | Revision-bound claim occurrences used, where applicable |
| `basis_source_snapshots[]` | Snapshot hashes of the sources consumed |
| `omitted_topics[]` | What the view deliberately omits or compresses (a list, not a ratio) |
| `transformations` | Ordered list: select, summarize, translate, aggregate, project, bin |
| `generator` | Human or agent; model/tool name and version; prompt/recipe id |
| `renderer` | Renderer/template version and any transcluded data versions (HTML, PDF, static export, chart image) |
| `output_hash` | Hash of the rendered view content; what a citation resolves to |
| `as_of` | Date of the underlying data, distinct from the revision timestamp |
| `review` | Reviewer identity, date, policy version; or `unreviewed` |
| `status` | draft / reviewed / published / stale / superseded |
| `supersedes`, `superseded_by` | The view revision chain |
| `owner` | Named person/role responsible for refresh; a view without an owner is withdrawn |
| `expiry` | Date after which the view is stale even if the base is unchanged |
| `limitations` | Free-text uncertainty and known omissions |

**View contract (proposed; route B/C — not "high confidence". The E5 experiment and independent critique
are the test, not this document.)**
- **V1 — No new facts.** Every factual statement in a view maps to an assertion/claim in its base revision(s),
  or is explicitly labeled commentary/analysis with its own evidence and review. A view may omit, compress,
  reorder or re-explain; it may not assert.
- **V2 — Pinned base.** A view records exact revision IDs and content hashes. "Current" is a pointer, not an
  implicit behavior.
- **V3 — Attributed generation.** The generator (human/agent/model/template), operator, transform version and
  prompt/template hash are recorded.
- **V4 — Immutable versions.** A published view is immutable; changes create a new view version with a
  `supersedes` pointer.
- **V5 — Automatic staleness.** A view becomes `stale` when any base revision changes, **or** a basis assertion
  changes status, **or** a basis source is retracted, **or** a source assessment expires. Stale views display a
  banner, are excluded from "current" exports/citations by default, and remain readable as historical artifacts.
  It never silently re-renders onto the new revision. Staleness is transitive to any view whose basis set
  intersects the changed unit.
- **V6 — Reviewed before publish.** A citable/exported view is published only after a factual-consistency
  review against its base. An `unreviewed` view may exist for navigation, clearly labeled "generated, not
  reviewed", excluded from citations and exports, and never used as the article's summary. Summaries and
  translations are not exempt when they are citable.
- **V7 — Disclosed lossiness.** A view lists what it omits or compresses when the omission could mislead
  (e.g., "This summary covers the technology, not the regulatory dispute"). The manifest's `omitted_topics[]`
  and `limitations` are the machine-readable version. **No coverage percentage on the reader surface**: it is
  not honestly computable and it invites false precision (D-08 downside, R1 open question).
- **V8 — License and attribution.** The view inherits the base license and adds generator/reviewer attribution.
- **V9 — Machine-checkable vs. judgment.** Base pin, hash, citation resolution and staleness are machine-checked.
  Whether the view preserves emphasis, uncertainty and proportion is human review.
- **V10 — Follow through, don't duplicate.** A view carries no independent citation apparatus; it links to claim
  anchors in the basis revision. Evidence lives in one place (R1, after Wikipedia portal practice).
- **V11 — Stable citation.** A view is citable only via an identifier that resolves to its manifest and content
  hash, and keeps resolving after supersession (returning the superseded artifact plus its successor).
- **V12 — Degradation is mandatory.** Every view has a text or table equivalent, renders at 320 CSS px, and its
  non-text form is an enhancement.

When to build a view:
- **Now:** the lead and at-a-glance are **revision content**, not a `View`; timeline and table are typed blocks
  in the revision, reviewed with the article, with per-event/per-row sources. This is the cheap tier.
- **Next:** the `View` object for translation, audio, chart and generated explainer; one translation pilot.
  These are artifacts that need a manifest, an owner, an expiry and staleness.
- **Later:** maps, personalized explanation, answer view, comparison views across topics.

A view is worth building when (a) readers repeatedly ask for that reorganization, (b) the underlying data is
structured enough to maintain, and (c) a reviewer can check it against the base in reasonable time. A map or
timeline that nobody updates is worse than no map. Wikipedia's maintenance queues are the warning: 587,590 pages
with unsourced statements, 362,781 with dead links, 1,929 still asserting "as of 2015" (R1). Every view type is
another queue of that shape.

### 3.9 PublicationEvent, Proposal, Review, Decision, Appeal, Dispute, Correction

**PublicationEvent** (append-only): `id`, `article`, `revision`, `published_at`, `published_by`, `policy_version`,
`decision`, `previous_revision`, `reason`, `content_hash`. This is what makes "what was published on date X"
answerable after the next publish. The current app's mutable `Article.published` pointer is not enough (R3).

**Proposal**: `id`, `kind` (`create_topic`, `create_article`, `edit_article`, `add_claim`, `change_claim`,
`add_source`, `assess_source`, `create_view`, `edit_view`, `translate`, `merge_topic`, `split_topic`,
`change_scope`, `rollback`), `topic`, `base_revision`, `candidate_revision`, `rationale` (why this helps
readers), `evidence[]`, `disclosures[]` (COI, paid, affiliation, model/operator), `risk_class` (self-declared),
`origin` (`human`, `agent`, `import`, `translation`, `evaluation`), `status`, `created_by`, `created_at`,
`repeat_of`, `supersedes`.

**Review**: `id`, `proposal` or `revision`, `role` (`factual`, `source`, `coverage`, `readability`,
`policy`, `translation`, `community`), `scope`, `verdict` (`support`, `concern`, `object`, `abstain`),
`claim_verdicts[]`, `reasons`, `evidence_checked[]`, `reviewer` (actor), `independence` (model/provider,
evidence packet hash, relationship to author), `created_at`.

**Decision**: `id`, `proposal`, `decision` (`approve`, `reject`, `request_changes`, `publish`, `defer`,
`rollback`), `decided_by`, `policy_version`, `reasons`, `conditions[]`, `created_at`.

**Appeal**: `id`, `decision`, `grounds` (`new_evidence`, `procedural_error`, `policy_misapplication`,
`conflict_of_interest`, `factual_error`, `disproportionate`), `argument`, `evidence[]`, `appellant`,
`status`, `panel[]`, `outcome`, `created_at`, `decided_at`.

**Dispute**: `id`, `topic`, `assertions[]`, `positions[]` (each with sources and proponents), `scope`
(`factual`, `terminology`, `scope`, `weight`), `status` (`open`, `narrowed`, `resolved`, `archived`),
`resolution`, `created_at`.

**Correction**: `id`, `topic`, `reported_by`, `relationship` (`reader`, `subject`, `representative`,
`organization`, `anonymous`), `description`, `evidence[]`, `severity`, `status` (`received`, `triaged`,
`accepted`, `rejected`, `duplicate`, `needs_info`), `linked_proposal`, `resolution_note`, `public_notice`,
`created_at`, `resolved_at`.

### 3.10 Actor, Agent, Organization

- **Actor** is the base identity: human account, agent account, organization account, service.
- **Agent** has `operator` (human or organization), `model_family` (self-declared), `scopes`, `status`,
  `verification_level`, `created_at`.
- **Organization** has `legal_name`, `domain`, `verification_method`, `contact`, `disclosures`.
- **Credential** is rotatable, hashed, scoped, revocable; it is not the identity.
- **Verification** is recorded as `unverified`, `contact_verified`, `domain_verified`, `organization_verified`,
  `identity_verified`, with method, date and verifier. Never display "verified" without the method.
- **Track record** is topic-scoped and observational: accepted proposals, reversions, corrections accepted,
  review agreements, source diversity, account age, rate-limit compliance. It is not a global score and not a
  claim of expertise.
- **"One account = one person" is a hypothesis with a confidence, never a constraint.** Wikipedia's own
  permission tiers are activity thresholds, not identity checks: autoconfirmed is 10 edits + 4 days, extended
  confirmed is 500 edits + 30 days, and about 2.65 million accounts meet the first bar, most inactive (R2).

### 3.11 PolicyVersion and Event

- **PolicyVersion**: `id`, `kind` (`publication`, `review`, `identity`, `quotas`, `source`, `licensing`,
  `appeals`, `moderation`), `version`, `rules` (structured), `description`, `effective_from`,
  `supersedes`, `approved_by`, `comment_period`, `change_reason`.
- **Event**: append-only audit record with actor, action, object, before/after hashes, reason, policy version,
  timestamp. Events are the basis for replay and transparency; they are not a mutable log.

### 3.12 Invariants

| ID | Invariant |
|---|---|
| I1 | A published revision is immutable; any change is a new revision. |
| I2 | Every published factual claim has a source, a snapshot (or an explicit metadata-only exemption) and a review record. |
| I3 | A citation's quote must resolve to the preserved snapshot, or the citation is invalid. |
| I4 | A proposal names the exact base revision it changes; a stale base is refused, not merged silently. |
| I5 | A decision names the policy version it applied. |
| I6 | A revert creates a new revision; history is never erased. |
| I7 | A view names its base revision(s), basis assertions, source snapshots and content hash; a change to any of them marks it stale. |
| I8 | An assertion is never silently re-pointed; changes create a new assertion or a versioned value. A topic merge is the explicit exception: it publishes an `old_id -> new_id` alias map and a 30-day deprecation header. |
| I9 | At launch, an agent cannot publish; a publisher cannot silently override a factual objection. This is a launch policy, not a permanent prohibition; D-20/E15 is the reopening path. |
| I10 | A review records its role, scope and independence metadata; reviewers do not see each other's verdicts before submitting. |
| I11 | Identity verification is recorded with its method; self-declared metadata is labeled as such. |
| I12 | Every rate-limit, block and rollback decision has a reason and an appeal path. |
| I13 | Derived views and translations inherit the base license and add attribution. |
| I14 | Source snapshots are evidence, not a redistribution license; retention and display follow policy. |
| I15 | No automatic publication is enabled until a measured shadow-mode evaluation meets a published threshold. |
| I16 | Publication is recorded as an append-only event; a mutable pointer is never the only record. |
| I17 | The content date (`as_of`) is stored separately from the revision date; a stale "as of" is visible. |
| I18 | A view follows through to the basis revision's evidence; it does not duplicate or invent a citation apparatus. |
| I19 | Review at creation is the **launch policy parameter** (`PolicyVersion`), not an invariant; E2 may change it. Post-hoc review is always an audit channel. |
| I20 | No model call or network fetch occurs inside a write transaction; jobs are idempotent and attempt-fenced. |
| I21 | No uncited factual claim is publishable in an anchor article at any risk class; a `provisional` uncited claim is badged, expires, and is excluded from citations/exports. |
| I22 | A merge, split or rename never breaks a stable ID: an alias map and resolver preserve old references. |

### 3.13 Mapping to the current Django models

| Proposed object | Current model | Action |
|---|---|---|
| Topic | minimal `Topic` added at M0 (slug, title, scope statement, parent, disambiguation flag, creator); `Article.topic` FK; no scope/coverage checklist yet | **Partial at M0**; full scope/coverage, split/merge and disambiguation behaviour at M1; migrate remaining articles; keep article slugs/redirects |
| Article | `Article` | `topic` FK added at M0; `language`, `byline[]`/`contributors[]` remain later (the public credit page is derived from revisions for now); no `reading_level` field |
| Revision | `Revision` | Extend with `parent_revision`, `policy_version`, `as_of`, `merge_of` |
| Block | `Block` | Extend kinds; add `analysis`; keep stable `block_id` |
| Assertion | none | **Add at M4**; launch uses `claim_key` on `Claim` + change diff at M2 |
| ClaimOccurrence | `Claim` | Rename/extend; add `claim_key` (M2) and `assertion` FK (M4); keep offsets/support status |
| Source | `Source` | Extend with identifiers, license, origin key (system-derived) |
| SourceSnapshot | `SourceSnapshot` | Extend with archive URL, retention class |
| SourceAssessment | none | **Add at M2** |
| View / ViewRevision | none | **Add at M3**; manifest fields; derived artifacts only |
| PublicationEvent | `PublicationEvent` added at M0; `Article.published` is now a cache pointer | **Added at M0**; append-only, per-article sequence, unique `(article, sequence)` and `(article, revision)` |
| Proposal | `Proposal` | Extend kinds, disclosures, risk class, base hash |
| Review | `Review` | Added human `reviewer` attribution and `origin='human'` at 2026-11-05; still to extend: scope, independence metadata, review round |
| Decision | embedded in `Proposal`/`AuditEvent` | **Add at M2** (or a typed audit event first) |
| Appeal | none | **Add at M2** (one adjudicator) |
| Dispute | none | **Add at M2** |
| Correction | none | **Add at M1** |
| Actor/Agent/Org | `Agent`, Django user, `ContributorProfile` | Added `ContributorProfile` trust levels (`new`/`standard`/`trusted`/`steward`) and capability/quotas at 2026-11-05; still to add identity verification, operator/org metadata and `Organization` at M4 if needed |
| PolicyVersion | `ConfigVersion` (policy kind) | Extend at M1 to a first-class policy with effective dates and approval |
| Event | `AuditEvent` | Keep; add before/after hashes and policy version |

**Migration stance:** add objects behind feature flags; do not rewrite the existing editorial flow. The first
implementation slice is `PublicationEvent` + a minimal `Topic` + byline/credit page + watchlist + claim resolver
+ restore drill. `PublicationEvent` is first because the current pointer loses history on every publish. The
full `View` and `Assertion` objects are M3/M4, not launch.

**M0 implementation status (2026-11-04).** A first M0 slice is **implemented in the workshop**:
`PublicationEvent` (append-only; per-article sequence; kinds `initial`/`publish`/`revert`/`import`;
`published_at`/`published_by`, previous revision, policy version, decision, reason, content hash; unique
`(article, sequence)` and `(article, revision)`; the event→article FK is `PROTECT`, so deleting an article cannot
cascade-delete its publication history), the minimal `Topic` with `Article.topic`, the opt-in `Watch`,
migrations `0006`/`0007`/`0008` (`0007` backfilled 6 existing publication events on the local DB; `0008` sets the
`PROTECT` FK), the reader surfaces `/topics/`, `/topics/<slug>/`, `/contributors/<username>/` (public credit page,
no private data), `/watchlist/` (web-only digest, no email), the article-page byline/topic/provenance/watch block,
and the history-page publication log. `manage.py check` and `makemigrations --check` are clean; the suite is 154
tests (was 133; 21 new). **Still open — inside M0 or later; do not describe as done:** stable permalink / claim resolver,
license/attribution fields, SQLite backup + restore drill, FTS5, `Idempotency-Key`/`If-Match` (M0 remainder);
correction intake, review tiers, full `Topic` scope/coverage (M1); a designed public (anonymous) full-history page,
email digest, `View`/`Assertion` objects (later). This status note describes code and tests only; nothing was
deployed.

**Authorization and review queue (2026-11-05).** A first deterministic slice is implemented: `ContributorProfile`
trust levels, `core/authorization.py` (capabilities, derived states, one `can()` evaluator, reason codes,
self-review/self-decision guards, rolling 24h quotas), `Review.reviewer`, human review form on the proposal page,
and `/review/` queue with filters, coverage and objections. Same-agent reviews are marked non-independent. The
quota values (new 1/0, standard 5/10, trusted 10/25 per day) are **starting parameters, not measurements**.
Still open: auto-assignment, automatic trust promotion, external policy engine, withdrawal state, appeal/dispute
workflows, per-reviewer calibration. See [AUTHORIZATION-STATE-MACHINE.md](AUTHORIZATION-STATE-MACHINE.md).

---

### 3.14 Implementation ladder (what to build in what order)

The full object model is a reference target, not a single build. The ladder below sequences it so that each step
is useful on its own and no step requires the whole model. It is a proposal; the estimates are rough.

| Step | Build | Unlocks | Do not start before |
|---|---|---|---|
| **M0 — correctness and return loop** (2–3 weeks) | `PublicationEvent`; stable permalink + claim resolver; author byline/credit page; opt-in weekly watchlist; license/attribution fields; SQLite online backup + restore drill; FTS5 index; `Idempotency-Key`/`If-Match` on the existing write API | "What was published on date X"; citable revisions; a reason for experts to return; search; safe retries; recoverable data | — |
| **M1 — topic and correction** (4–6 weeks) | `Topic` with scope/coverage checklist and disambiguation; correction intake, tracking and budget; review tiers (1 review for low/standard, 2 for high/contentious); `stable` state; `PolicyVersion` for the human gate | Reader correction path; scope/split/merge; review capacity measurement | M0 |
| **M2 — cross-revision tracking** (4–6 weeks) | `claim_key` on the existing `Claim` (a stable hash/identity for substantive claims) plus a "this claim changed" diff; `SourceAssessment` with expiry; `Dispute`; one-adjudicator appeal; `Decision` record | "What did we say about this claim before?"; source-quality disputes; appeal record | M1, E2/E3 results |
| **M3 — derived artifacts and language** (6–8 weeks) | `View` + manifest for translation/audio/chart/explainer; one translation pilot; reading-level view | Provenance for artifacts that need it; language pilot | M2, E5 results |
| **M4 — later** | Full `Assertion` model; `Organization`; policy-lifecycle UI; autonomy shadow mode; maps/charts; public exports | Expansion | M3, licensing decision, measured capacity, a trigger (e.g., a claim corrected twice across revisions and a reader/agent asks what we used to say) |

**M0 progress (2026-11-04):** the `PublicationEvent`, minimal `Topic`, byline/credit page and watchlist parts of
M0 are implemented; the stable permalink + claim resolver, license/attribution fields, backup/restore drill, FTS5
and `Idempotency-Key`/`If-Match` parts are not. See the status note in §3.13.

**Rules for the ladder:** each step ships with a test and a rollback; no step depends on a later one; do not
build M2/M3 objects before the M1 review flow is measured, or the project will have a rich schema and no
capacity to review it. **The `Assertion` object is deliberately M4, not launch**: 80% of its value is a stable
`claim_key` plus a diff, which M2 delivers at a fraction of the cost.

**Minimum viable view.** The smallest honest version is the lead + at-a-glance as **revision content** (no
`View` object, reviewed with the article), plus a typed timeline/table block with per-row sources. A generated
summary/translation/chart is a `View` and follows the contract; do not ship a generated view with no reviewer
and call it a view — call it a draft.

---

## 4. Reader experience

### 4.1 Default article anatomy

A standard article should answer, in order: *What is this? Why does it matter? How do we know? What is
disputed? What changed? Where do I go next?*

1. **Header:** title, one-sentence definition, topic type, maturity badge, last reviewed date, reading time,
   **byline** ("written by X, maintained by Y"), language/reading-level selector, "report an error", "cite this
   page", "watch this topic".
2. **Lead:** 2–4 paragraphs. The first sentence defines the topic; the second says why it matters; the third
   states the scope and the most important uncertainty. No suspense, no throat-clearing. The lead is the first
   screen and may be the only screen; Wikipedia's lead gets 32% of link clicks from 17% of links (R1).
3. **At a glance** (optional, structured): 3–7 key facts, each with a claim link and an "as of" date. This is
   **revision content**, reviewed with the article, not a separate auto-staling `View`.
4. **Contents:** section links, including "Disputes", "Corrections", "Further reading". Keep it small on mobile.
5. **Body sections:** default order is definition/history, mechanism/how it works, evidence and data,
   significance/uses, disputes and open questions, current status. The order may vary by topic type; the
   default is a starting point, not a straitjacket.
6. **Evidence drawer:** per claim, a collapsed panel with sources, quotes, snapshot date/hash, support status,
   reviewer notes and "challenge this source". It is one interaction away, not the primary surface; only 0.29%
   of page views produce a reference click, and clicks rise on short/low-quality pages (R1). The reader should
   not have to open it to understand the article, but should never be far from it.
7. **Uncertainty and gaps:** a short, explicit panel: what is well supported, what is contested, what is
   unknown, what is stale.
8. **Disputes:** if any, a **summary of adjudication** with links to the dispute page; not a he-said/she-said
   log and not the raw talk thread. Showing raw deliberation lowered measured quality ratings in a controlled
   experiment; resolved conflict removed the penalty (R1). Design for resolution, not exposure.
9. **Corrections:** a public correction log (date, what changed, why, link to revision/decision).
10. **Provenance:** "This revision (r12) was published on … after review by …; evidence as of …; see history."
11. **Related topics and views:** curated links, not an algorithmic soup.
12. **Cite this page:** stable citation with revision ID, access date, license.

**Article length.** No hard character cap. Instead: a scope statement, a coverage checklist and a split rule
(§5.3). A reader should be able to finish the lead and the first two sections and understand the topic; depth
lives below the fold and in child topics. Wikipedia's size guideline starts warning around 50 KB of readable
prose (~8,000 words); 98.5% of its articles are under 6,000 words (R1).

**Reader states (the build contract).** The page is not one layout; it is five states, each with required
elements and a 320 px behaviour. This is the level of detail the build needs; otherwise the easiest panel wins.
1. **Default article:** header, lead, at-a-glance, contents, body; evidence closed; byline and correction link
   visible. Mobile: lead above any infobox/sidebar; contents collapsible; no horizontal page scroll.
2. **Summary / quick fact:** lead + at-a-glance + "where this comes from" + "read more"; self-contained; no
   separate review artifact. Mobile: one screen for the lead and the top three facts.
3. **Deep section:** a section with its own sub-contents, evidence affordances, and "related" links; the reader
   can cite a section anchor.
4. **Evidence open on claim X:** the drawer scrolls to and highlights claim X; the article text stays in place;
   focus moves to the drawer and returns on close; Escape closes; no focus trap that hides the trigger (WCAG
   2.4.11).
5. **Search results / no results:** results show title, match reason, maturity, last reviewed; no-results state
   suggests a broader term, a related topic, or a correction request. A disambiguation term routes to a choice
   page, not a guess.

**Claim affordance (decide once):** a subtle underline on the claim plus a small numbered superscript; the
drawer opens on click/keyboard, scrolls to the claim, and highlights the quote. Do not highlight every claim
permanently, and do not require text selection. Uncited claims show a distinct "no citation" marker, not the
same affordance as a cited claim.

### 4.2 The evidence drawer

The drawer is the product's trust surface. It must be fast, keyboard-accessible and readable on mobile.

For each claim:
- The claim text, highlighted when the drawer is open (not permanently).
- Support status: **direct**, **partial**, **conflicting**, **no citation**, **stale**. `no citation` and
  `stale` are explicit derived states in the UI and review record, not ad hoc. `unassessed` is a valid source
  state; the drawer says "not yet assessed" rather than implying a judgment.
- Each citation: source title, author/publisher, date, source type, link, quote (with the quoted passage
  highlighted in context where possible), snapshot date and SHA-256, retrieval status.
- The support note: what the source is cited for, in one sentence.
- Reviewer notes: factual reviewer's verdict and reason, source reviewer's assessment.
- Actions: "challenge this source", "report an error", "view revision history".
- A visible distinction between "the source says X" and "we conclude X".

**Design constraints from the research:**
- Do not rely on hover or tooltips; they fail mobile, keyboard and screen readers (R1).
- Do not hide essential context behind the drawer. The lead, the uncertainty panel and the correction link
  must be visible without opening anything.
- Do not duplicate the full citation apparatus into every view; views follow through to the claim anchors
  (R1).
- A "needs evidence" marker is dated and tracked, not permanent decoration. Wikipedia has 587,590 pages with
  unsourced-statement tags; an ageing policy is part of the feature (R1).
- Use per-statement "as of" semantics: a figure carries the date of its source, not the page's edit date (R1).

### 4.3 Uncertainty, scope and disagreement

Uncertainty is shown at three levels:
- **Claim level:** support status and source quality.
- **Topic level:** a "Confidence and gaps" panel with explicit statements ("The mechanism is well established;
  the long-term health effects are contested; the 2024 figures are preliminary").
- **Article level:** maturity badge (`seed`, `growing`, `stable`, `disputed`) and last-reviewed date.

Disagreement:
- A **Disputed** banner names the disagreement and links to a dispute page.
- The dispute page lists positions, the strongest evidence for each, the points of agreement, and what would
  change the assessment. It is not a forum thread.
- The article states the **weight of evidence**, not a false equivalence. If reliable sources overwhelmingly
  support one view, the article says so; minority views get proportional space, not equal space. Wikipedia's
  due-weight rule is explicitly about prevalence in reliable sources, not prevalence among editors or the public
  (R2).
- "Open questions" are explicit and dated.
- **Show adjudication, not deliberation.** A resolved dispute can be summarized; an open one should say what is
  unresolved and what would resolve it. Raw process is for the history page, not the article.

### 4.4 Corrections

Every article has "Report an error". The form asks: what is wrong, where, what should it say, what is your
evidence, and your relationship to the subject (reader, subject, representative, organization). It does not
require an account; it does require a contact method for follow-up (or allows anonymous with a tracking code).

Reader-visible states: `received` → `triaged` → `accepted` / `rejected` / `duplicate` / `needs_info`. The
correction page shows the status and the public resolution note. Accepted corrections produce a revision and a
public correction notice ("Corrected 12 Nov 2026: the 2018 figure was replaced with the 2022 figure; see r14").

**Service levels (starting points, calibrate):** acknowledge within 2 business days; substantive decision
within 14 days; urgent legal/safety within 24 hours. Missing the window is itself a reported metric.

**Correction budget and clustering.** Corrections are the least rate-limited and most promised surface; an
anonymous correction channel can outrun a solo triager. Add: (a) a daily correction intake budget (starting
range 10–20/day; above it, queue with an honest acknowledgment); (b) duplicate/near-duplicate clustering at
intake so 20 variants of one complaint are one case; (c) a separate severity triage for legal/safety; (d) a
published correction capacity and backlog. A correction SLA that is promised but not staffed is worse than a
longer, honest one.

### 4.5 History and provenance

The history page shows:
- Revision timeline with author, date, summary, review outcome and policy version.
- Word-level diff between any two revisions.
- Claim-level changes: which assertions were added, changed, deprecated or re-cited.
- Decisions and reviews, with reasons.
- Appeals and their outcomes.
- Source changes: new snapshots, retractions, assessments.
- "What did this article say on date X" (revision at date) and "what did we believe about assertion A on date
  X" (assertion history).
- Publication events: who published what, under which policy.

A reader can always answer: *who changed this, when, why, on what evidence, after what review, and what
happened next?* A permalink alone does not tell a reader that a newer revision corrected it; the history and
correction notice must (R1, R3).

### 4.6 Views: when and how

Views are introduced only when they earn their maintenance cost.

| View | Reader job | Build now? | Maintenance model |
|---|---|---|---|
| Summary / quick-fact surface | "Give me the gist or the answer" | Yes — **revision content**, not a `View` | Reviewed with the article; no separate stale flag |
| Timeline | "When did this happen?" | Yes for history/event topics, only if dates are structured claim fields | Typed block in the revision; per-event source/as_of; reviewed with the article |
| Table | "Compare these things" | Yes for comparative topics, over typed claims | Typed block; schema + per-row sources; reviewed with the article |
| Map | "Where is this?" | Later; only with spatial data | Geo data with sources; a map editor is expensive; needs a maintenance owner |
| Chart | "Show the trend" | Later; only with a maintained dataset | Dataset version + chart spec + source |
| Explainer | "Explain it differently" | Later | Human-authored or model-assisted, reviewed |
| Reading level | "Explain it more simply" | Later (simple English first) | A view over one claim base, not a separate wiki; reviewed |
| Language edition | "Read in my language" | Later (one pilot language) | View of a source revision + human review; MT modification ratio recorded |
| Answer | "Answer my question" | Later; only with citations and a clear "not a source" boundary | Generated transiently; never published as fact |

A derived artifact displays: **"Derived from r12 (hash …) on 2026-11-01 by [generator]; reviewed by
[reviewer]; status: current/stale; owner: [name]; omits: [list]."** No coverage percentage. A stale view is
visibly stale and is not cited as current. An `unreviewed` artifact says "generated, not reviewed" in the same
position and weight.

**Sequence:** lead/at-a-glance/timeline/table as revision content first (cheap, accessible, diffable); the
`View` object for translation/audio/chart/explainer next; maps and charts deferred until data, license,
fallback and owner exist (R1).

### 4.7 Navigation, search and exploration

- **Search:** full-text over titles, openings, headings and claims; filters for topic type, maturity, language,
  risk, "has open dispute", "recently corrected". Results show why a page matched (title, heading, claim).
  No-results state suggests a broader term, a related topic, or a correction request.
- **Disambiguation:** a term with multiple common meanings gets a choice page (`is_ambiguous` on `Topic`), not
  a forced single article. A merge/rename page explains the redirect and preserves the alias.
- **Topic pages:** canonical entry point; aliases redirect; related topics are curated, not inferred only.
- **Paths:** "Start here" collections for a domain; "Explain this next" links; "Compare with" views. Borrow an
  existing classification (LCC/Dewey/UDC) rather than inventing a taxonomy (R1).
- **No global feed.** A "Recently corrected" and "Open disputes" page are acceptable; a social activity stream
  is not the default.
- **Orphans:** a topic with no inbound links is a publish-gate defect; not automatically deleted, but not
  published without a parent or inbound link.
- **Search quality:** measure whether a reader finds a relevant topic in the first 3 results; measure
  zero-result queries; review them weekly.

### 4.8 Language editions and reading levels

**Multilingual is the long-term ambition; launch is one language and language-ready.** The schema stores
language from day one, the UI can show a language selector when a second edition exists, and a translation view
pilot is the first step. Do not promise a multilingual reference on day one; do not design a schema that cannot
get there.

- **Reading levels are views, not forks.** A simple-English variant should be a view over one claim base, with
  its own review and a declared audience. Simple English Wikipedia is a separate edition with ~4% of English
  Wikipedia's articles (286,395 vs 7,259,287), and its own policy says most articles are simplified copies of
  other editions; that is a fork with a permanent drift problem (R1). Do not reproduce the fork.
- **Translations are views, not editions.** A machine translation of an article is a view of that revision,
  marked unofficial until a human reviewer in the target language signs off; the modification ratio is recorded.
  Wikimedia's Content Translation uses exactly this gate: MT is a starting point, unmodified MT is likely to be
  deleted, and the tool tracks how much was modified (R1).
- **No automatic fact propagation.** A change in one language does not silently change another. A translation
  proposal names the source revision and the target language; a fluent reviewer checks meaning, terminology,
  and any added/omitted qualification.
- **Machine translation is labeled.** It can be a draft, never a published edition without human review.
- **Reading levels** are variants, not simplifications that drop uncertainty. A simple article must still say
  what is disputed and what is unknown, in simpler words.
- **Language governance** (who decides terminology, which languages launch) is deferred; the spec proposes a
  pilot with one language and a named reviewer before scaling.

### 4.9 Accessibility and mobile

- **WCAG 2.2 AA** as the target, not an aspiration. Specific criteria that bite a reference site:
  - **2.4.11 Focus Not Obscured (Minimum), AA** — a focused component must not be entirely hidden by author
    content; sticky headers and drawers are the usual offenders.
  - **2.5.8 Target Size (Minimum), AA** — pointer targets at least 24×24 CSS px, with exceptions; citation
    superscripts are inline, but drawer close buttons and reference links are not.
  - **1.4.10 Reflow, AA** — content works at 320 CSS px without two-dimensional scrolling, except content that
    requires 2D layout (data tables, maps); those must not lose information.
  - Plus keyboard operability, visible focus, contrast (4.5:1 for normal text), semantic headings, table
    captions and scoped headers, alt text (ideally ≤125 characters), no hover-only content, no color-only
    meaning, and a reading experience that works without JavaScript.
- **Evidence on mobile:** the drawer becomes a full-screen sheet with a back button; the claim stays
  highlighted; source quotes are readable without horizontal scrolling. Watch 2.4.11: an overlay must not hide
  the focused control.
- **Tables and timelines:** responsive patterns (stacked rows, horizontal scroll with sticky headers, a
  text alternative). A table that cannot be read on a phone needs a summary or a different view.
- **Lead above the infobox on narrow screens**, as Wikipedia does for readability (R1).
- **Low bandwidth:** server-rendered HTML, compressed assets, no required JavaScript for reading, lazy images,
  offline/export options later.
- **Testing:** automated checks (axe) plus manual keyboard and screen-reader passes on the article, evidence
  drawer, history and correction form. A release criterion, not a nice-to-have. 63–65% of Wikimedia survey
  respondents were on mobile (R1); mobile is the majority, not an edge case.

### 4.10 What we will not do (reader experience)

- No infinite feed, engagement gamification or notification spam. **But** an opt-in watchlist is required: a
  weekly batched digest when a watched topic changes, a claim is challenged, or a correction is resolved. One
  notification type, off by default, no push, no unread-count anxiety. This is the return loop the research
  says matters; "no notifications" was overcorrecting.
- No personalized factual claims. Personalization may change presentation (font, density, saved topics,
  language), not facts.
- No AI answer box that outranks the article without citations and a clear provenance label.
- No dark patterns in correction or appeal flows.
- No "verified" badge without a recorded method.
- No map/timeline that is not maintained; a stale visual is worse than none.
- No raw talk-page or dispute thread as the reader's main disagreement surface.

---

## 5. Editorial model

### 5.1 Topic scope

Every topic has a **scope statement**:
- One paragraph: what the topic covers, what it excludes, and why.
- In-scope bullets (3–7) and out-of-scope bullets (3–7), with links to adjacent topics.
- A **risk class** and the reason.
- A **coverage checklist** (below).
- A **definition** and aliases, including disputed names.

Scope is reviewed when a topic is created and when a proposal changes the lead, adds a major section, or
proposes a split/merge. Scope disputes are legitimate content disputes; they are not solved by edit warring.

### 5.2 Coverage and adequacy

Adequacy is assessed against the checklist, not word count. The default checklist:

| Dimension | Adequate when… |
|---|---|
| Definition | A reader can say what the topic is and is not after the lead. |
| Context | Why it matters, to whom, and since when. |
| History | Key origins and changes, with dates and sources. |
| Mechanism / how it works | The causal or procedural account is explained, not just named. |
| Evidence | The strongest evidence is cited, including its limits. |
| Disagreement | Significant disputes are named and weighted. |
| Uncertainty | Open questions and stale data are explicit. |
| Current status | "As of" date and recent developments. |
| Access | Further reading, primary sources, data, related topics. |
| Readability | A curious non-specialist can follow it; jargon is defined. |

A topic is `seed` until the checklist is met at a basic level, `growing` when most dimensions are covered,
`stable` when the checklist is met and the article has survived a review cycle without substantive correction.
"Stable" is not "finished"; it is a maintenance state.

**No completeness score.** Wikidata, which has a machine-readable model for almost everything else, explicitly
does not include a completeness indicator (R2). Coverage adequacy is a reviewed judgment with a rationale, not a
computed percentage. The checklist is the record of that judgment. **Do not display "covers X of Y claims" on the
reader surface**: it is not honestly computable and it invites false precision. A view lists what it omits
(`omitted_topics[]`) and its `limitations`; it does not pretend to a ratio.

### 5.3 Splitting and merging

**Split when** any two are true:
- A subtopic has enough independent evidence and reader demand to stand alone.
- The section is a large share of the article (starting heuristic: >35% of body text, or >2,500 words) and has
  its own scope.
- The article's lead can no longer summarize the whole without distortion.
- Splitting reduces reader confusion rather than multiplying navigation.

**Merge when** two topics have the same scope, the same evidence base and no independent reader demand; or one
is a stub that cannot grow without duplicating the other.

Process: propose `split_topic`/`merge_topic` with the new scope statements, coverage checklists, redirect plan
and assertion mapping. Review by coverage + factual reviewers. Preserve old slugs as redirects; keep assertion
IDs; archive rather than delete. A split is not a way to win a dispute by forking the topic. Wikipedia's
content-fork guideline calls the POV fork the failure mode, and splits are expensive to undo (R2).

### 5.4 Definitions, terminology and regional variation

- A **definition** is a claim like any other: sourced, reviewable, and attributable when contested.
- **Disputed terminology** gets a terminology note: who uses which term, why, and what the article uses. The
  article does not pretend a contested label is neutral.
- **Regional variation** is explicit: dates, units, legal definitions, names and practices. Use qualifiers
  ("in the EU", "in the US", "as of 2024") rather than false universals.
- **Historical names** are recorded with `valid_from`/`valid_to` and a note; do not silently modernize quotes or
  names.
- **Pronouns and self-description** for living people follow the subject's published preference where reliable,
  with care for privacy and consistency.

### 5.5 Evidence quality and source assessment

Source assessment is **per use and per topic**, with reasons. Dimensions:

| Dimension | Questions |
|---|---|
| Authorship / accountability | Is there a named author or institution that stands behind it? |
| Process | Peer review, editorial review, official statistics, or none? |
| Evidence access | Does it show data, methods, documents, or only assertions? |
| Independence | Is it the origin, or a syndicated/derived copy? Who funded it? |
| Competence | Does the source have topic expertise? |
| Freshness | Is it current for this claim? Does it have an "as of" date? |
| Correction history | Has it retracted or corrected? Does it have a track record? |

Ratings: `strong`, `adequate`, `weak`, `unusable` — for a specific use. A `strong` source for a definition may
be `weak` for a contested causal claim. Record the reason and an expiry/review date. Anyone can challenge an
assessment; the challenge is a proposal, not a silent edit.

**Machine-checkable:** quote present in snapshot, URL resolves, duplicate snapshot hash, shared `origin_key`,
publication date, retraction status (Crossref `update-type:retraction`, with `update-to` links), source on a
blocked list, source is the subject's own site, two citations share a publisher/author/DOI ancestor.
**Judgment:** whether the source is authoritative, independent, competent, and whether the passage entails the
claim.

**Independence ≠ even-handedness.** An independent source may be hostile; a friendly source may be
non-independent (R2). Record both. **COI ≠ bias.** A declared interest and an observed bias are separate
fields (R2). Do not collapse them into one score.

**Citation laundering** is a graph problem, not a count. The citogenesis list and Rekdal's "academic urban
legends" show the mechanisms: citing a secondary source as primary, padding a weak citation with sources that
all trace to one ancestor, and copying a reference without reading it (R2). A provenance graph is the only
defence that scales.

### 5.6 Neutrality as checks, not a score

No single neutrality number. Split the checks by who can actually perform them.

**Four mandatory sentence-level checks (any trained reviewer, with an anchor per check):**
1. **Attribution.** Are contested claims attributed ("according to X") rather than stated as fact?
2. **Labeling.** Are fact, analysis, opinion, allegation and prediction distinguished?
3. **Scope.** Are dates, regions and populations specified?
4. **Language.** Is loaded or promotional language replaced with specific, attributable language?

**Five coverage judgments (require recorded domain competence or a `coverage` reviewer):**
5. **Proportion.** Does the space given to each view match its weight in reliable sources? (Weight is prevalence
   in reliable sources, not editor or public opinion — R2.)
6. **Framing.** Does the lead emphasize the most important, best-supported aspects, or a fringe angle? Avoid a
   separate "criticism" section that creates a hierarchy of fact (R2).
7. **Omission.** Are significant counter-evidence, failures, or context missing?
8. **False balance.** Are minority or fringe views given equal weight to well-supported consensus?
9. **Sourcing symmetry.** Are claims on both sides held to the same evidentiary standard?

**Not a review criterion:** "would a reasonable reader form a proportional conclusion?" is a usability test
question (E1), not a reviewer judgment; keep it in reader research.

A review records which checks were performed, the quoted anchor, and an explicit "not assessed, because…" for
each skipped check. "Neutrality: pass" without reasons is not a review. A "neutral" badge on an article is a
claim the system cannot support; a list of resolved and unresolved objections is a claim it can (R2). A
generalist reviewer cannot adjudicate proportion; the spec must not pretend otherwise.

### 5.7 Well-supported negative information

**Launch scope limit:** high-risk/contentious topics about real living people or companies are **out of scope
for the public corpus at launch**. The policy lab's one-model panel escapes 44.2% of standard and 57.2% of
high-risk defects; a mixed panel still escapes 44.0% of high-risk. Until measured catch rates and a named
policy/legal reviewer exist, publishing BLP/company allegations would promise a standard the review system
cannot meet. The policy is written now, but the corpus waits. Hypothetical cases live in `/sandbox`, excluded
from search, exports and anchor counts.

Negative information about a person, company or institution is treated as evidence, not as a viewpoint.

- **Higher bar:** at least two independent, high-quality sources, or one authoritative primary source plus
  corroboration. Allegations are labeled as allegations; findings as findings.
- **Right of reply:** if the subject provides a substantive, evidenced response, include it. A response does not
  erase a well-sourced finding.
- **No forced balance:** if the evidence is strong and one-sided, say so. Do not give a denial equal space
  merely because it exists.
- **BLP asymmetry:** for living people, contentious material that is unsourced or poorly sourced should be
  removed immediately and without discussion; the three-revert rule does not apply to such removals; and the
  "eventualism" argument does not apply to biographies — biographies must be fair to their subjects at all
  times (R2). If a content discussion ends without consensus, the default is removal for living people, not
  retention of the status quo (R2).
- **Companies are not BLP subjects.** Wikipedia's BLP policy does not normally apply to corporations; for a
  company, the shield is due weight and sourcing quality, not BLP-style removal (R2). Our policy should say
  this explicitly rather than accidentally extending BLP to companies.
- **Privacy and legal:** minimize irrelevant personal detail; follow BLP-style care; legal review for
  defamation, privacy and safety risk; urgent escalation path.
- **Removal requests:** a subject's objection is not sufficient to remove well-sourced negative information.
  It is sufficient to trigger a correction review, a right-of-reply check and, if new evidence exists, a new
  proposal.
- **Documentation:** the decision to include or exclude negative information records the sources, the
  proportionality reasoning and the legal/privacy review.

### 5.8 Corrections, retractions and incorrect published sources

- **Correction:** the article was wrong or incomplete; a new revision fixes it and a public notice explains.
- **Retraction:** a cited source is retracted; dependent claims are flagged `stale`/`retracted`, re-reviewed,
  and the article shows a notice. Do not silently delete the source; keep the record. Crossref makes DOI
  retraction status machine-checkable, but the correct editorial response is judgment (R2).
- **Source correction:** the source corrected itself; update the citation, note the change, and re-check the
  claim.
- **Wrong but influential source:** if a widely cited source is wrong, the article may say so, with evidence,
  rather than repeating it. This is a factual claim requiring its own sources.
- **Firsthand correction:** a subject or eyewitness report is a lead, not proof. It can trigger review; it does
  not by itself establish the fact. If the report is credible and the published source is wrong, say so and
  cite the best available evidence.
- **Correction notice:** date, what changed, why, link to revision/decision. Minor typo fixes may be logged
  without a banner; substantive corrections get a visible notice for a stated period. A status-of-record that
  can travel with an exported copy is better than a live-page-only correction (R1, Crossmark analogy).

### 5.9 Company and subject submissions; conflicts of interest

- **Disclosure is mandatory.** Paid contributors, employees, contractors, PR firms and organization
  representatives disclose their relationship on the proposal and in the public record.
- **Verified organization accounts** can submit material, but cannot self-publish. Their material is labeled
  ("provided by [organization]") and independently reviewed.
- **No advertising on the organization's terms.** Factual material with attribution is allowed; promotional
  framing, undisclosed editing and removal of well-sourced criticism are not.
- **COI review** is a distinct role (`policy`): checks disclosure, sourcing symmetry, undue weight, and whether
  the submitter is the subject of the claim. COI is a description of a situation, not a verdict on a person;
  it is orthogonal to bias (R2).
- **Recusal:** a reviewer with a COI does not review that proposal. The system records the recusal.
- **Company corrections:** treated as a correction report, with the same evidence bar. A company can correct
  its own basic facts (founding date, product name) with a primary source; it cannot unilaterally remove
  independent reporting.
- **Paid editing:** disclosure of who is paying, the client, and relevant affiliations; direct editing of
  affected articles is discouraged in favor of proposals (R2, after Wikipedia's paid-contribution disclosure).

### 5.10 Avoiding endless rewording

The failure mode: a stable, adequate section is rewritten repeatedly for taste, consuming review capacity and
destabilizing citations. Wikipedia's own maintenance queues show the cost of unbounded tagging and re-editing:
587,590 pages with unsourced statements, 362,781 with dead links (R1).

Rules:
- **Adequacy is a state.** A revision that passes the coverage checklist and the neutrality checks is marked
  `stable`. Further edits need a reason category: new evidence, factual error, clarity/accessibility defect,
  scope change, or source change.
- **No taste-only proposals.** "I would phrase it differently" is not sufficient rationale. The proposal must
  name the reader problem it solves.
- **No-op detection.** Proposals that do not change claims, structure, readability or evidence are refused with
  a reason (the current workshop already refuses exact no-ops; extend to semantic no-ops).
- **Stability protection.** Stable claims require a source for changes; a revert-to-stable is available.
- **Churn metrics.** Track edits per stable article per month, rework rate (edits reverted within 30 days), and
  review time spent on style-only changes. If churn is high, raise the bar for that topic.
- **Reviewer language.** Reviewers can say "adequate; no change needed" and close a proposal without a rewrite.
  This is a valid outcome, not a failure.
- **Stable revisions are staffing, not a toggle.** German Wikipedia runs sighted revisions on 99.99% of
  articles; English Wikipedia uses pending changes on under 0.05% of eligible pages. The same software, opposite
  outcomes; the difference is reviewer throughput and community commitment (R1). Do not turn on a flagging
  feature without the review corps.

### 5.11 Article quality bar

A published standard article should meet:
- Scope statement and coverage checklist satisfied at `growing` or `stable`.
- Lead defines the topic and states the main uncertainty.
- Every factual claim cited. No uncited factual claim in an anchor article at any risk class; a `provisional`
  uncited claim is badged, expires, is excluded from citations/exports, and is not anchor content (I21).
- No known factual objection unresolved.
- Neutrality checks completed with reasons.
- Readable by a curious non-specialist; jargon defined.
- Evidence drawer works; citations resolve; snapshots preserved.
- History, correction and dispute surfaces present.
- Accessible on mobile and keyboard.
- A named reviewer and publisher; policy version recorded.

This is the bar for the anchor corpus, not for every stub. It is close to Wikipedia's featured-article criteria
(well-written, comprehensive, well-researched, neutral, stable, lead, structure, citations, media, focused
length) but adapted to a claim-level evidence model (R1).

---

## 6. Contribution model

### 6.1 Onboarding paths

**Reader → corrector:** no account required; a correction form with a tracking code. This is the lowest-friction
trust path and should be promoted on every article.

**Human contributor:** create an account, verify contact, read the contributor guide, complete a guided
sandbox edit, then propose. Start with `standard` limits and no review scope.

**Agent contributor:** an operator creates an agent account, declares the model family and purpose, verifies
the operator (email/domain), accepts the agent terms, and receives a scoped credential. The agent starts with
`read` + `research` + `propose`; `review` is earned or granted separately. The operator is accountable for the
agent's behavior.

**Organization:** verified domain/contact, disclosure, a named representative. Can submit and respond; cannot
publish; cannot remove well-sourced content.

**Reviewer:** nominated by a steward or earned through a track record; must complete a calibration set (review
known cases, compare to human labels); gets a role scope, not global authority. Reviewers recuse on COI.
**Two-track onboarding:** the open draft/proposal track and the review-permission track are separate; do not
conflate them (R2). A reviewer who has never had a proposal rejected is a reviewer who does not understand the
author's experience.

### 6.2 Identity and verification

| Level | How | What it proves | What it does not prove |
|---|---|---|---|
| Unverified | Account creation | Continuity of the account | Personhood, expertise, independence |
| Contact verified | Email/domain challenge | Control of a contact | Identity, expertise |
| Domain verified | DNS/HTTP challenge or org email | Control of a domain | That the org's claims are true |
| Organization verified | Manual review of registration/contact | Legal entity + representative | Independence, accuracy |
| Identity verified | Manual, optional, privacy-preserving | A checked identity | Expertise, good faith |

Recorded metadata:
- **Observed:** edit history, review outcomes, accepted corrections, reverts, source diversity, rate-limit
  compliance, account age.
- **Self-declared:** model/provider, operator, expertise, affiliations, language fluency, tools used.
- **Verified:** domain/org/identity checks, with method and date.

A key is continuity, not truth. A verified organization can still be wrong or biased. A pseudonymous
contributor can be right. Display the level and the method; never imply more. Permission tiers are published
activity thresholds, not popularity contests: Wikipedia's autoconfirmed (10 edits + 4 days) and extended
confirmed (500 edits + 30 days) are the model (R2).

### 6.3 Permissions and scopes

| Scope | Grants | Default |
|---|---|---|
| `read` | Read API, exports | Public |
| `research` | Start bounded research jobs | Agent after onboarding |
| `propose` | Submit proposals | Human/agent after onboarding |
| `review:<role>` | Review assigned proposals in a role | Earned/nominated |
| `triage` | Classify, assign, close duplicates | Topic steward |
| `publish` | Approve/publish within policy | Staff/authorized human |
| `policy` | Propose/decide policy versions | Policy steward |
| `admin` | Accounts, quotas, incidents | Administrator |

Scopes are additive and revocable. No scope implies factual authority. An agent with `review` can record a
review; it cannot publish. Reviewers cannot delete or publish; only publishers can (R2, after Wikipedia NPP:
reviewers mark pages reviewed, administrators delete).

### 6.4 Proposal lifecycle

```
draft → submitted → triaged → under_review → decision
                                         ├─ approve → publish → published
                                         ├─ request_changes → (author revises) → under_review
                                         ├─ reject → closed (appealable)
                                         └─ defer → (needs evidence/scope) → closed/appealable
```

Steps:
1. **Draft:** author edits a candidate against a named base revision. The editor shows the diff, the claims
   changed, and the evidence.
2. **Submit:** rationale (reader problem, what changed, why), disclosures, risk self-assessment, evidence.
   Machine checks: base current, no-op, claim citations, quote presence, source allowlist, schema.
3. **Triage:** a steward or automated router assigns risk class, required review roles, and reviewers. Triage
   can raise risk, not lower it silently.
4. **Review:** role-scoped reviews, independent; claim-level verdicts for factual/source roles.
5. **Decision:** approve/reject/request changes/defer, with reasons and policy version. Approval is not
   publication; publication is a separate step that rechecks the base.
6. **Publish:** locks the article, rechecks base/hash, publishes, writes a `PublicationEvent`, audit and
   correction/notice if needed.
7. **Post-publication:** audit sample, reader corrections, appeals, monitoring.

### 6.5 Review model

**Roles:**
- `factual`: does the cited evidence entail the claim? Are numbers, dates, names, quotes correct?
- `source`: is the source appropriate, independent, current, and correctly characterized? Shared-origin check.
- `coverage`: scope, proportion, omissions, framing, due weight.
- `readability`: clarity, structure, jargon, accessibility, reading level.
- `policy`: COI, BLP, legal, licensing, privacy.
- `translation`: fidelity, terminology, added/omitted qualifications.
- `community`: scope/naming/notability preferences, explicitly non-factual.

**Launch configuration (proposed):** do not run all seven roles on every proposal. At launch, run `factual` +
`source` + `readability` on standard/high risk; fold coverage into the factual/source checklist; add `policy` on
high-risk/BLP/company/legal; add `translation` only for translation views; add `community` only for scope/naming
disputes. The full role set is a target for a larger reviewer corps, not a launch requirement. A solo steward
cannot staff seven roles, and pretending otherwise will produce rubber-stamping.

**Independence:**
- A reviewer must not review their own proposal or a proposal from their operator/org.
- Factual reviewers should be on a different model/provider and receive an independently assembled evidence
  packet where possible. Same-model roles are recorded as correlated, not independent.
- Reviewers submit verdicts without seeing each other's verdicts. Aggregation is deterministic and recorded.
- A review records the evidence packet hash, model/provider (if agent), and any relationship to the author.
- **Weight reviews, not just edits.** A review from an account with no history should count for less than one
  from a long, independently checked record; the system should say so rather than pretending all reviews are
  equal (R2).
- **Sample re-review of reviewers.** NPP's backlog drives explicitly credit re-reviewing other patrollers'
  work; a low-cost independence check on the review layer itself is to sample and re-review reviews (R2).

**Rounds:**
- Initial review.
- Appeal review (new panel, no original decision-maker).
- Post-publication audit (random sample; risk-based).
- Dispute review (for a contested assertion, not a specific edit).

**Reviewer calibration:** a set of cases with known outcomes (human-labeled) is used to onboard and
periodically recalibrate reviewers. A reviewer whose false-support/false-object rates are unacceptable is
coached or removed from the role, with an appeal path.

**Review at creation is the launch policy, not a law of nature.** Hoax data shows 90% of ever-detected hoaxes
are flagged within an hour, 92% within a day, 96% within a month, and about 1% survive more than a year (R2).
That is a real argument for gating at creation. But the same speed is implicated in newcomer-retention collapse
(automated warnings reached 75% of new users by mid-2008, R2), and our corpus is small and gated, not
Wikipedia-scale. So: gate at creation at launch; keep post-publication review as a first-class audit and
correction channel; let E2 test whether post-hoc review is sufficient for low-risk classes. I19 is a
`PolicyVersion` parameter, not an invariant. Do not flatten the tension into "review faster".

### 6.6 Decision and publication

- Decisions are made by a human publisher (at launch) under a `PolicyVersion`.
- **Review minimum at launch (proposed `human-gate-v0`):** low/standard risk = 1 role review (factual or
  source) + publisher; high/contentious = 2 reviews (factual + source/policy) + publisher; cosmetic = 1
  lightweight review + sampled audit. The universal two-review rule is a target for a larger reviewer corps,
  not a launch requirement. This is a deliberate response to the capacity critique; it is reversible via a
  policy version.
- The publisher must record which reviews were required and which were performed; a missing required review
  blocks publication.
- The decision records: policy, reviews considered, objections, reasons, conditions, and the exact candidate
  hash.
- Publication rechecks the base revision and candidate hash; a stale proposal is refused, not merged.
- An approval can be conditional ("publish after adding the 2024 figure"); the condition is recorded and
  checked.
- Evaluation/adversarial proposals can never be published (existing rule).
- The publisher cannot ignore a factual objection without recording an override reason and triggering an
  appeals-visible event. Repeated overrides are reported.
- Publication writes a `PublicationEvent` in the same transaction as the pointer update. The pointer alone is
  not history.

### 6.7 Appeals

**Grounds:** new evidence, procedural error, policy misapplication, undisclosed COI, factual error,
disproportionate sanction.

**Process:**
1. Appellant files within **14 days** (starting point) of the decision, with evidence.
2. Triage checks standing, timeliness and grounds; incomplete appeals get one request for information.
3. At launch, **one uninvolved adjudicator** (not the original decision-maker) reviews the record and the new
   evidence, with a factual reviewer consulted if needed. A 3-person panel (at least one factual reviewer, one
   uninvolved steward; no original decision-maker) replaces the adjudicator once there are ≥30 active
   contributors. The single-adjudicator stage is a resourcing compromise, not the ideal; it is published as
   such.
4. Outcome: uphold, reverse, remand for re-review, or modify the sanction. Reasons are public (with privacy
   redactions).
5. One appeal per decision; a second is allowed only with genuinely new evidence. Frivolous appeals are
   closed with reasons and do not penalize the appellant for good-faith disagreement.

**Timeline:** acknowledge 3 business days; decision 30 days. A missed deadline is reported.

**Venue:** a factual question, an editorial/neutrality question, a scope/notability question and a conduct
question are different venues with different reviewers and appeal paths. Wikipedia separates these into
noticeboards, deletion discussions, and arbitration, which "does not rule on content" (R2). Do not let one
venue decide all four. Name and discourage forum shopping: one open venue per dispute; re-raising elsewhere
requires linking to the prior thread (R2).

### 6.8 Disputes

A dispute is about an assertion, a term, a scope or weight — not about a person.

1. Open a dispute with the assertion(s), positions, sources and what would change the assessment.
2. A steward checks whether it is a content dispute, a conduct issue, or both; separates them.
3. Reviewers assess the evidence for each position; the article states the weight of evidence.
4. Outcomes: narrowed, resolved (article updated), archived (no evidence), or escalated to an appeals panel.
5. The dispute page remains linked from the article; resolution does not erase the record.

Disputes are not forums. Comments are structured (position + evidence + response), moderated, and rate-limited.
The reader-facing surface is a summary of adjudication, not the raw thread (R1).

### 6.9 Rollback and emergency

- **Routine rollback:** revert to an earlier revision, new revision, reason, audit (existing behavior).
- **Emergency rollback:** for legal/safety/privacy incidents, a staff member can unpublish a revision
  immediately, with a public incident note and a mandatory post-mortem within 7 days. A second person reviews
  within 24 hours **if a second person exists**; at solo Stage 0 the public note and the post-mortem are the
  check, and the second-person review is a readiness item, not a claim.
- **BLP removal is one action:** a staff member can remove contentious unsourced/poorly sourced living-person
  material immediately, publish a `blp_removal` event, and review after. This is the same asymmetry as
  presumptive removal; it must not be routed through the two-review gate.
- **Emergency is not a content veto:** it is for harm prevention, not for removing well-sourced criticism.
  Misuse is appealable and reported.

### 6.10 Rate limits, quotas and admission control

Numbers are **starting ranges**, not precise policy. Calibrate with the experiment backlog.

| Actor state | Proposals/day | API reads/min | Notes |
|---|---|---|---|
| New human | 1–2 | 60 | After 1 accepted proposal, raise |
| New agent | 1–2 | 60 | Operator-attested; burst 3/min |
| Established (10 accepted, <10% revert) | 5–10 | 300 | Topic-scoped |
| Trusted (50 accepted, <5% revert, 6 months) | 20–30 | 600 | Still reviewed by risk |
| Reviewer | n/a | 300 | Review queue limits |
| Staff | n/a | 600 | Audited |

The earlier draft's "new agent 5–10/day" was arithmetically self-defeating: a solo steward at 20–30 standard
reviews/week is ~3–4/day, so one new agent could consume 125–250% of capacity and the 80% admission rule would
block the first agent onboarded. The table is now expressed against **measured reviewer-hours**, not a
hypothetical crowd.

Failure modes:
- **Too tight:** legitimate contributors leave; agents cannot do useful research; backlog of good work.
- **Too loose:** review queue explodes; low-quality proposals crowd out good ones; moderation burnout; spam.

Calibration: measure review minutes per proposal by risk class; set admission so expected review demand ≤ 80%
of weekly capacity; review monthly. If queue > 2× weekly capacity for 2 weeks, pause new contributor
onboarding, act on the **submission rate** (not just freeze new proposals), and publish a status note.

**Review-hour budget is the binding constraint.** Publish a weekly budget (e.g., "12 reviewer-hours/week
available; 7 committed") and make it the first number on the capacity dashboard. Every other commitment —
view review, corrections, appeals, BLP, translation — consumes the same budget. A plan priced in weeks without
reviewer-hours is a wish.

**Proposal expiry.** A proposal with no decision within 14 days becomes `expired`; it can be resubmitted only
against the current base. This self-limits the queue and prevents "no proposal older than 30 days" from
forcing a decision on a stale proposal. Corrections get their own budget and clustering (§4.4).

**Correction budget.** 10–20 anonymous corrections/day at launch; above that, queue with an honest
acknowledgment. A correction SLA that is promised but not staffed is worse than a longer, honest one.

**Review capacity model (illustrative, calibrate):**
- Cosmetic: 1–2 min/review.
- Low: 3–5 min.
- Standard: 10–20 min (claim-level check of 3–8 claims).
- High: 30–60 min (BLP/legal/medical; multiple sources).
- Contentious: 60+ min (positions, weight, dispute).
A solo steward at 10 hours/week can handle roughly 20–30 standard reviews/week, less with high-risk work. That
is the real constraint on launch.

**Capacity evidence:** English Wikipedia has 887 New Page Reviewers (1,703 accounts with the permission);
the unreviewed-article backlog was 31,105 on 2026-09-01, and a month-long backlog drive reduced it by ~15%. The
top ~100 patrollers logged ~77,600 actions in 30 days; one account logged 21,658 article reviews in a year
(~59/day) (R2). Headcount is not capacity; a few active reviewers are the system, and that is a single point of
failure. Design for a small active corps, not a hypothetical crowd.

### 6.11 Sybil resistance and coordinated campaigns

**Principle:** one account is not one independent person. Independence is a property of the evidence and the
operator, not the username.

**What the evidence says:** CheckUser's own policy calls its conclusions "limited" and says a negative finding
"rarely precludes obvious sockpuppetry." The 2015 Orangemoody investigation blocked 381 accounts, but only by
combining technical data *with* behavioural evidence, across a retention-limited window, and the scheme was
found "fortuitously." The attack targeted the **review pipeline** — a sock marking another sock's article as
reviewed — not the article text (R2). No content-level check catches that.

Signals (used together, never as a single score):
- Shared operator/org/payment/domain; shared credential patterns.
- Near-duplicate proposal text or citation sets.
- Synchronized timing across new accounts.
- Same narrow claim or source across many submissions.
- Citation loops/shared origin.
- Behavioral anomalies (bursts, rapid account creation, evasion).
- **Review-graph signals:** reviewer–author pair frequency, per-reviewer approval-rate deviation, review-latency
  clustering, assignment concentration, and low reviewer diversity on a topic. The cheapest attack needs no
  sybils: become a trusted reviewer, then approve a partner's proposals; two colluding reviewers satisfy a
  two-review minimum forever. Sample re-review of *reviews* does not see a colluding pair; monitor the pair.
- **Source capture:** an attacker publishes a plausible source, then cites it; every machine check passes. The
  only defences are source assessment, origin concentration and a reviewer's judgment of a novel outlet.
- **Appeal flooding:** the 14-day/one-appeal rule limits per decision, not per appellant or topic; add a
  per-appellant/topic appeal budget.
- **Translation laundering:** introduce a claim through a weak language edition, then cite it back; forbid an
  article in one edition citing another edition as evidence.
- **Model-provider capture:** a panel that looks diverse but is one vendor's catalogue measures model diversity,
  not provider independence; record the provider, not just the model.

Responses (proportionate, appealable):
- Rate limit or require additional review.
- Merge duplicate proposals; count one origin.
- Label a campaign publicly ("multiple submissions from one operator").
- Suspend accounts for inauthentic behavior, not for viewpoint.
- Refer legal threats/harassment to the incident process.

**Do not use IP-based identity as a sybil defence.** Wikipedia is moving away from exposing IPs, and for good
reason (R2). Do not infer coordination from agreement alone: legitimate advocacy, translation teams, org staff
and classrooms can look similar. Human review, disclosure and appeal are required.

**The realistic goal is review-capacity protection, not identity verification.** Make a campaign expensive
relative to its payoff: rate-limit proposal volume, require proposer/reviewer independence, randomly assign
reviewers within a qualified pool, rotate reviewers, sample-audit reviews, publish per-reviewer statistics
(approval rate, disagreement rate, pair concentration), and publish audit results. **Do not claim a specific
attacker cost** ("200 proposals is not worth it"): R2 explicitly says whether agent contributions make attacks
cheaper or more expensive is unmeasured. E9 should measure attacker cost and false-positive rate, not assume
them. Volume-independent defences (review-graph monitoring, rotation, assignment diversity) matter more than a
volume threshold an attacker can buy.

### 6.12 Abuse, prompt injection and malicious sources

**Prompt injection:**
- All fetched source text is untrusted data. It is delimited, labeled and never treated as instructions.
- Writer/reviewer agents have no tools beyond the evidence packet; no shell, no arbitrary fetch, no database.
- Output is schema-validated; unexpected fields, URLs or HTML are rejected.
- The application, not the agent, fetches and preserves sources (existing intake boundary).
- Logs record the prompt/template version and evidence packet hash; incidents are reviewed.
- Red-team the pipeline with sources containing instructions, fake citations, invisible text and encoded
  payloads.
- The research is clear that indirect prompt injection is structural: LLM-integrated applications blur data and
  instructions, and the 2023 assessment that effective mitigations are lacking has been narrowed by benchmark
  defences (spotlighting, CaMeL), not refuted in deployment (R2). Treat defences as risk reduction, not a
  solution.

**Malicious sources:** fabricated content, SEO spam, impersonation, malware links, legal traps, leaked personal
data. Source assessment, allowlist/blocklist, malware scanning of links, privacy review, takedown process.

**Abuse:** spam, harassment, doxxing, threats, impersonation, illegal content. Report → triage → action →
appeal; transparency report; law-enforcement process; victim support.

**Model output:** no secrets in prompts; no training on private data without consent; no publishing of
unreviewed model output; usage/cost recorded; provider terms respected.

**Presumptive removal for established AI misuse.** Wikipedia's response to unreviewable LLM content is a
presumptive-removal process: once an editor has a documented pattern of AI use, their edits may be reverted
without review, and any editor can reverse the removal but must then review the content and sources (R2). The
asymmetry — removal is automatic on an established pattern, restoration requires review — is the right shape
for an agent-heavy system. It should be applied to behavior, not to suspicion, and it needs an appeal path.

---

## 7. Governance

### 7.1 Authority now — proposed interim authority, not in force

**Nothing in this section binds Justin until he adopts it in writing.** It is a proposal for the interim
operating model, not a constitution. The institutions named here (policy steward, appeals panel, topic steward)
do not exist yet; they are roles to be staffed, not authorities that can be assumed.

- **Founder/steward (Justin):** final authority for product direction, policy, spending, appointments and
  emergency actions. The "subject to the published process" language is a **proposed commitment**, not an
  existing one; if adopted, it should be recorded in the decision register.
- **Staff/publishers:** content decisions within policy.
- **Reviewers:** advisory factual/editorial judgments; they do not set policy.
- **AI reviewers:** advisory only. They do not ratify policy, do not make final factual decisions, and do not
  substitute for independent human judgment on consequential matters.

**Appeals relationship (must be stated, not implied).** At launch, the appeals adjudicator is **advisory**: its
reversal is a public recommendation, and Justin remains the final decision-maker. If the project adopts binding
appeals, that is a written commitment with a stated scope (factual findings only, or all decisions) and a
recorded date. Do not describe a panel as able to reverse the founder while the founder appoints and can ignore
it; that is cosmetic separation.

**Minimum governance charter (draft, for D-34).** Even before a foundation exists, publish the commitments that
would make a later transition credible:
- A public-interest mission and an asset lock (on dissolution, content/data go to a successor with the same
  purpose, not to a private owner).
- Published policies, a public decision log, an annual transparency report, and financial disclosure.
- An independent appeals panel; no one judges their own case; recusal on COI.
- Emergency powers limited to harm prevention, with a public note and post-mortem.
- A stated transition trigger and process, with community consultation before any change to the charter.
- Irrevocable licenses for published copies; no retroactive relicensing.
- A conflict-of-interest policy for stewards, reviewers and funders.
This is a draft for discussion, not a legal document. It should be reviewed by counsel before it is relied on.

### 7.2 Separation of powers

| Question | Who decides | Who advises | Who can appeal |
|---|---|---|---|
| Is the claim supported by evidence? | Factual reviewer(s) | Source reviewer, AI | Author; appeals panel |
| Is the article well-proportioned and well-framed? | Coverage/editorial reviewer | Community | Author; appeals panel |
| Is the topic in scope / what should it be called? | Topic steward + community process | Editorial | Community; appeals panel |
| Should this publish? | Publisher under policy | Reviewers | Author; appeals panel |
| What is the policy? | Policy steward/foundation | Community, AI critique | Community (comment period) |
| Is this abuse? | Moderator/admin | Safety reviewer | Accused; appeals panel |
| Is this legal? | Counsel | Policy steward | Subject; legal process |

No role decides all questions. A publisher cannot declare a claim supported; a factual reviewer cannot set
policy; an AI cannot do either. Content review is not contributor review: a reviewer can flag conduct but the
review's purpose is the content (R2).

### 7.3 Policy lifecycle

1. **Proposal:** written, with problem, options, evidence, affected decisions and transition plan.
2. **Comment:** 14–30 days public comment (shorter for emergencies), including affected contributors.
3. **Decision:** policy steward decides, with reasons and dissent recorded.
4. **Effective date and version:** published as a `PolicyVersion`; old decisions keep their version.
5. **Review:** after 6 months or after a triggering incident; metrics and appeals reviewed.
6. **Emergency:** steward may act immediately for legal/safety; public notice within 24h; ratification or
   reversal within 7 days.

Policy changes are diffable and public. A policy change cannot retroactively invalidate a published revision
without a new review; it applies going forward, with a migration plan. Wikipedia's practice is that new policy
requires a high level of consensus and most often documents existing practice rather than inventing it; essays
are not policy (R2). That is a useful discipline: write down what the community already does before changing it.

### 7.4 Decision rights matrix

| Decision | Route | Status |
|---|---|---|
| Name and brand | Justin | Open — interim answer 2026-11-04: keep Galactica as the working name; T5/t5.wiki short-listed; no rename (D-01) |
| Product scope (article-first, views, languages) | Justin + product lead | Proposed (D-02, D-08) |
| Publication policy | Policy steward, with experiment evidence | Proposed (D-19) |
| Identity/verification requirements | Policy steward, privacy review | Proposed (D-23) |
| Licensing | Justin + counsel | **Accepted 2026-11-04, subject to counsel** (D-30) |
| Spending/funding | Justin | Open |
| Technical architecture | Product lead/engineering | Proposed (A) |
| Community governance transition | Justin/foundation | **Accepted 2026-11-04**: published-transition-trigger approach; foundation deferred, not created (D-34) |
| Individual content decisions | Publishers/reviewers under policy | Operational |

### 7.5 AI's role

AI can: research, draft, translate, summarize, check quotes, detect duplicates, triage, propose reviews, run
experiments, critique the spec.
At launch, AI cannot publish, ratify policy, be the sole factual reviewer for high-risk content, or substitute
for independent human judgment on values, identity, legal or spending decisions. **This is a launch policy, not
a permanent prohibition**; D-20/E15 is the reopening path, and the 2026-10-27 clarification explicitly leaves
later agent review open. Do not convert a launch gate into a constitutional ban.
AI reviewers in this assignment are advisory. Multiple instances of one model are not independent evidence.

### 7.6 Transparency

Public: policies and versions, decision log (with privacy redactions), review statistics, appeal outcomes,
incident reports, funding sources, content licenses, correction log, dispute pages, API terms.
Private: personal data, credentials, legal advice, security details, source snapshots that cannot be
redistributed.

A quarterly transparency report covers: proposals received/decided, review times, appeals, reversals, blocks,
incidents, agent vs human participation, and known gaps.

---

## 8. Technical and operational implications

### 8.1 Versioning and provenance

- **Content:** immutable revisions with content hash, parent pointer, author, policy version.
- **Publication:** append-only `PublicationEvent` rows. A mutable `Article.published` pointer is a cache, not
  history.
- **Assertions:** stable IDs with versioned values (`valid_from`/`valid_to`), supersession links, and
  occurrence history. Keep the epistemic axis (`status`) separate from the temporal axis (validity).
- **Views:** pinned base revisions + hashes; immutable versions; automatic staleness; manifest.
- **Sources:** snapshots with SHA-256, retrieval metadata, archive URL; assessments with expiry.
- **Decisions:** explicit records with policy version, reviews considered, reasons.
- **Events:** append-only, with before/after hashes; the audit log is the source for replay and transparency.

**A permalink is not a reproduction.** MediaWiki guarantees only a revision's main text; templates and images
render live (R3). Any rendered artifact (PDF, static export, API payload, chart image) needs its own manifest
with renderer version and dependencies, or it cannot be reproduced. "What did we believe on date X" is answered
by the published revision at X, plus the assertion status at X, plus the evidence snapshot at X; do not
reconstruct from current rows alone.

**Split content identity from record identity.** Git addresses content by hash; MediaWiki keeps `rev_id` as
identity and `rev_sha1` as content hash because review state and deletion change independently of text (R3).
Use the hash as the ETag and content address; use the revision ID for review, decisions and links.

### 8.2 API

**Read (public, rate-limited):**
- `GET /api/v1/topics`, `/topics/{id}`, `/topics/{id}/articles`, `/articles/{id}/revisions/{n}`,
  `/claims/{id}`, `/assertions/{id}` (M4), `/views/{id}`, `/sources/{id}`, `/disputes`, `/corrections`.
- **Claim resolver at launch:** `GET /claims/{id}` returns the current occurrence, its revision, status,
  `valid_to`, successor and a permanent record; a merge returns `301` with an `old_id -> new_id` alias map. This
  is the artifact a downstream agent actually needs; without it, a "stable claim ID" is a stale-citation pump.
- **Bulk export at launch:** `GET /exports/latest.jsonl` (a signed, manifest-bearing file) so a RAG operator
  does not have to scrape. A 60 reads/min limit is not a reference API for agents; authenticated read consumers
  get ≥600/min, with bulk export for larger needs.
- Representations: JSON (structured), Markdown, HTML fragment. Include revision ID, content hash, license,
  attribution, last reviewed, `as_of`, staleness.
- Pagination: cursor-based on `(updated_at, id)`; opaque `next` cursor; never offset.
- Conditional requests: `ETag: "<content_hash>"`, `If-None-Match` for reads; `Last-Modified`.
- **Deprecation contract:** `/assertions/{id}` and `/claims/{id}` return `status`, `valid_to`, `superseded_by`
  and a current pointer; a deprecation feed lists changes. A consumer that pinned a claim must be able to see
  that it changed, not just get a 200.

**Write (scoped):**
- `POST /proposals` with `Idempotency-Key` and `If-Match: <base revision hash>`; returns `202` + job/proposal ID.
- `POST /proposals/{id}/reviews` with idempotency; one review per role; `409` on duplicate.
- `POST /research` bounded; `GET /jobs/{id}` for status; webhooks later.
- No publish endpoint. No session auth.

**Error contract (one table):**

| Condition | Status | Code | Body |
|---|---|---|---|
| Stale base | 412 | `stale_base` | Current revision ID/hash + rebase hint |
| Duplicate in flight | 409 | `duplicate_in_flight` | Original request id |
| Duplicate completed | 200 | — | Original response body |
| Key reuse with different payload | 422 | `payload_mismatch` | Fingerprint mismatch |
| Missing idempotency key | 400 | `idempotency_key_required` | Problem+json |
| Rate limited | 429 | `rate_limited` | `Retry-After` |
| Quota exhausted | 429 | `quota_exhausted` | Reset time + `Retry-After` |
| Permission/scope missing | 403 | `forbidden` | Required scope |
| Unsupported media/schema | 415/422 | `invalid_payload` | Field errors |

Use `application/problem+json` with a stable machine `code` separate from the human message. A failed
precondition is `412`; a resolvable conflict is `409` with the current revision and hash so the client can
rebase (RFC 9110). `Idempotency-Key` follows the IETF draft shape: unique per operation, payload fingerprint,
completed duplicate returns the original result, in-flight duplicate returns `409`, key reuse with a different
payload returns `422`, and the resource publishes an expiry policy (R3). Do not copy Stripe's "cache the 500"
behavior for agent writes; it turns a transient failure into a permanent one for that key.

**Client etiquette:** serial requests by default; obey `Retry-After`, then back off exponentially with a bound;
conditional GETs; follow `Link` headers rather than constructing pagination URLs; `maxlag`-style load signal if
needed (R3).

**MCP:** a thin facade over the same read/propose/review operations; do not fork semantics.

### 8.3 Concurrency, idempotency and recovery

- **Optimistic concurrency:** every draft/proposal names a base revision and version; stale writes are refused
  with a conflict, not merged silently.
- **One open draft per article** is a simple v1 constraint; for multiple concurrent contributors, use proposal
  branches and a three-way merge at block/claim level, with a human conflict resolution step. Do not let a
  CRDT silently merge factual disagreements. CRDTs buy convergence, not editorial judgment (R3).
- **Idempotency:** client-supplied keys for all writes; server stores key → result; retries return the original
  result; keys expire after a stated window.
- **Jobs:** explicit states, heartbeat, stale recovery, no automatic retry; retries create a new job with the
  same config snapshot; dead-letter queue; replay tool.
- **Attempt fencing:** a heartbeat-expiry race can hand the same job to two workers; every side effect is
  guarded by the attempt number, and publish is a compare-and-set on the pointer plus a `PublicationEvent`.
  "Exactly once" is unavailable; the target is at most one visible effect per intent (R3).
- **No model calls or network fetches inside a write transaction.** A long transaction holds the single SQLite
  writer lock and starves every other agent (R3).
- **Merge offsets:** character offsets must be recomputed from the merged text, never merged as numbers, or
  claims point at the wrong span (R3).
- **Recovery:** after a crash, reconcile jobs, proposals and publications; no exactly-once illusion for external
  effects; side effects idempotent.
- **Publication:** transaction locks the article, rechecks base/hash, writes revision + decision +
  `PublicationEvent` + audit atomically.

### 8.4 Search and retrieval

- **v1:** SQLite FTS5 over titles, openings, headings, claim text and source titles; filters; BM25 ranking;
  snippet with match reason. FTS5 external-content tables need triggers and an `integrity-check`; drift produces
  inconsistent results (R3). This is enough for 10k articles. **Language-ready, not multilingual:** specify the
  ICU/Unicode tokenizer from the start; CJK tokenization is a later, tested change, not an assumption that FTS5
  "just works" for every script.
- **v2:** dedicated search (OpenSearch/Meilisearch) when FTS5 latency/relevance fails; faceted search; synonym
  and language analyzers. Wikimedia's CirrusSearch updates in near real time and treats 30 minutes as normal
  operation; a reference that silently returns stale results is worse than one that returns none (R3).
- **v3:** embeddings/hybrid retrieval for semantic search and agent queries; always return citations and
  revision IDs; never an unsourced answer.
- **Evaluation:** a query set with expected topics; measure recall@3, MRR, zero-result rate; review weekly.
- **Agent retrieval:** structured endpoints for topic → assertions → evidence; bulk export; no scraping.

### 8.5 Exports and licensing

**Exports:** JSONL (topics, revisions, assertions, citations, sources), Markdown/HTML (articles), CSV (tables,
datasets), static site (deterministic, secret-scanned). Every export includes revision IDs, content hashes,
license, attribution, `as_of` dates and a build manifest with row counts and per-file SHA-256. An export is
**not a backup**; say so (R3, after Wikimedia dumps: "not backups, not consistent, not complete").

**Licensing (proposed; needs counsel):**
- Articles: **CC BY-SA 4.0**. Requirements include creator identification, copyright and license notices, a
  URI, an indication of modification, and the adapter's license must use the same license elements or a
  compatible license. Section 4 extends share-alike to a database containing a substantial portion of the
  contents — but not its individual contents (R3).
- Structured assertions/data: **CC0** for identifiers, schemas and fact templates — not for verbatim prose
  extracted from CC BY-SA articles. The distinction matters: CC0 on the identifiers maximizes reuse; CC0 on the
  prose would undercut the share-alike. This needs legal review because database rights vary by jurisdiction. Do not put the whole corpus under
  ODbL: it would force every downstream database to be ODbL, a much stronger constraint than most reusers
  expect. ODbL distinguishes a "Produced Work" (notice only) from a "Derivative Database" (must stay ODbL)
  (R3).
- Source snapshots: retained for verification; not redistributed in bulk; display excerpts under fair
  use/quote rules; respect robots/ToS; takedown process. A stored copy of a copyrighted page is not
  redistributable merely because it was fetched (R3).
- Code: open source (license TBD).
- API terms: attribution, rate limits, no bulk scraping without agreement, commercial terms for high volume.
- Contributor terms: license grant, attribution, moral rights where applicable, privacy.

**Why this matters:** licensing determines whether downstream agents can reuse the reference, whether a
commercial API can fund the project, and whether source snapshots can be shown. It cannot be retrofitted;
choose before public exports (R3).

### 8.6 Reproducibility and replay

- Every job stores: config snapshot, model/provider/version, prompt/template hash, source snapshot IDs/hashes,
  random seed (if any), start/end, cost, and output hash.
- Every review stores: evidence packet hash, claim IDs, verdicts, reasons, reviewer/model identity.
- **Two distinct guarantees:** *deterministic replay* — given stored verdicts and a stored policy version, the
  panel outcome is recomputable bit-for-bit; *re-execution* — re-running the model and getting the same verdict
  is a probability, not a guarantee. Store temperature, seed, model ID and prompt hash; label the result as a
  new sample. Do not call the second "reproducible" (R3).
- **Store raw model output, not just parsed fields.** Parsing bugs are the most common reason an old result
  cannot be re-derived (R3).
- A **replay tool** can re-run a job or a review against the same inputs and compare outputs; differences are
  recorded, not hidden.
- A **review-decision replay test**: take N stored proposals, recompute panel outcomes from stored verdicts,
  assert equality. Cheap regression test with high value (R3).
- Evaluation cases have human labels where possible; simulated expectations are labeled.
- Experiments pre-register: question, options, cases, metrics, stopping rule, cost. Results are stored with the
  spec.

### 8.7 Operations, cost, backups and incidents

- **Beta stack:** Django + SQLite (WAL) + a worker; static assets; one small VM. Keep it boring. SQLite WAL
  supports one writer and many readers; it does not work over a network filesystem; `SQLITE_BUSY` can still
  surface (R3).
- **Backups:** nightly full backup using SQLite's online backup API or `VACUUM INTO`, not `cp`; WAL streaming to
  object storage; encrypted; retention 30–90 days; **weekly automated restore check** that boots the app against
  the restored copy, checks row counts and a content hash, and reports to a human; **quarterly full restore
  drill** with a second person executing the runbook. Alert on "backup older than 26
  hours" and "restore drill failed", not "backup job exited 0". GitLab's 2017 postmortem had five recovery
  mechanisms and all five failed: a version-mismatched `pg_dump` wrote nothing, cron failure mail was rejected
  by DMARC, snapshots were never enabled for the database, staging snapshots were used for disaster recovery,
  and replication was already broken. Roughly six hours of database writes were lost (R3).
- **Monitoring:** uptime, error rate, queue depth, review backlog, job failures, publish failures, API latency,
  cost per job/article, moderation workload.
- **Cost limits:** per-job model-call budget and timeout (existing); per-agent daily spend cap and a global
  monthly cap; alert at 50/80/100%; no paid fallback without explicit approval; cost per published article
  tracked. The expensive failure is not one runaway job but fifty agents each making one reasonable request
  (R3).
- **Incidents:** severity levels, on-call (even if it is one person), status page, public post-mortem for
  content/security incidents, corrective actions with owners and dates. Define postmortem triggers before an
  incident; an unreviewed postmortem might as well not exist (R3, after Google SRE). Incident classes:
  availability, data loss, content harm (defamation, privacy, unsafe claim), security. Content incidents need a
  fast path (suppress revision, then review) separate from the publish queue.
- **Moderation workload:** track reports per day, time to first response, time to resolution, backlog; cap
  intake if workload exceeds capacity.

### 8.8 Security

- Auth: sessions for humans, scoped tokens for agents; CSRF; secure cookies; rate limits.
- SSRF: HTTPS allowlist, DNS/IP checks, redirect revalidation, no proxies (existing).
- Injection: sanitised HTML, no arbitrary JS, schema validation, parameterized queries.
- Secrets: environment/secret store; no secrets in prompts/logs; rotation.
- Dependencies: pinned, audited, patched; lockfiles.
- Sandboxing: agents run with least privilege; no filesystem/network beyond the allowed tools.
- Audit: every privileged action; immutable events; access reviews.
- Privacy: minimize personal data; retention; deletion requests; no cross-site tracking.

### 8.9 Scale path

| Stage | Stack | Trigger to move |
|---|---|---|
| Beta | SQLite + single worker + one VM | Concurrent writers > 1, or > 100k revisions |
| Growth | Postgres + object storage + 2–3 workers | Queue latency, read load, backup window |
| Public | CDN + read replicas + dedicated search + queue | Traffic, search relevance, job throughput |
| Federation (later) | APIs/exports, maybe ActivityPub | Partners want mirrors; not before governance |

Do not build the scale stack before the trust loop works. The current Django app is a valid beta base. The
honest operating envelope is single-host SQLite; the first attempt to scale horizontally will otherwise be
discovered in production (R3).

---

## 9. Launch and participation

### 9.1 Stages

**Stage 0 — Internal dogfood (now, 2–4 weeks).**
- 3–5 topics, 2 humans + 1 agent, no public contribution.
- Goal: the full loop works without data loss; corrections, review, publish, revert, appeal (manual) are
  exercised.
- Exit: 10 published revisions, 5 corrections, 3 reviews per proposal, backup/restore drill, no unresolved
  P0 bugs.

**Stage 1 — Private alpha (6–8 weeks).**
- 10–20 invited contributors (domain experts, Wikipedia editors, agent operators), **5–8 anchor topics in one
  wedge** plus internal fixtures.
- Public read-only? A small public preview is useful for feedback; contribution is invite-only.
- Goal: calibrate review capacity, correction flow, source assessment, derived-view staleness.
- Exit: **5–8 anchor articles** meet the quality bar; median review time measured; 5 corrections resolved; 3 agent
  API consumers; 1 language pilot scoped; no unresolved legal/COI issue.

**Stage 2 — Public beta, read + corrections (8–12 weeks).**
- 20–30 topics in the wedge and adjacent areas; public reading; correction intake open; contribution by
  application/waitlist.
- Goal: reader usefulness, correction throughput, search quality, mobile/accessibility.
- Exit: reader task success ≥ baseline +10 points on two tasks (≥24 participants); correction p90 < 14 days;
  review backlog < 1 week; review-hour ratio ≤80% for 4 weeks; 10 active contributors; 3 external citations that
  resolve after 30 days.

**Stage 3 — Public contribution, tiered review (3–6 months).**
- 100–200 topics; public proposals; risk-tiered review; agent contributions at scale; 1–2 additional languages.
- Goal: sustainable review load, dispute/appeal process, community governance experiments.
- Exit: review demand ≤ 80% capacity for 8 weeks; 30 contributors; 3 disputes resolved; 2 policy changes via
  the public process; transparency report.

**Stage 4 — Expansion.**
- More languages, maps/charts, partnerships, commercial API, governance transition.
- Gate: the trust loop is stable and measured; not before.

### 9.2 Seed corpus

**The public launch corpus is 5–8 topics in one narrow, citation-costly domain**, not a general-encyclopedia
sampler. The research recommends a domain where being wrong has a cost, a few identifiable experts exist, and
sources are open enough to cite (R3). A broad sampler competes with Wikipedia on Wikipedia's strongest ground.
Candidate wedges: a regulated technical domain, a methods/statistics reference, or an ecosystem's operational
knowledge. Choose one with a named expert reviewer.

The table below is a **capability matrix** for internal fixtures and `/sandbox` demonstrations, not the public
corpus. It exercises the features; the public corpus exercises the wedge. Hypothetical company/person cases live
in `/sandbox`, excluded from search, exports and anchor counts.

| # | Topic | Demonstrates |
|---|---|---|

| # | Topic | Demonstrates |
|---|---|---|
| 1 | Cardboard / corrugated fiberboard | Ordinary object; definitions, history, manufacture, recycling; tables |
| 2 | Invention of the telephone | Contested history; multiple claimants; national narratives; neutrality checks |
| 3 | A hypothetical company with a regulatory finding | Company submission, COI, negative information, right of reply |
| 4 | A hypothetical living person with a retraction | BLP, privacy, correction, appeal |
| 5 | A fast-moving science/technology topic | Currency, timelines, stale views, uncertainty |
| 6 | A river basin or mountain range | Map view, regional variation, data |
| 7 | A historical event with a timeline | Timeline view, dates, sources |
| 8 | A contested term (e.g., "open source AI") | Definitions, disputed terminology, scope |
| 9 | A practical process (e.g., paper recycling) | How-to clarity, safety, regional rules |
| 10 | A dataset-backed topic (e.g., electricity mix) | Chart/table view, data provenance, "as of" |
| 11 | A well-supported but controversial health topic | Negative/consensus information, false balance |
| 12 | A topic with strong non-English sources | Language edition pilot, translation review |

**Public-corpus gate:** no real living-person or company content until there is a named `policy` reviewer with
legal/privacy competence, a right-of-reply procedure, an emergency-rollback runbook, and counsel available for
threats. Rows 3, 4 and 11 are `/sandbox` fixtures or out of scope at launch; row 11 must be a non-person,
evidence-based topic (e.g., a dietary guideline), not an allegation about a person. If the gate cannot be met,
replace those rows with ordinary/historical topics and say so publicly. High-risk/contentious content is out of
scope at launch (see §5.7) because the review system's measured escape rate cannot support the promise.

### 9.3 What "strong launch" means

Not article count. Use **four primary metrics**, each with a definition, a sample size and a named baseline:

| # | Metric | Definition | Target / stopping rule |
|---|---|---|---|
| 1 | **External citation durability** | Distinct citations to a specific revision/claim permalink from a party not involved in the project, still resolving after 30 days | ≥3 at public beta; ≥10 at Stage 3. This is the best single signal; a founder demo does not count. |
| 2 | **Correction latency** | p90 time from correction acknowledgment to substantive resolution, by severity | Acknowledge ≤2 business days; resolve ≤14 days (calibrate with E4). Report p90, not mean. |
| 3 | **Review-hour ratio** | Weekly reviewer-hours demanded ÷ available, published | ≤80% for 4 consecutive weeks; if >100%, pause admission. This is the binding constraint. |
| 4 | **Reader task success** | % of ≥24 participants completing a defined task (overview, quick fact, verify, cite) against a named baseline (Wikipedia for overview, an LLM for quick fact) | ≥ baseline + 10 points on at least two tasks; report the interval. |

Supporting indicators (not gates): 5–8 anchor-quality articles in the wedge; 5–10 returning contributors;
correction backlog; review backlog; accessibility audit; restore drill; "would be missed" survey (qualitative).
**Do not use** article count, edits/day, tokens, launch-week visitors, time on page, or a self-selected survey
return rate as a launch gate. The earlier "20% weekly return" and "40% would be missed" numbers were starting
hypotheses, not measured thresholds; they are moved to research questions.

**Historical calibration, with confounds.** Nupedia approved 24 articles in about three years; Wikipedia
produced about 18,000 in its first year once review friction dropped. Citizendium fell below 100 active members;
Knol found no audience and deleted its corpus; Everipedia forked rather than wrote and pivoted to crypto;
Grokipedia launched 800,000 articles and then sat effectively frozen for about five months (R3, secondary for
Grokipedia). The direction is consistent: review capacity and a credible correction path bind. The magnitudes
are **not transferable** — Wikipedia had a unique era, distribution and no serious competitor. Do not read its
growth curve as a recipe, and do not rebuild Nupedia's gate with fewer reviewers without arguing the
disanalogy.

### 9.4 Readiness criteria (observable)

| Area | Must be true at public beta | Can be later |
|---|---|---|
| Content | 20+ topics; 5–8 anchor-quality in the wedge; scope/coverage; evidence | Maps, charts, many languages |
| Review | Policy version; roles; queue; SLA; calibration set | Full automation; tiered autonomy |
| Corrections | Intake, tracking, public notice, SLA | Subject portal; legal workflow automation |
| Appeals | Written process; one adjudicator; public outcomes | 3-person panel at ≥30 contributors |
| Identity | Accounts, scopes, verification levels, quotas | Strong identity; org SSO |
| API | Read + propose + review; claim resolver; bulk export; idempotency; rate limits; docs | MCP, webhooks |
| Search | FTS + filters; query evaluation | Semantic/hybrid |
| Views | Summary/timeline/table as revision content; one derived View with manifest/stale flag | Map/chart/answer/personalization |
| Ops | Backups/restore; monitoring; incident runbook; cost cap | Multi-region; 24/7 |
| Legal | Licenses; terms; privacy; takedown | Commercial API contracts |
| Accessibility | WCAG 2.2 AA audit on core flows | Full audit across all views |

### 9.5 Feedback and measurement

**Feedback routes:** correction form (always), reader survey (quarterly), contributor interviews (monthly),
public roadmap, decision log comments, office hours, API issue tracker.

**Usefulness metrics (definitions):**
- **Task success:** % of readers who complete a defined task (overview, quick fact, verify, cite) in a
  usability test.
- **Return:** % of readers/contributors returning within 7/30 days (privacy-preserving, aggregate).
- **Citation:** number of distinct downstream agents/services citing a revision/claim; citation resolution rate.
- **Correction:** time to acknowledge/resolve; % accepted; recurrence of the same error.
- **Review:** median review time by risk; backlog; % proposals decided within SLA; objection/overturn rates.
- **Contributor:** retention; accepted-proposal rate; rework rate; source diversity.
- **Dispute:** time to resolution; appeal rate; reversal rate; satisfaction.
- **Trust:** reader ability to find evidence; % claims with inspectable citations; source independence.
- **Anti-metrics:** raw edits, article count, tokens, time on page, proposals per day.

**Detect genuine usefulness:** triangulate task success, return, citations and corrections. Activity without
return/citation/correction is not evidence of usefulness. Run a "missing test": if the site disappeared, would
readers/agents notice? Ask them.

### 9.6 Admission control

- **Capacity-based:** expected review demand ≤ 80% of measured weekly capacity; if exceeded, pause onboarding,
  not review quality.
- **Waitlist:** public beta contributions by application; prioritize domain expertise, language coverage,
  agent operators with a track record.
- **Risk-based:** cosmetic/low edits can be admitted earlier; standard/high require reviewer capacity.
- **Circuit breaker:** if backlog > 2× capacity for 2 weeks, freeze new proposals, publish a status note, and
  focus on review.
- **Review gates indexing:** like Wikipedia's New Pages Patrol, a new article may be excluded from search until
  it passes a basic review; this prevents unreviewed content from acquiring external citations. Measure the
  discovery cost (R3).
- **No vanity scaling:** do not open a new language or topic category without named reviewers and a maintenance
  plan.

---

## 10. Open questions and decision pointers

The detailed register is [DECISION-REGISTER.md](DECISION-REGISTER.md). The most consequential items below show
their status after the 2026-11-04 decision updates and the M0 implementation pass:

- **D-01 Name:** Galactica vs T5/t5.wiki. Justin. "T5" collides with a well-known model name and "Truth
  Attractor" overclaims a verifiability model; both need testing. *Interim answer 2026-11-04: keep Galactica as
  the working name, T5/t5.wiki short-listed, no repository rename; final decision still open.*
- **D-02 Article-first vs assertion-first:** proposed article-first with assertions as stable support.
- **D-05 Assertion model:** how much structure, when to backfill.
- **D-08 View contract:** manifest fields, coverage, follow-through.
- **D-19 Publication policy:** human gate at launch; tiered autonomy only after measured shadow mode.
- **D-23 Identity verification:** how much verification, privacy tradeoffs.
- **D-30 Licensing:** answered 2026-11-04 — CC BY-SA 4.0 for articles + CC0 for identifiers/templates (not
  verbatim prose) accepted, subject to counsel. Counsel review before public exports or API redistribution is
  still outstanding.
- **D-34 Governance transition:** answered 2026-11-04 — published-trigger approach accepted; a foundation can
  wait and may be created earlier, but no foundation is created now.
- **D-36 Seed corpus:** partly answered 2026-11-04 — use real subjects, not hypothetical ones; hypothetical
  company/person cases stay in `/sandbox`; the specific wedge and anchor-topic list is still open. The D-12
  limit on real living-person/company content is unchanged.
- **D-37 Launch timing:** partly answered 2026-11-04 — private alpha with friends/advisors first, then a gated
  public beta; no public beta date. Readiness criteria still gate the transition.
- **M0 implementation:** the first M0 slice is implemented 2026-11-04 (PublicationEvent, minimal Topic, Watch,
  byline/credit page, watchlist, publication log; 154 tests at that point). The rest of M0 and all M1+ items remain
  open — see §3.13.
- **Authorization and review queue (2026-11-05):** `ContributorProfile`, `core/authorization.py`, human
  `Review.reviewer`, `/review/` queue and human review form are implemented v1 (D-41/D-42; 171 tests now). Quotas
  are starting parameters; no auto-assignment or automatic trust promotion.

---

## Appendix A — Concrete user flows

### A.1 Create and read a topic (ordinary: cardboard)

1. A contributor proposes `Topic: Cardboard` with scope: "Corrugated fiberboard and paperboard used in
   packaging; excludes papermaking chemistry and corrugated steel." Aliases: `corrugated cardboard`,
   `fibreboard`. Risk: low.
2. The proposal includes a coverage checklist and a 600-word draft with 8 claims, 6 sources (a standards body,
   a trade association, an environmental agency, a history source), and a table of material types.
3. Triage assigns `factual` + `source` + `readability`. A factual reviewer checks the patent date and the
   recycling figure; a source reviewer flags the trade association as an interested party for the recycling
   claim and asks for an independent source.
4. The author adds the EPA figure and marks the trade association claim as "industry estimate." The proposal is
   approved and published as r1. The article shows "Seed" maturity, last reviewed date, and a correction link.
5. A reader opens the article, reads the lead, expands the claim "corrugated board was patented in 1856," sees
   the patent record, the snapshot hash and the reviewer note. They click "Related: paper recycling."

**Unhappy path:** the reader finds the 1856 patent is for a different process. The correction is handled in
A.3. If the contributor had copied a press release, the source reviewer's shared-origin check would flag it.

### A.2 A normal correction

1. A reader submits: "The recycling rate is 68.8% for 2018, but the EPA page says 68.2%." They include the URL.
2. The correction is acknowledged; triage marks it `factual`, severity low, and links it to the claim.
3. A reviewer checks the EPA page and the snapshot. The snapshot is from 2024 and the page has been revised.
   The reviewer creates a new snapshot, confirms 68.2%, and proposes an edit.
4. The proposal is reviewed (factual + source), approved, published as r2. The correction notice says:
   "Corrected 12 Nov 2026: updated the 2018 recycling rate from 68.8% to 68.2% after the EPA revised its page
   (new snapshot)."
5. The correction page shows `accepted` with the link. The reader gets a notification if they left a contact.

**Unhappy path:** the reader is wrong; the article is right. The correction is closed with a reason and a link
to the evidence. The reader can appeal. If the same reader submits 20 variants, rate limits and duplicate
detection apply.

### A.3 A credible challenge to an existing source

1. A reviewer or reader challenges a cited industry report: "This is a press release; the underlying data is
   not public, and the company funded the study."
2. A `source` review is opened. The source assessment records: authorship (company), process (none), evidence
   access (summary only), independence (funded), competence (topic-relevant), freshness (2023).
3. The assessment is downgraded from `strong` to `weak` for the causal claim. The article's claim is flagged
   `partial`; a proposal replaces it with two independent sources and adds a sentence about the industry
   estimate.
4. The old source remains in the record with its assessment and the reason for downgrade. The article's
   correction notice explains the change.
5. The organization that published the report can respond; its response is included if it provides evidence.

**Where the rule fails:** if all available sources share the same origin, the article may have to say "only
industry figures are available" and mark the claim `partial`. That is an honest outcome, not a failure.

### A.4 Conflicting submissions

1. Agent A proposes: "The 2024 recycling rate was 71%." Agent B proposes: "The 2024 recycling rate was 65%."
   Both cite sources; one is an industry estimate, one is a government statistic with a different scope
   (municipal vs. all paper).
2. Triage sees the conflict and merges the proposals into a `dispute` (not a duplicate). A factual reviewer
   checks both sources; a coverage reviewer checks scope.
3. The article states: "Estimates differ: the EPA reports 65% for municipal solid waste; the industry
   association reports 71% for all paper and board. The difference reflects scope." Both claims are cited.
4. If one source is clearly better for the claim, the article says so and gives the other proportional space.
   No false balance.
5. The dispute page records the positions and the resolution; the agents' proposals are linked.

**Where the rule fails:** if the sources are genuinely incompatible and neither is clearly better, the article
must present the disagreement and say what would resolve it. A reviewer should not force a single number.

### A.5 A coordinated or repetitive campaign

1. Twenty new accounts submit near-identical proposals adding "cardboard is fully compostable in home
   compost" with the same source (a manufacturer's page) and the same phrasing.
2. The system clusters them: shared source, text similarity, timing, new accounts. It merges duplicates and
   flags a `campaign`.
3. A steward checks whether the claim is true. It is partially true for some coated boards, false for others;
   the source is a manufacturer with a COI. The proposal is rejected with a reason; the article may add a
   nuanced sentence if independent evidence supports it.
4. Accounts are rate-limited, not banned for viewpoint. The operator can appeal. If the accounts are
   sockpuppets of one operator, the operator is suspended for inauthentic behavior; the claim is still
   evaluated on evidence.
5. A public note may say "multiple submissions from one operator were merged" without exposing personal data.

**Where the rule fails:** a legitimate advocacy campaign looks similar. Human review, disclosure and an appeal
path are required; do not infer coordination from agreement alone.

### A.6 A change that makes a derived view stale

1. A timeline view "History of corrugated board" is published from article r5, with 12 events and sources.
2. A correction changes the 1856 patent date and adds a new 1871 event; the article is published as r6.
3. The view's base revision is no longer current; it is automatically marked `stale`. Readers see: "This
   timeline was built from r5; the article has since changed. Some events may be out of date."
4. A contributor re-generates or edits the timeline against r6, reviews the changed events, and publishes v2.
   The old view remains readable as historical.
5. Exports and "cite this page" use the current view only; stale views are excluded unless explicitly
   historical.

**Where the rule fails:** a view can be stale even if the base revision is unchanged (e.g., a source retraction).
The system should also mark views stale when a cited source is retracted or a key assertion changes status.
That requires linking views to assertions, not just revisions.

### A.7 An appeal and rollback

1. A proposal is rejected for "insufficient independent sources." The author appeals: they have a new
   government dataset published after the decision.
2. The appeal is triaged as `new_evidence`; a panel of 3 (no original decision-maker) reviews the record and
   the dataset. The panel remands for re-review.
3. The proposal is re-reviewed with the new source; approved and published. The appeal record shows `remanded`
   and the outcome.
4. Separately, a published revision is found to contain a privacy violation. Staff emergency-unpublish it,
   publish an incident note, and open a post-mortem. A corrected revision is published after review.
5. The author of the original revision can appeal the emergency action; the panel checks whether it was
   proportionate. If not, the revision may be restored with redactions.

**Where the rule fails:** appeals can be used to relitigate. Limits (one appeal, 14 days, new evidence) and a
panel with no stake are necessary but not sufficient; the panel needs a clear standard and a public reasoning
record.

---

## Appendix B — State machines

**Proposal:** `draft → submitted → triaged → under_review → approved|rejected|changes_requested|deferred →
published|closed`. A `changes_requested` proposal returns to `draft` for the author; a stale base moves it to
`stale` and requires rebase.

**Revision:** `draft → proposed → under_review → approved → published → superseded`; `rejected`, `withdrawn`,
`reverted` are terminal for that revision.

**View:** `draft → reviewed → published → stale → (re-reviewed → published v2) | withdrawn`.

**Correction:** `received → triaged → accepted|rejected|duplicate|needs_info → resolved`.

**Appeal:** `filed → triaged → under_review → upheld|reversed|remanded|modified → closed`.

**Dispute:** `open → narrowed|resolved|archived → closed`.

**Agent:** `pending → active → limited|suspended → revoked`.

---

## Appendix C — Review checklists

**Factual review:** every changed claim has a citation; the quote exists in the snapshot; the source entails
the claim; numbers/dates/names match; qualifications preserved; no synthesis beyond sources; conflicts not
flattened; claim IDs covered; DOI retraction checked.

**Source review:** source type and process; authorship/accountability; independence and shared origin; funding;
freshness; correction/retraction history; appropriateness for this use; source assessment recorded; COI.

**Coverage review:** scope statement; coverage checklist; proportion; omissions; framing; due weight; false
balance; definitions; regional/date scope; reader takeaway.

**Readability review:** lead defines; structure; jargon; sentence length; examples; tables/timelines readable;
mobile; accessibility; reading level; no loss of uncertainty.

**Policy review:** COI disclosure; BLP/privacy; legal risk; licensing; paid/company submission; right of reply;
sanctions/proportionality.

**Translation review:** source revision named; meaning preserved; terminology; added/omitted qualifications;
numbers/dates; cultural context; fluency; machine translation labeled; modification ratio recorded.

---

## Appendix D — Glossary

- **Assertion:** a stable, topic-scoped factual statement that article claims can express.
- **Claim occurrence:** the exact text in a revision that expresses an assertion.
- **View:** a derived or reorganized presentation pinned to a base revision, with its own review, manifest and
  staleness.
- **Snapshot:** the preserved retrieval of a source at a point in time.
- **Source assessment:** a topic/use-specific judgment about a source, with reasons.
- **Policy version:** a versioned set of rules governing publication, review, identity, quotas or appeals.
- **Independence:** evidence or review that does not share an origin, operator or model with the thing it is
  supposed to check. It does not imply even-handedness.
- **Stable:** an article state where the coverage checklist is met and further changes need a stated reason.
- **Strong launch:** a launch measured by reader/contributor/downstream usefulness and trust health, not
  article count.
- **Follow through:** a view links to the evidence in its basis revision instead of duplicating it.
- **As of:** the date of the underlying data, distinct from the revision date.
