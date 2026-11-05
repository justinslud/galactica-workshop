# Critique — product, reader experience and feasibility

**Reviewer:** independent critic (not the author). **Date:** 2026-11-04.
**Reviewed:** `PRODUCT-SPEC.md` v2.1, `LAUNCH-PLAN.md` v1.0, `WORKED-EXAMPLES.md`, `EXPERIMENTS.md`,
`DECISION-REGISTER.md`, `00-CURRENT-STATE.md`, the three research notes, plus `core/models.py`, `core/views.py`,
`templates/core/article.html`, `templates/core/_article_body.html` and `CURRENT.md`.
**Method:** read the documents and the code; did not run the server, tests or any experiment; changed no file
except this one.
**Verdict.** An unusually honest, well-sourced internal design document that has not decided whether it is
building a reader product or a provenance engine, and whose operating model is priced at roughly four times the
capacity it admits to having.

---

## Most consequential criticisms (ordered by severity)

1. **One new agent can out-consume the entire human review corps.** §6.10 grants "New agent: 5–10 proposals/day"
   while the same section says a solo steward at 10 h/week handles "roughly 20–30 standard reviews/week" (≈3–4 a
   day). One new agent takes 125–250% of weekly capacity. Either the quotas collapse or the 80% admission rule
   (§9.6) blocks the first agent that onboards.
2. **The corpus and the quality bar are arithmetically incompatible with the staffing plan.** At §5.11 (every
   claim cited with a snapshot, ten neutrality checks with reasons, two reviewers, accessibility), an anchor
   article is 8–20 hours of expert work. Twelve to twenty anchors is 100–400 hours; Stage 1 gives 6–8 weeks at
   10 h/week — 60–80 hours — and also demands the assertion model, correction intake, 50 timed proposals, a
   30-source assessment pilot, reviewer calibration, a usability test and a name decision. The plan is priced in
   weeks; it needs pricing in reviewer-hours.
3. **There is no return loop and no author credit** — the two mechanics the research says actually work. R3
   names "notification when a claim they care about is challenged" and "attribution and a citable revision URL".
   The spec has no watchlist, alert, digest or RSS, and §4.10 rules notifications out as "notification spam".
   §4.1's header has no byline, §3.3 gives `Article` no author field, and the shipped template shows only revision
   state and a date. An expert's reward for eight hours is a username inside a review record.
4. **The summary is both the first screen and a reviewed, auto-staling `View`.** §4.1.3 calls at-a-glance "a
   view"; V6 requires review before publish and V5 marks any base change `stale`. So every correction makes the
   top of the page say "stale", and every article needs a second reviewed artifact re-reviewed on every edit —
   against a stated constraint that review capacity binds. E5's own stopping rule ("if re-review is >2× the
   original review, the view is not worth it at launch") will trip, and no fallback decision is recorded.
5. **"Evidence one step away" is a thesis, not a design.** §4.2 lists content but does not decide the inline
   affordance (superscript? chip? underline?), whether claim text is highlighted always or on selection, what an
   uncited claim looks like to a reader, or what "challenge this source" creates (`Correction`? a `Proposal` of
   kind `assess_source`?). The shipped page is a per-block `<details>` labelled "Claims and evidence (N)" —
   block-level, the drawer readers will not open. The 0.29% click rate is used both to hide evidence and to
   justify heavy investment in it.
6. **Differentiation has no wedge.** The seed portfolio (§9.2, LAUNCH §6) is a general-encyclopedia sampler.
   R3 recommends the opposite: "a domain where being wrong has a cost, a few identifiable experts exist, and
   sources are open enough to cite." Cardboard and paper recycling are where Wikipedia is strongest; the
   telephone is a Wikipedia featured article with a 7-million-article distribution advantage; the health topic is
   the highest-risk, lowest-feasibility item in the list.
7. **The project's own measurement undermines its high-risk trust claim.** The policy lab reports 44.2% escape
   on standard and 57.2% on high-risk defects for the one-model panel, 22.3%/44.0% for a mixed panel. The spec
   uses this only to refuse autonomy; it never confronts that a mixed panel still passes roughly half of high-risk
   defects, while §5.7 promises BLP-grade care and §5.11 "no known factual objection unresolved".
