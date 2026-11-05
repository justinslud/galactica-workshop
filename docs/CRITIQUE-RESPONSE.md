# Critique response and revision record

**Date:** 2026-11-04.
**Reviewers:** two independent AI critics with separate briefs and separate files:
[trust/governance](critique/trust-governance.md) and [product/feasibility](critique/product-feasibility.md).
They did not see each other's critiques. Their authority is advisory; they did not ratify policy.
**Response author:** the lead. This is one substantive critique-and-revision pass, not a review loop.

---

## What changed in response

| Critique | Severity | Change |
|---|---|---|
| Agent quota (5–10/day) exceeds human review capacity (≈3–4/day) | blocker | Quotas cut to 1–2/day for new humans/agents, 5–10 established, 20–30 trusted; review-hour ratio is now the binding metric; "one agent cannot consume 125–250% of capacity" stated. Spec §6.10, D-25, launch plan §11. |
| Two reviews + publisher for every edit infeasible at launch | blocker | `human-gate-v0` is tiered: low/standard = 1 review + publisher; high/contentious = 2 + publisher; cosmetic = 1 lightweight + audit. Universal two-review is a later target. Spec §6.6, D-19. |
| 12–20 anchors at the quality bar unaffordable | blocker | Public launch corpus is **5–8 topics in one citation-costly wedge**; the 12-topic matrix is internal fixtures/`/sandbox`. Spec §9.2, D-36, launch plan §7. |
| No watchlist/notification and no byline | blocker | Added author byline/credit page and opt-in weekly watchlist (one notification type, off by default). Spec §3.3, §4.1, §4.10, M0 ladder. |
| Founder-final authority coexists with a panel that can reverse him | blocker | §7 retitled "proposed interim authority, not in force"; appeals adjudicator is advisory at launch unless Justin adopts binding appeals in writing; 3-person panel at ≥30 contributors. Spec §7.1, §6.7, D-21/D-34. |
| Uncited claims publishable at self-declared low risk | blocker | No uncited factual claim in an anchor article at any risk class; `provisional` uncited claims are badged, expire, excluded from citations/exports. Risk class assigned by triage, not author. Spec §3.6, §5.11, I21. |
| View manifest cannot be populated; V5 misses retraction | major | Manifest and fields reconciled: `basis_assertions[]`, `basis_claim_occurrences[]`, `basis_source_snapshots[]`, `owner`, `expiry`, `omitted_topics[]`, `limitations`. V5 fires on base change, assertion status, source retraction or assessment expiry. Spec §3.8. |
| Reading levels are both an Article field and a view | major | Removed `reading_level` from `Article`; reading levels are views; a reviewed translation can become a language edition. Spec §3.3, §4.8, D-04/D-39. |
| Synthesis/explanatory prose has no object or review role | major | Added `analysis` block kind with its own citations and a `coverage` review. Spec §3.5, §3.6, V1. |
| Reviewer collusion / review-graph capture unaddressed | major | Added review-graph signals (pair frequency, approval-rate deviation, assignment diversity, rotation), provider recording, source capture, appeal flooding, translation laundering. Spec §6.11, D-24. |
| "200 proposals is not worth running" lacks support | major | Deleted the claim; E9 measures attacker cost/false positives; volume-independent defences added. Spec §6.11. |
| Ten neutrality checks not usable by the assigned reviewer | major | Split into four mandatory sentence-level checks + five coverage judgments requiring recorded domain competence; "not assessed, because…" required. Spec §5.6, D-11. |
| Coverage percentage contradicts "no completeness score" | major | Removed the reader-facing ratio; manifest uses `omitted_topics[]`/`limitations`. Spec §5.2, §3.8, §4.6, D-08. |
| BLP "remove immediately" has no bypass; no-consensus rule has no consensus process | major | Added `blp_removal` one-action path (publish then review); real living-person/company content is out of scope at launch; high-risk scope limit stated. Spec §5.7, §6.9, §9.2. |
| `[claimed]/[open]` research becomes design certainty | major | Removed "high confidence" from the view contract; restored caveats for the policy lab, Nupedia, Grokipedia and the chatbot audit; I19 demoted to a policy parameter. Spec §3.8, §6.5, §9.3. |
| Stale-citation pump from deprecate-not-delete | major | Added claim resolver at launch (`GET /claims/{id}`), assertion resolution contract (status, `valid_to`, successor, current pointer), deprecation feed, merge alias map. Spec §8.2, §3.2, I8/I22. |
| Correction intake unbudgeted while carrying the SLA | major | Added correction budget (10–20/day), intake clustering, severity triage, published capacity. Spec §4.4, §6.10. |
| `origin_key` author-supplied | major | Assigned by the application from DOI/publisher/author/wire metadata + snapshot similarity; per-topic origin concentration; ≥2 origins for high-risk. Spec §3.7, §5.5. |
| Summary is a reviewed, auto-staling View on the first screen | major | Lead/at-a-glance/timeline/table are **revision content**, not `View`; `View` is for translation/audio/chart/explainer. Spec §4.1, §4.6, §3.8, M3. |
| Evidence interaction unspecified | major | Added five reader states and a claim affordance (subtle underline + numbered superscript; drawer scrolls/highlights; uncited marker; focus/escape behavior). Spec §4.1–§4.2. |
| No wedge; seed portfolio competes with Wikipedia | major | Public corpus is a wedge; capability matrix is fixtures; distribution plan added (two channels, one partner, referral target). Spec §9.2–§9.3, launch plan §7/§9. |
| 44% high-risk escape contradicts BLP/quality promises | major | High-risk/contentious real-subject content out of scope at launch; the limit is published. Spec §5.7, §9.2. |
| Fictional subjects in the public corpus | major | `/sandbox` only, excluded from search/exports/anchor counts. Spec §9.2, launch plan §7. |
| No distribution plan | major | Added two channels, one partner, one referral target; measure referral source. Launch plan §9. |
| Appeals panel and seven roles before a community exists | major | Launch roles = factual/source/readability (coverage folded in; policy on demand); one adjudicator; panel at ≥30 contributors. Spec §6.5–§6.7. |
| `coverage` percentage not computable | minor | Removed; `omitted_topics[]`/`limitations` instead. Spec §3.8. |
| Manifest lacks `owner`/`expiry`; timelines lack per-event sources | minor | Added both; timeline/table blocks require per-event/per-row source/as_of. Spec §3.5, §3.8. |
| Binary gates on underpowered samples | minor | Replaced §9.3 with four primary metrics (n, definition, baseline); survey return is no longer a gate. Spec §9.3, D-38. |
| Orphan publish-gate blocks the first topic | minor | Bootstrap exemption for the first 3–5 topics with a curated "Start here" parent. Spec §3.2. |
| "Multilingual" promised but deferred; FTS5 fails for CJK | minor | Product sentence says "language-ready, one language at launch"; ICU/Unicode tokenizer specified; CJK later. Spec §1.2, §8.4. |
| CC0 over assertions from CC BY-SA prose | minor (legal) | CC0 for identifiers/schemas/templates only, not verbatim prose; counsel review. Spec §8.5, D-30. |
| Grokipedia `[secondary]` label dropped | minor | Restored in launch plan historical calibration. Launch plan §9. |

