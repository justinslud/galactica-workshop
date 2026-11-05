# Critique — trust, epistemics and governance

**Reviewer:** independent critic (not the author). **Date:** 2026-11-04. **Scope:** `PRODUCT-SPEC.md` v2.1, the
decision register, worked examples, launch plan, experiments, `00-CURRENT-STATE.md`, R1–R3. Nothing was edited or
deployed.

The object model and the refusal to score neutrality are better than the genre norm. The problems are hypotheses
turned into commitments, authority the spec does not hold, and gates built on unmeasured numbers.

---

## Most consequential criticisms

1. **The review regime is arithmetically impossible.** D-19 requires two reviews plus a publisher for every
   published edit; §6.10 prices a solo steward at 20–30 reviews/week, so 10–15 publishes before corrections and
   views — with two humans at Stage 0.
2. **Independence is unachievable at launch, so it will be waived silently.** With two or three people the
   author/reviewer/operator rules (§6.5, I10) cannot hold; one actor files both reviews and nothing records it.
3. **Governance is founder-final and panel-reversible at once.** §7.1 gives Justin "final authority for … policy,
   spending, appointments"; §6.7 lets a panel "remand, uphold, reverse", including "one uninvolved steward" — an
   office with no holder.
4. **`[needs source]` at low risk rebuilds the failure the spec cites.** §3.6/§5.11 permit uncited claims below
   standard risk while `risk_class` is "self-declared" (§3.9); §4.2 cites 587,590 unsourced-statement pages.
5. **The view contract cannot be populated and fails under retraction.** The "required to publish" manifest needs
   `basis_hash`, `claim_ids`, `coverage`, `transformations`, `limitations` — none exist on `View`; V5/I7 watch only
   the base revision, and A.6 concedes retraction leaves views "current".
6. **A computed percentage contradicts the "no score" rule.** §5.2 forbids a completeness score; §3.8/§4.6
   require "covers X of Y claims". D-08 names the false-precision risk.
7. **The sybil model defends the wrong seam.** §6.11 quotes R2 on Orangemoody — an attack on the *review
   pipeline* — then lists only proposal-level signals; two reviewers approving each other's work uses no sybils.
8. **The cost asymmetry justifying "capacity protection" is invented.** §6.11 says a 200-proposal campaign "is not
   worth running (R2)"; R2 says the opposite is unknown: "I found no measurement."
9. **The neutrality checks do not fit their reviewer, and R2 said so.** Its "Don't": "a well-informed generalist can
   adjudicate all three; noticeboards work because thousands of specialists self-select."

---

## 1. Internal contradictions and category errors

**The reader surface models states the schema cannot store.** §3.6 defines `support_status` as `direct`,
`partial`, `conflicting`, `absent`; §4.2 tells readers to expect "**direct**, **partial**, **conflicting**, **no
citation**, **stale**". The two warnings that carry the most trust weight are unrepresentable, so a developer
derives them ad hoc and no reviewer can record them.

**`View` and its manifest are different objects.** `View` lacks `basis_hash`, `claim_ids`, `coverage`,
`transformations` and `limitations`; `base_revisions[]` is plural against a singular `basis_revision`; the manifest
says `claim_ids` where the fields say `base_assertions[]`. Claims die at the next revision and assertions survive,
so choosing claim IDs means a view can only be rebuilt, never partially revalidated.

**Prose has no home, and prose is the product.** §3.3 forbids facts "absent from its topic's assertion set"; §3.6
makes `Assertion.statement` a single-language phrasing. Yet §5.2 requires the causal account "explained, not just
named", and V1 permits "labeled commentary/analysis … with its own evidence and review" — with no object or citation
form for a synthesis drawing on five sources. Synthesis is the product's differentiator and the model's blind spot.

**Invariants are decorative where it matters.** I2 depends on classifying a "factual claim" — the unsolved problem.
I8 ("never silently re-pointed") is undetectable when mapping is "exact/normalized text and human confirmation". I9
forbids only *silent* override, which §6.6 allows with a recorded reason. I19 is a policy choice, not an invariant —
yet E2 exists to test it, so E2 cannot change what I19 forbids.

**The view contract fails the retraction test.** A retraction, assessment downgrade or assertion moving to
`disputed` leaves dependent views `published` and citable; A.6 diagnoses this and §3.8 is unchanged. A promoted
translation edition has "its own revisions", nothing tracks the source's later corrections, and nothing forbids one
edition citing another as evidence.

**Fixes.** One schema for `View` and manifest with `basis_assertions[]` and `basis_source_snapshots[]` required;
V5 firing on assertion status, retraction and assessment expiry; delete either `Article.reading_level` or the view
kind; an `analysis` block kind with its own citations; `no_citation` and `stale` added to the enum or declared
derived.