8. **Governance institutions precede the community that would staff them.** Seven review roles (§6.5), a
   3-person appeals panel with a 30-day SLA (§6.7), disputes, policy comment periods, quarterly transparency
   reports and reviewer calibration — for 10–30 contributors, several of them agents. Five appeals alone need
   15 reviewer-slots. The founder must personally operate all of it until a community exists.

---

## 1. Product for a reader, or well-specified internal system?

**What is wrong.** The reader section inherits the object model's grain. §4.1 is a twelve-item anatomy list, not
a page: it does not resolve which elements are required, what collapses on mobile, or what the default first
screen is. There are no state designs — no empty search, no no-results guidance, no redirect/merge page and, most
tellingly, **no disambiguation**. WORKED-EXAMPLES A.0 notices "Cardboard is ambiguous (paperboard vs corrugated
fiberboard)" and solves it with a scope statement inside one topic; a reader searching "mercury" or "java" has no
described path. §4.7 says to "borrow an existing classification (LCC/Dewey/UDC)" but specifies no browse page, no
subject tree render, no breadcrumbs and no mapping — and LCC is a US library scheme proposed for a multilingual
reference.

**Concrete example.** §4.2 bullet 1: "The claim text, highlighted in the article." Literally, every claim carries
a persistent highlight; read as on-demand, the reader must first select text. The spec does not choose, and that
choice is the whole interaction. The shipped template renders one `<details>` block per section listing all its
claims, so a reader cannot tell which sentence a source supports.

**Why it matters.** Clarity is the product bet and clarity consists of these decisions. Without them the build
defaults to the easiest panel, and the bet goes untested.

**Fix.** A five-state reader spec before further object work: default article, quick-fact/summary, deep section,
evidence open on claim X, search with results and with none — each with required elements, 320 px behaviour and
the exact affordance. Decide the claim affordance once: subtle underline plus numbered superscript, drawer
scrolls to and highlights the selected claim. Add `is_ambiguous` on `Topic` with a choice page; specify the
merge/redirect page. Cut §4.1 to eight elements marked required/default/optional.

---

## 2. Scope and feasibility for a solo founder

**Essential (cannot be retrofitted):** `PublicationEvent`, a minimal `Topic`, permalinks, correction intake,
FTS5 search, licence fields, backup/restore drill, author byline, watchlist. That is the launch slice.

**Speculative:** `Assertion` (§3.6), `View`/`ViewRevision` as a full object (§3.8), `SourceAssessment` expiry,
`Organization` as a model, `PolicyVersion` as a model, `Appeal`, `Dispute`, seven review roles.

**Cut or defer.** `Assertion` is the most expensive object in the model and buys cross-revision tracking a
twelve-article corpus does not need; 80% of the value is a stable `claim_key` on the existing `Claim` plus a
"this claim changed" diff. §3.13 proposes the first slice as "`PublicationEvent` + `Topic` + `View` +
`Assertion`" — the two hardest objects plus two. A real first slice is `PublicationEvent` + `Topic` + byline +
watchlist. Type the decision as an audit event before modelling `PolicyVersion` (§3.13 itself offers this). Make
`Organization` fields on `Actor` until a second organisation asks.

**Is the 12–20 corpus realistic?** No (criticism 2). D-36's own reversal says "start with 8 topics"; the documents
disagree with themselves (12–20 in the spec, 12 in LAUNCH §6, 10–15 in Stage 1, 8 in D-36). Stage 1 also depends
on "at least 2 active human reviewers besides Justin" with no acquisition path and no reward for them.

**Is the burden understated?** Substantially. The app is 18 models and ~5.8k lines of Python for six demo
articles; §3.13 roughly doubles the object count and adds five reader surfaces, two ops processes, three
governance processes, a language pilot, a search index, an export pipeline, a backup drill and a replay tool.
Each object is a model, migration, admin, form, template, permission check, audit path and tests. At 10 h/week
this is a multi-year programme described as 6–12 months.

**Fix.** Publish a per-stage capacity budget in reviewer-hours and make it the gate. Cut Stage 0 to three
deliverables: `PublicationEvent`, permalink + citation resolution, restore drill. Move `Assertion`, `View`,
`Appeal`, `Dispute`, `Organization` and the seven-role split to a post-beta backlog with explicit triggers
("`Assertion` when a claim has been corrected twice across revisions and a reader asked what we used to say").
Start with two review roles, factual and editorial; split later, when there are people to fill them.