---

## What was not changed, and why

- **Article-first remains.** The critics did not argue for assertion-first; they argued the assertion object is
  too expensive now. I moved it to M4 and added `claim_key` at M2, but kept the article as the publication unit.
- **The human gate for high-risk/contentious remains.** The tiered minimum reduces low/standard review, not the
  high-risk gate. The policy lab's 44%/57% escape rates do not justify less.
- **The view contract remains for derived artifacts.** I removed the summary/at-a-glance from the `View` object
  and dropped the coverage ratio, but kept the manifest and staleness for translation/audio/chart/explainer.
  The critics' "too conservative on views" point is preserved as dissent: an `unreviewed` labelled view is now
  allowed for navigation, but not for citations/exports.
- **Multilingual ambition remains.** The product is "language-ready, one language at launch"; D-39 still defers
  a second language until a named reviewer exists. The critics' "too conservative on languages" point is
  preserved as dissent.
- **No real BLP/company content at launch.** The critics disagree on whether this is too conservative; I treat
  it as a safety gate, not a permanent exclusion.
- **The name decision remains open.** T5 collision and "Truth Attractor" overclaim are recorded as
  considerations, not verified legal conclusions.

---

## Dissent preserved

**Critic 1 (trust/governance) thinks the spec is too conservative on:**
- Requiring review of every view; it would allow labelled unreviewed views. The revision allows unreviewed
  navigation views but not citable ones — a partial adoption.
- Deferring multilingualism; it would fix the schema now. The revision keeps the deferral but makes the schema
  language-ready and adds a translation view pilot.
- Making "AI cannot publish" a standing prohibition. The revision demotes it to launch policy with D-20 as the
  reopening path.

**Critic 2 (product/feasibility) thinks the spec is too ambitious on:**
- `Assertion`, `Dispute`, `Appeal`, `Organization`, `PolicyVersion` and seven roles. The revision moves
  `Assertion` to M4, reduces launch roles to three, makes appeals one adjudicator, and defers the panel.
- "What did we believe about assertion A on date X" before the first reader. The revision keeps `claim_key` at
  M2 and full assertion history at M4.
- 12–20 featured-article-quality topics. The revision cuts the public corpus to 5–8 in a wedge.

**Where the lead disagrees with both critics:**
- The human gate for high-risk content is not over-conservative; it is the only defensible response to the
  policy lab's measured escape rates and the absence of counsel.
- A citation-grade artifact is a real differentiator even if most readers do not click citations; the reader
  surface must be fast and plain, but the evidence layer is for the minority who verify and for downstream
  agents. The revision keeps both, with clarity first.
- The project should not drop "multilingual" from its long-term identity; it should be honest that launch is one
  language. The revision does that.

---

## What remains unresolved after this pass

- The wedge domain and the 5–8 anchor topics (D-36; needs Justin + a named expert).
- The name (D-01), licensing (D-30), governance transition (D-34), public beta timing (D-37).
- Measured catch rates, review minutes, reader task success, correction triage time, restore drill, accessibility
  audit. These are experiments, not document decisions.
- Whether the appeals adjudicator should be binding at launch. The revision makes it advisory unless Justin
  adopts it in writing; that is a values/authority decision, not a research question.
- Whether `claim_key` is enough to avoid the full `Assertion` object at 50+ articles. The M4 trigger is a
  hypothesis; measure it.

---

## Process note

The two critiques were produced independently, before either saw the other. Their files are preserved verbatim
in `docs/critique/`. This response is the only revision pass; it does not claim the critiques were fully
satisfied. The spec's status is still **proposal**, and the decision register's `proposed` items are still not
accepted policy.