---

## 2. Overclaims and unsupported confidence

**"Proposed, high confidence" is the loudest instance.** §3.8 heads the view contract "(proposed, **high
confidence**)" while D-08 is a route-C critique candidate and E5 — the experiment that would price views — is unrun
and P0. R1's open question is whether "review attaches to each artifact or to the generator recipe"; V6 answers it
by requiring review of every artifact.

**"Review at creation or not at all" is a finding in the spec, a hypothesis in the research.** §6.5 concludes "Late
review is mostly wasted effort." R2 labels that `[proposed adaptation]`, notes the numbers concern *ever-detected*
hoaxes among thousands of watchers, and states: "Findings 2 and 3 are in tension; do not flatten them." Finding 3 is
that the speed catching hoaxes is implicated in driving contributors away; the spec keeps the first and promotes the
conclusion to I19.

**Simulated numbers become settled facts.** The lab's 44.2% vs 22.3% escape rates are assumptions
(`00-CURRENT-STATE.md` §1.1: "**simulated assumptions**, not measured catch rates"), a caveat the spec drops. R2: the
rates "remain **[open]** until measured from recorded review runs."

**History is used to prove the opposite of what it shows.** Nupedia/Wikipedia is `[historical]`, and R3 warns "the
magnitudes are not transferable." The case shows lowering review friction produced supply; the spec's answer is to
rebuild the Nupedia gate with fewer reviewers, and the disanalogy is never argued.

**Decisions precede the experiments that test them.** §0: "So the design is clarity first, evidence one step away"
— E1 is the test, unrun. The capacity estimate ("Standard: 10–20 min", i.e. 1.5–6 minutes per claim) carries the 80%
threshold, quotas and circuit breaker before E2/E10 measure it.

**Fixes.** Use the register's status vocabulary in §3.8; demote I19 to a parameter so E2 can change it; carry the
simulation caveat inline; tag the capacity estimate `[assumption]` and gate Stage 1 exit on measuring it.

---

## 3. Governance authority

**Separation is real horizontally, cosmetic vertically, and the spec does not distinguish them.** Separating
*kinds of judgment* (factual/editorial/community/conduct) is well grounded in R2's venue evidence: §7.2 refuses to
let a publisher declare a claim supported. What is cosmetic is separation of *authority*: §7.2 assigns policy to
"Policy steward/foundation", scope to "Topic steward + community process", appeals to an "Independent panel" —
bodies with no members. §7.1 gives the founder policy *and* appointments, so the steward is a delegate and the panel
is a committee he staffs.