---

## 3. Differentiation

**What is wrong.** The spec sells claim-level evidence as a reader trust surface while its own research says
readers do not click it (0.29% of page views; process provenance is the least-rated trust cue at 3.73/5). The
people who use claim anchors are reviewers and downstream agents. That is a real market — but not the reader
market the launch plan measures itself against.

Second, "a stable, citable revision" is not new: Wikipedia has `oldid` permalinks and citing one is routine. The
new artifact is the claim anchor plus review provenance — a developer tool. The API chapter does not treat it as
one: bulk export is "later" (§8.5), reads are 60/min for new consumers, there is no resolver for a claim ID,
licensing is undecided (D-30), and no proposal turnaround is promised. A RAG operator cannot consume even thirty
articles at 60 reads/min without scraping, which the terms forbid.

**Is the agent API a market or a hope?** A hope. "3–5 downstream agents/services citing specific revisions"
(§9.3) is a target, not evidence: no operator interviews, letters of intent, price, terms or usage research. The
expensive half of the API (propose + review) serves agents that want to do editorial work on a twelve-article
wiki — a demand that does not exist yet. The cheap half (read + stable IDs + resolver) serves the demand that
does.

**Fix.** Name one buyer and one job in the first paragraph: "a citation-grade reference for [chosen regulated
domain], where a wrong number costs money and an agent must point at a revision." Ship a public resolver
(`GET /claims/{id}` returning the current occurrence plus a permanent record, 301 on merge with an alias map), a
one-file bulk JSONL export at launch, and ≥600 reads/min. Defer the propose/review API to Stage 3. Drop
"multilingual" from the product sentence until a second language exists (D-39 defers it; §1.2 promises it).

---

## 4. The view strategy

**Strength.** Pinning a base revision, hashing it and declaring staleness is the right instinct, and V10 (follow
through to the basis evidence rather than duplicating citations) is the cheapest correct rule in the document.

**Over-engineering.** An 18-field manifest plus twelve invariants specifies an artifact class, not the three
views that will exist. `coverage: Included / total claims … plus a list of what was omitted` is not honestly
computable: "what was omitted" from a summary is editorial judgement every time, and "covers 8 of 40 claims" is
noise to a reader and false precision to an auditor — D-08's own downside admits this. Meanwhile the fields
WORKED-EXAMPLES *requires* are missing from the manifest: an **owner** and an **expiry** (cross-cutting table),
and per-event `source_id`/`as_of` for timelines, which B.4 records as "**a revision to the spec**". The spec did
not absorb its own worked examples. That process signal matters more than any single field.

**Would a reader understand it?** The reader gets one line: "Derived from r12 (hash …) … covers X of Y claims."
R1 is explicit that process provenance is the cue readers rate least. That line is for auditors; say so instead
of designing it as a trust device.

**Would a contributor maintain it?** Not for summaries, and not at this cost: sequenced as written, every article
edit invalidates its own first screen.

**Fix.** Three tiers. (1) *Revision content* — lead, at-a-glance, typed table/timeline **blocks** — reviewed with
the article, no `View` object, no staleness; each table row carries its own `source_id` and `as_of`. (2) *Derived
artifacts* — translation, audio, chart, generated explainer — get the `View` object, manifest, owner, expiry,
staleness. (3) *Deferred* — maps, answer views. Ship tier 1 at beta and exactly one tier-2 pilot (translation),
which is also a more interesting differentiator than a second summary surface.

---

## 5. Launch and metrics

**What is wrong.** "Strong launch" (§9.3, LAUNCH §8) mixes four real measures with five soft ones. Real: p90
correction latency, review backlog, citation resolution, and the best single metric in the document — "at least
one external citation is from someone who is not involved in the project" (LAUNCH §8.3). Soft: "20% weekly return
among surveyed readers" is measured intent, not return; "'would be missed' ≥ 40%" has no baseline or instrument;
"10 active contributors" is undefined; "3–5 downstream citations" is gameable by the founder's own demos; "task
success above a plain-search baseline" names no baseline and, with 5–8 participants, has an interval spanning
most of the plausible range — and is then used as a binary gate.

**Readiness criteria** are binary gates on underpowered samples, and several are satisfiable by construction:
"10 articles meet the quality bar" counts what you wrote; "30+ topics" counts what you seeded. **Admission
control** (§9.6) protects capacity in principle but, per criticism 1, fires on the first agent; the circuit
breaker (backlog > 2× capacity for two weeks → freeze proposals) is a kill switch that fires exactly when a
community forms. **Seed topics** are wrong per criticism 6, and two of the twelve are fictional companies and
people in a *public reference* — polluting search, exports and credibility, and useless to any reader.

**Biggest omission: there is no distribution plan.** Nothing in either document says how the first thousand
readers arrive — no channel, partner, SEO plan, directory, launch venue or referral target. A plan whose success
metric is a return rate needs traffic first.

**Fix.** Replace §9.3 with four metrics, each with n and a definition: (i) external citations from uninvolved
parties that still resolve after 30 days; (ii) p90 correction acknowledgment; (iii) weekly reviewer-hours
demanded ÷ available, published; (iv) task success on ≥24 participants against a named baseline (Wikipedia for
overview, an LLM for quick fact). Delete the survey return gate. Add a distribution section naming two channels
and one partner target. Keep hypothetical cases in a quarantined `/sandbox` namespace excluded from search,
exports and anchor counts.

---

## 6. What would make me not use or contribute

**As a reader.** I arrive from a search for a quick fact. A "Seed" badge, a dispute banner and a stale-view
notice read as unfinished, and I go back to Wikipedia. If I stay, nothing brings me back: no watchlist, no "the
claim you corrected was fixed", no alert when a disputed claim resolves. The research says quick-fact is 25–38%
of reader demand; this design is built for the citation task instead.

**As a domain expert.** I get no byline. My sentences must map to claim spans and (if `Assertion` ships) to
stable assertions — editorial work that feels like data entry. My correction waits up to 14 days, and a reviewer
may close my proposal as taste-only under §5.10. My reward is a review record with my username. R3 says
attribution and a citable revision are the currency for experts; the spec pays in neither.

**As an agent operator.** 60 reads/min, no bulk export, no claim resolver, licence undecided, no turnaround
commitment. Worse: §3.2 says a merged topic's "assertions and revisions are re-pointed or archived", but I8 and
§3.6 promise an assertion is never silently re-pointed. A merge is exactly a silent re-point, and it breaks the
stable claim ID that is the only reason to integrate.

**Fix.** Ship the byline ("written by X, maintained by Y") and a credit page. Add an opt-in, weekly-batched
watchlist with one notification type. Define merge semantics now: assertion IDs immutable, merges publish an
`old_id → new_id` alias map, the resolver follows it, and old IDs carry a 30-day deprecation header.

---

## Where I disagree with the author

**Too conservative.** (1) D-19 imposes two reviews plus a publisher decision on *every* published edit,
including typos, while §6.10 defines a "cosmetic: 1–2 min" tier. Spending the scarcest resource on a two-person
review of a comma is misallocation, and the lab gives no evidence a human minute beats a diff check plus sampled
audit there. (2) Deferring all languages (D-39, Stage 3) contradicts both the product sentence and seed #12,
which needs non-English sources it cannot have in an English-only corpus. Translation-as-a-view is the cheapest
differentiator available and the one agent operators would pay for; deferring it is under-ambitious, not prudent.
(3) I19's "review at creation or not at all" imports Wikipedia's hoax half-life into a setting with twelve gated
articles and almost no readers. Here post-publication review is not wasted effort; it is the only channel that
tells you what readers catch. Keep it first-class.

**Too ambitious.** `Assertion`, `Dispute`, `Appeal`, `Organization`, `PolicyVersion` and seven review roles are a
governance stack for thirty people. "What did we believe about assertion A on date X" (§4.5) is a research-library
capability specified before the first reader arrives. Coverage percentages invite the false precision §5.2 claims
to avoid. And 12–20 featured-article-quality topics is a two-person-year promise inside a solo-founder plan.

---

## What the spec gets right