**The spec ratifies governance on Justin's behalf.** It binds him — "final authority … **subject to the published
process**" — which is not among the accepted decisions. It creates an appeals body
that can reverse him without deciding whether he is bound. It turns a launch policy into a standing prohibition ("AI
cannot publish", I9, §7.5) while the 2026-10-27 clarification says human review at the start "is not a new
requirement for permanent human approval". And it adopts ~20 policy parameters by fiat without the 14–30 day comment
period §7.3 prescribes.

**Appeals are not credible as staffed.** A panel with "no one who made the original decision" and "one uninvolved
steward" needs five people; Stage 0 has two, and B.2/C.5 add that panels need domain competence. D-21's fallback
("single appeals reviewer + steward review") is not the process described.

**BLP/COI are right in direction, wrong in mechanism.** §5.7 imports "removed immediately and without discussion"
and "no consensus … defaults to removal for living people". The first needs a removal path bypassing the two-review
gate; §6.9's rollback is unpublish-by-staff. The second imports a *consensus* procedure the system lacks: a
publisher decides, so no content discussion has a no-consensus default.

**Fixes.** Retitle §7 "Proposed interim authority — not in force", mark institutions `[nonexistent]`, and state
that nothing binds Justin until he adopts it in writing; settle appeals in one sentence; publish the parameters as
`PolicyVersion v0` with a comment window; make the 24-hour emergency second review conditional on a named person.

---

## 4. Sybil/coordination and review capacity

**Aimed at the wrong seam.** §6.11 correctly quotes R2 that Orangemoody "targeted the **review pipeline** … No
content-level check catches that." It then lists six signals, all proposal-level: shared operator, near-duplicate
text, timing, narrow claim, citation loops, bursts. None concerns the review graph — reviewer–author pair
frequency, per-reviewer approval deviation, latency clustering, assignment diversity. §6.4 has triage "assign …
reviewers", a single point of capture held by the same steward, and the cheapest attack needs no sybils: become a
trusted reviewer and approve a partner's work.

**Admission control and review-at-creation are incompatible as written.** I19 forbids deferring review; §9.6's
breaker freezes *new proposals*, which does nothing to a backlog whose only clearance route is the late review I19
forbids. §9.3 then requires "no proposal older than 30 days without a decision", forcing a decision on exactly the
proposal whose review the spec calls wasted. No expiry rule exists for proposals or corrections.

**The correction channel is the least rate-limited and most promised surface.** §6.10's quotas cover proposals and
API reads; §4.4 allows anonymous corrections and promises 2 days / 14 days. Twenty a day against one triager breaks
the SLA the launch plan makes the central credibility claim.

**Missing attacks.** Source capture — publish a plausible source and cite it; every machine check passes. The
independence signal is author-supplied: `origin_key` is merely "recorded" (§3.7) and the proposer supplies
`evidence[]`. Appeal flooding: one appeal *per decision*, not per appellant. Model-provider capture: E3 cannot test
cross-provider independence with "3 models available in the local catalog". Translation laundering: introduce a claim
in a weak edition, cite it back.

**Fixes.** Review-graph monitoring and random assignment within a qualified pool; proposal expiry (14 days →
`expired`) with the breaker acting on submission rate; a correction intake budget; `origin_key` derived by the
application, never by the proposer.

---

## 5. Evidence quality and neutrality

**The ten checks do not fit the reviewer, and R2 warned against trying.** Checks 1, 5 and 10 need an estimate
of the reliable-source base and a counterfactual about readers; neither is measured, and R2 says a generalist
cannot adjudicate weight. Checks 3, 4 and 9 need domain knowledge. Only 2, 6, 7, 8 are sentence-level and
generalist-checkable. The documents also disagree: §5.11 requires checks "completed with reasons" for every
article; D-11 starts with four for contested topics. A reviewer resolves this by doing the cheapest two and
writing "no issue found" — indistinguishable from a real review.

**Source assessment is too heavy and too light.** Per use *and* per topic, seven dimensions and four ratings for
every source exceeds a solo reviewer — hence D-09's reversal to disputed/high-risk only. Yet the enum has no
`unassessed`, so §4.2 promises "source reviewer's assessment" for every claim. Too light: no *scope match* dimension
(population, region, period against the claim's qualifiers) — A.4's "municipal vs all paper" is exactly this.

**The BLP asymmetry is directionally right and unsafe at solo scale.** "Remove first, discuss later" is the one
place where slowness is irreversible, yet it is paired with a 24-hour path, a 14-day SLA, one steward and no counsel.
C.4 admits "a small project cannot run a 24/7 legal/privacy desk"; `LAUNCH-PLAN.md` §12 then mitigates legal risk with
"insurance", which appears in no decision or readiness row, and the hard gate ("avoid real living-person cases until
… counsel") is only a `should` in §9.2.

**"Deprecate not delete" has no consumer contract.** Retention is right for the Wikidata reason. But §3.6 promises
"a stable claim ID", `status` includes `retracted`, and nothing requires `/assertions/{id}` to return the successor or
validity window — unlike V11, which does require views to resolve "plus [their] successor". Stable IDs plus soft
deprecation is a stale-citation pump.

**Fixes.** Four mandatory sentence-level checks (2, 6, 7, 8) plus five coverage judgments (1, 3, 4, 5, 9) requiring
recorded domain competence; a quoted anchor or an explicit "not assessed, because"; `unassessed` and scope match; a named
real-subject gate; assertion resolution with a deprecation feed.

---

## 6. Failure modes the spec underplays

**Most likely: review starvation, then a quiet quality waiver.** The design is right; the resourcing is absent. The
outcome is drift, not collapse — reviews become single-reviewer, then self-review, then "reviewed" by an agent on
the same model, while the dashboard still reports "≤ 80% capacity" because capacity was redefined.

**Second: the corpus is a demo, not a demand hypothesis.** R3 recommends "a narrow citation-grade reference …
a regulated domain" because "a general encyclopedia competes with Wikipedia on its strongest ground"; Justin's
recorded preference is "lean futuristic". The portfolio is cardboard, the telephone, a river basin. Stage 1–2 tests
measure whether the *surface* works, not whether anyone needs these topics.

**Third: a legal/BLP incident before counsel exists.** One well-sourced negative claim produces a demand letter;
the options are capitulate, litigate without budget, or go dark. Insurance and legal review appear in no decision
or readiness row. Underplayed fourth: source capture.

---

## Where I disagree with the author

**Too conservative on derived views.** V6 reviews every view, including summaries, and V5 excludes stale ones from
citations; R1's rule is better — an unreviewed view is publishable at "the same position and weight" if labelled.
Universal review guarantees a stale-view backlog and pushes readers to the unreviewed artifact anyway. Ship
template-derived views with machine checks, label `unreviewed` views, and reserve human review for citation exports.

**Too conservative on multilingualism to the point of incoherence.** The definition says "multilingual", D-39 defers
languages, and `Assertion.statement` is single-language. A localized statement table is cheap now and expensive
later. Either drop the word or fix the schema.

**Too conservative on cosmetic autonomy, for the wrong reason.** Gating autonomy on 500 edits is defensible;
making "AI cannot publish" a standing prohibition is not caution but over-ratification, and it contradicts the
recorded path to decentralization. Keep the gate, delete the prohibition.

**I disagree with the seed-corpus strategy outright.** I would launch five topics in one narrow domain where being
wrong costs money, and treat breadth as a later reward for trust — not twelve showcase topics chosen to demonstrate
view types. That is the article-count mistake in narrative form.

---

## What the spec gets right

- The split between revision (content), publication event (record) and view manifest (reproduction) is correct, and
  `PublicationEvent`-first is the right implementation order.
- Refusing a neutrality score, and insisting "a 'neutral' badge … is a claim the system cannot support" (§5.6).
- "Independence ≠ even-handedness" and "COI ≠ bias", with separate fields and no collapsed score.
- Admission control, anti-vanity metrics, and no new language without a named reviewer.
- Accessibility and licensing as launch blockers; the register's status/route/reversal discipline.

---

## What I could not assess

- Whether the workshop implements what `00-CURRENT-STATE.md` claims. I read documents, not `core/editorial.py`.
- Whether two reviewers, counsel and insurance are obtainable at the project's budget, or what a review minute costs.
- Whether the lab's 0.85/0.30 correlation parameters correspond to any real model pair.
- Reader demand for any seed topic; trademark clearance; CC0 soundness under EU database rights.
- Whether the 587,590 / 362,781 / 81,345 figures were current when fetched; I did not re-query.

---

## Severity table

| Issue | Severity | Affected section/decision | Fix |
|---|---|---|---|
| Two reviews + publisher per edit infeasible at launch headcount | blocker | D-19, §6.10, §9.1 | Risk-tiered minimum; published review-hour budget |
| Founder-final authority coexists with a panel that can reverse him | blocker | §7.1, §7.2, §6.7, D-21, D-34 | State the binding relationship, or make appeals advisory |
| Uncited claims publishable at self-declared low risk | blocker | §3.6, §3.9, §5.11 | No uncited claims; `provisional` badge with expiry; policy-set risk class |
| Manifest cannot be populated from `View`; V5 misses retraction | major | §3.8, I7, A.6, D-08 | One schema; assertion/source bases; staleness on retraction |
| Reading levels both an `Article` field and a view | major | §3.3, §4.8, D-04 | Delete one |
| Synthesis prose has no object or review role | major | §3.3, §5.2, V1 | `analysis` block with citations and coverage review |
| Reviewer collusion and review-graph capture unaddressed | major | §6.11, §6.4, §6.5 | Graph monitoring, random assignment, published statistics |
| "200 proposals" cost claim unsupported | major | §6.11 | Delete; measure attacker cost in E9 |
| Ten neutrality checks unusable by the assigned reviewer | major | §5.6, §5.11, D-11 | Four sentence-level + five domain judgments; anchors |
| Coverage percentage contradicts "no completeness score" | major | §5.2, §3.8, §4.6 | Drop the ratio; keep the omission list |
| BLP removal has no bypass; no-consensus rule has no consensus process | major | §5.7, §6.9, C.4 | `blp_removal`; named gate |
| `[claimed]`/`[open]` findings become design certainty | major | §0, §3.8, I19 | Restore labels; demote I19 before E2 |
| Deprecate-not-delete with no consumer contract | major | §3.6, §8.2, V11 | Resolution returns status and successor; deprecation feed |
| Correction intake unbudgeted while carrying the SLA | major | §4.4, §6.10 | Correction quota and intake clustering |
| `origin_key` author-supplied, so independence is self-declared | major | §3.7, §5.5 | Derive in-app; per-topic origin concentration |
| No `unassessed` rating; no scope-match dimension | minor | §5.5, §4.2 | Add both |
| Emergency second-person review unavailable at Stage 0 | minor | §6.9 | Conditional on a named second person |

**The single change I would make first:** replace the universal two-review rule with a risk-tiered minimum *and*
publish the review-hour budget as the binding constraint. Every other commitment — view review, correction SLA,
appeals panel, BLP path — draws on that same unmeasured resource.