- `PublicationEvent` append-only, with the mutable pointer demoted to a cache. Correct and non-negotiable.
- Content hash separated from revision ID; no ordering derived from numbers.
- No single trust or neutrality score; neutrality as named checks with reasons.
- Honest evidence labels, "where the rule fails" sections, and refusing to treat the policy lab as authorization.
- Accessibility as a release criterion with named WCAG 2.2 AA criteria, not an aspiration.
- Reviewer independence as the lever, rather than cleverer policy rules.

---

## What I could not assess

- **Real reader demand.** No traffic model, keyword evidence or interviews; I cannot tell whether a citation-grade
  segment exists at a scale supporting even five articles.
- **Whether claim-level editing is sustainable.** "Claim-level citations already work" rests on six demo
  articles, 47 claims, 263 citations and four snapshots — machine-generated density, not sustained human work.
- **The founder's budget.** The 10 h/week figure is the plan's assumption, not a verified fact.
- **Legal exposure** of CC0 assertions extracted from CC BY-SA prose, snapshot retention, and real BLP content.
- **The rendered UI.** I read templates and views but did not run the server; my UX claims are inferences.
- **The external research.** I did not re-fetch sources; where the notes say "claimed" or "secondary", the spec
  often states the number unhedged (notably Grokipedia and the agent-native wiki benchmarks).

---

## Severity table

| # | Issue | Severity | Affected | Fix |
|---|---|---|---|---|
| 1 | Agent quota (5–10/day) exceeds human review capacity (≈3–4/day) | **blocker** | §6.10, §9.6, D-25 | Cap new-agent proposals at 1/day; quota as a fraction of measured weekly hours |
| 2 | 12–20 anchors at the §5.11 bar unaffordable at 10 h/week | **blocker** | §9.2, §5.11, D-36 | Five anchors in one niche; reviewer-hour budget per stage |
| 3 | No watchlist/notification and no author byline | **blocker** | §4.1, §3.3, §4.10 | Byline, credit page, opt-in weekly watchlist |
| 4 | Summary is a reviewed, auto-staling View on the first screen | **major** | §4.1.3, §3.8 V5–V6 | Lead + at-a-glance as revision content; `View` for translation/audio/chart |
| 5 | Evidence interaction unspecified; shipped UI block-level | **major** | §4.2, `_article_body.html` | Five-state reader spec; underline + superscript; per-claim drawer |
| 6 | Seed portfolio competes with Wikipedia instead of finding a wedge | **major** | §9.2, LAUNCH §6, R3 | One citation-costly niche; contested cases as internal fixtures |
| 7 | 44% high-risk escape contradicts BLP and quality promises | **major** | §5.7, §5.11, D-19 | Declare high-risk topics out of scope at launch; publish the limit |
| 8 | Fictional subjects in the public corpus | **major** | §9.2 rows 3–4 | Quarantine to `/sandbox`, excluded from search and exports |
| 9 | Topic merge silently re-points assertion IDs | **major** | §3.2 vs I8, §3.6 | Immutable IDs, alias map, resolver, 30-day window |
| 10 | No distribution plan for first readers | **major** | LAUNCH §8–9 | Two channels, one partner, one referral target |
| 11 | Appeals panel and seven roles before a community exists | **major** | §6.5, §6.7, §7 | One reviewer + one adjudicator at launch; panel at 30 contributors |
| 12 | `coverage` percentage in the view manifest not computable | minor | §3.8, D-08 | Drop the percentage; keep `omitted_topics` and `limitations` |
| 13 | Manifest lacks `owner`/`expiry`; timelines lack per-event sources | minor | §3.8, WORKED-EXAMPLES B.4 | Add the three fields |
| 14 | Binary gates on underpowered samples; survey "return" is intent | minor | §9.3–9.4, D-38 | n-defined metrics; p90 not median; drop the survey gate |
| 15 | Orphan publish-gate blocks the first topic | minor | §3.2 | Bootstrap exemption or a curated "Start here" parent |
| 16 | "Multilingual" promised but deferred; FTS5 fails for CJK | minor | §1.2, §8.4, D-39 | Say "language-ready"; specify ICU tokeniser first |
| 17 | CC0 over assertions from CC BY-SA prose | minor (legal) | §8.5, D-30 | CC0 for identifiers/templates only; no verbatim prose |
