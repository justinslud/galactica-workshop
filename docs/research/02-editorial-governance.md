# 02 — Knowledge/editorial model and contribution/governance

**Status:** research note, not a specification. Evidence gathered 2026-11-04.
**Scope:** trust and governance questions behind Galactica/T5 — what is editable, how scope and coverage are judged, how neutrality becomes reviewable checks, how evidence quality is assessed, who may contribute and review, how sybil resistance fares in open communities, how mature projects separate factual review from editorial judgment and community preference, and what is genuinely defended against abuse and prompt injection.
**Method:** DuckDuckGo HTML endpoint for discovery, then primary pages fetched directly (Wikipedia `action=raw` wikitext, Wikidata raw, arXiv abstracts, publisher PDFs, Crossref REST API). No source below is described from a search snippet.

### Labels

**[demonstrated]** — I read the policy text, interface, dataset, or paper myself. **[claimed]** — the organisation or authors assert an effect I did not verify. **[historical/abandoned]** — existed and was changed. **[proposed adaptation]** — my inference for Galactica/T5. **[open]** — could not verify.

Convention applied throughout: the *text* of a Wikipedia policy is **[demonstrated]** (a real, inspectable artifact of a working system); claims *inside* those pages about effects ("this prevents X") are **[claimed]** unless a measurement is cited.

---

## Top findings

1. **Citation count cannot distinguish corroboration from a shared ancestor.** English Wikipedia curates "citogenesis" incidents: an unsourced edit enters the press, then the press item is cited back. Copying an error into the press is not citogenesis; citing the press item back into the article is. **[demonstrated]** (S11)

2. **Review value decays fast, and unreviewed content legitimises itself.** 90% of ever-detected hoaxes were flagged within an hour of creation, 96% within a month; ~1% survive a year. But conditional on surviving day one, a hoax has ~50% odds of another month. **[demonstrated]** (S23)

3. **The speed that catches hoaxes is implicated in killing the contributor pipeline.** By late 2007 over half of new users got their first message from an algorithmic tool; by mid-2008, 75% — alongside a retention collapse among desirable newcomers. **[demonstrated]** measurement, **[claimed]** causation. Findings 2 and 3 are in tension; do not flatten them. (S23, S24)

4. **Review capacity is far more concentrated than headcount suggests, and the queue is structural.** 887 reviewers; the top ~100 logged ~77,600 actions in 30 days (~2,600/day); one account logged 21,658 article reviews in a year (~59/day). A month-long incentivised drive moved the article queue 31,105 → 26,281, about 15%. **[demonstrated]** (S17, S18)

5. **"Due weight" is defined against source prevalence, not editor or public opinion** — "not its prevalence among Wikipedia editors or the general public." "Apparent parity between the supermajority view and a tiny minority view" is forbidden. This is the mechanism that prevents forced balance. **[demonstrated]** (S1)

6. **The no-consensus default is deliberately asymmetric.** No consensus retains the prior version — *except* for living people, where it results in removal. Removing poorly sourced contentious BLP material is also exempt from the three-revert rule. **[demonstrated]** (S5, S6)

7. **Independence, even-handedness, and bias are three different things.** "Independence does not imply *even-handedness*: an independent source may hold a strongly positive or negative view"; and "a COI can exist in the absence of bias, and bias regularly exists in the absence of a COI." **[demonstrated]** (S4, S8)

8. **The strongest sybil tool in the largest open wiki calls its own conclusions weak.** "Conclusions derived from CheckUser data have limited usefulness, and a negative finding… rarely precludes obvious sockpuppetry." Orangemoody blocked 381 accounts only by combining technical *and* behavioural evidence, within a retention window, and the scheme was found "fortuitously." **[demonstrated]** (S10, S20)

9. **Wikipedia has concluded LLM content is not reviewable at the rate it is produced.** LLM text "can be produced at a rate that makes review by other editors infeasible," backed by a process allowing reversion *without review* once a pattern of AI use is established — a governance admission disguised as a content rule. **[demonstrated]** (S12, S13)

10. **Arbitration committees are constituted so they cannot rule on content.** "The Committee does not rule on content, but may propose means by which community resolution of a content dispute can be facilitated." Conduct and content authority are separated at the top. **[demonstrated]** (S7)

## 1. Editable objects and relationships

**Findings.** Wikidata has the clearest implemented separation of content, claim, and evidence: a **claim** is a property–value pair plus optional **qualifiers**; it becomes a **statement** only when augmented with **references** and a **rank** (preferred / normal / deprecated). Two decisions are worth stealing. **Historic information is qualified, not overwritten** — "If information is no longer current, date qualifiers are added instead of statements overwritten." And **known-false information is retained and marked, not deleted** — deprecated rank "helps avoid a situation in which it's deleted and erroneously re-added as valid information." Deleting a well-cited false claim destroys the record that anyone once cited it, and the claim returns. **[demonstrated]** (S21)

Wikidata "does not aim to answer the question of whether a claim is correct, but only whether the claim appears in a reference" — a verifiability model, not a truth model, and the key precedent for a project named "Truth Attractor." **[demonstrated]** (S21)

Wikipedia separates less than it appears to: revisions are immutable and talk pages are a separate namespace, but **presentation is not separated from prose** — citation formatting, section order, infobox content, and image placement all live inside editable article text. Model **[demonstrated]**; the cost is **[proposed adaptation]**.

**Borrow.** Four object types with distinct rules — prose revision, claim, evidence snapshot, topic/scope declaration; deprecation not deletion; verdicts bound to a revision hash.
**Don't.** Wikidata's refusal to judge correctness at all. Galactica needs a third state between "cited" and "true": *reviewed and accepted, with confidence and a recheck date*.
**Implies.** Presentation is derived, not authored; views generated from claim graph plus prose by a versioned generator.
**Open.** Does a claim belong to one article or to a topic many articles render? No project I found has made the hybrid work. **[open]**

---

## 2. Scope, coverage, and splitting

**Findings.** Wikipedia has **no explicit scope field**; scope is inferred from title, lead, and talk-page convention. What it has is numeric splitting thresholds and a strong anti-forking rule. Size guideline: over 15,000 words "almost certainly should be divided or trimmed"; over 9,000 "probably"; under 6,000 "length alone does not justify division"; under 150 words for two months, consider merging. **[demonstrated]** (S14)

Splitting has exactly two reasons — **size** and **content relevance** — and the guideline is candid about failure: "undoing a split may be labor-intensive… try to avoid splitting until after a community discussion." Splits are cheap and hard to reverse. The counter-pressure is the **point-of-view fork**: "a content fork deliberately created to avoid a neutral point of view (including undue weight)." **[demonstrated]** (S15, S1, S16)

Coverage adequacy is where precedent is weakest. Wikipedia's answer is notability — "significant coverage in multiple reliable, independent, secondary sources" — which measures **source attention**, not importance, and so excludes topics nobody has written about while admitting topics whose coverage is entirely promotional. **[demonstrated]** (S3)

Wikidata, with a machine-readable model for everything else, states flatly: "Wikibase does not include any completeness indicator." Even a formal claim model cannot express "this topic is adequately covered." **[demonstrated]** (S21)

**Borrow.** Numeric, published thresholds; the two-reason split rule plus a mandatory neutrality check; reversibility as a design criterion.
**Don't.** Notability-by-press-attention as the coverage gate, or splitting without a documented merge path.
**Implies.** Scope as a first-class object with acceptance criteria; coverage adequacy as a reviewed judgment with a stated rationale, not a score.
**Open.** Is "adequate coverage" decidable by its reviewers, or does it need domain expertise Galactica will not have? **[open]**

---

## 3. Neutrality as checks, not a score

**Findings.** NPOV decomposes into separable, reviewable operations rather than a scalar. The policy's own list is a checklist — avoid stating opinions as facts; avoid stating seriously contested assertions as facts; avoid stating facts as opinions; prefer nonjudgmental language; indicate relative prominence — and each is a yes/no question about a specific sentence. **[demonstrated]** (S1)

- **Proportion** is operationalised as depth of detail, quantity of text, prominence of placement, juxtaposition, and imagery. The flat-Earth test is canonical: the Earth article does not mention modern flat-Earth belief, and that omission is *correct*. **[demonstrated]** (S1)
- **False balance** is anchored to the BBC Trust's 2011 science-impartiality policy, which warns that an opposite view without due weight makes "viewers… perceive an issue to be more controversial than it actually is." The policy's illustration: pairing a supermajority view with a tiny minority "would be to give apparent parity… by assigning each to a single activist in the field." **[demonstrated]** (S1)
- **Framing** is structurally checkable: segregating content into criticism or pro/con sections "may also create an apparent hierarchy of fact where details in the main passage appear true and undisputed, whereas other segregated material is deemed controversial." **Attribution** substitutes for omission — opinions that cannot be stated in the work's voice are attributed in-text, and weasel formulations ("many people think") are rejected. **[demonstrated]** (S1)
- **Well-supported negative information about people** gets an asymmetric layer: contentious material that is unsourced or poorly sourced "should be removed immediately and without discussion"; 3RR does not apply to such removals; and "the idea… that it is therefore okay for an article to be *temporarily* unbalanced… does not apply to biographies… biographies must be fair to their subjects at all times." **[demonstrated]** (S5)
- That protection is **not** extended to companies: "This policy does not normally apply to material about corporations, companies, or other entities regarded as legal persons." For a company the only shield is due weight and sourcing quality. **[demonstrated]** (S5)

**Borrow.** Each principle as a **named objection type** with a sentence-level anchor — proportion, framing, omitted counter-evidence, false balance — plus the asymmetric default for contested negative claims about people.
**Don't.** A "neutrality score"; weight, framing, attribution, and tone do not collapse into one dimension. Nor the full BLP apparatus at launch.
**Implies.** Review emits objections with types and anchors, not verdicts.
**Open.** How does due weight work when the reliable-source base is thin in a language? **[open]**

---

## 4. Evidence quality and provenance

**Findings.** **Circular reporting is documented at scale.** The citogenesis list holds dozens of cases with edit diffs and press citations, 2005–2021 — a fabricated Aboriginal deity with a ten-year tenure, a Dutch fish pie that reached national television. Its definition is worth adopting verbatim: it "only becomes citogenesis if next that media item is cited in the Wikipedia article as a source in support of the statement, creating a closed loop." **[demonstrated]** (S11)

**Citation laundering is described mechanistically in the literature.** Rekdal's "Academic urban legends" walks the spinach/iron decimal-point story and shows the story *itself* is an academic urban legend: Larsson (1995) misreported Hamblin (1981), and a chain of authors cited without checking, producing a claim false in its particulars yet universally repeated. He enumerates the moves — citing a secondary source as if primary; padding a weak citation with sources that all trace to one ancestor; copying a reference without reading it, which "is usually impossible to discover and to prove." **[demonstrated]** (S22)

- **Independence is a property of the relationship, not the outlet** — absence of vested interest, positive *or negative*: "an example of a negative interest is owning or working for a company that represents a competing product's article." Family, employees, and officers are non-independent. **[demonstrated]** (S4)
- **Self-published is defined by the absence of independent review** — "characterized by the *lack of independent reviewers* (those without a conflict of interest) validating the reliability of the content," with press releases and company websites named. Sponsored content counts as self-published and primary even in a reputable outlet. **[demonstrated]** (S3)
- **Retraction status is machine-checkable, and I verified it.** Crossref's REST API returns 81,345 records matching `update-type:retraction`, each carrying `update-to` entries pointing at the retracted DOI with a `source` of publisher or Retraction Watch. **[demonstrated]** (S28)
- **Staleness is not.** Wikipedia has no rule that sources expire — only "as of" dating, update tags, and a breaking-news caution. Whether a 2019 figure is still right is judgment. **[demonstrated]** (S3)
- **Company submissions** are handled by disclosure plus channel change, not exclusion: paid editors "must disclose who is paying them, who the client is, and any other relevant affiliation," and are "strongly discouraged from editing affected articles directly." **[demonstrated]** (S8, S5)

**Borrow.** Snapshot-first; a **provenance graph** rather than a citation list; deprecation over deletion; disclosure as declared/observed/verified.
**Don't.** "Multiple independent sources" as a checkbox, or publisher prestige as a proxy for independence.
**Implies.** A **shared-origin signal** as a first-class field (publisher, author, wire, release, cited ancestor) — computable from metadata, with a residual that is recorded judgment.
**Open.** Can shared-origin detection work across languages without a shared identifier? **[open]** What is the right response when a source is retracted after acceptance? **[open]**

---

## 5. Contribution and review

**Findings.** **Onboarding is a separate gated path with its own queue.** Articles for Creation lets anyone submit a draft for review, is the *required* route for conflicted editors, and is where prohibitions live — including "Do not use large language models to write your draft." **[demonstrated]** (S12)

**Identity is behavioural, not verified.** Every permission tier is an activity threshold: 10 edits/4 days, 500 edits/30 days; 2.65M accounts clear the first bar, most inactive. The sockpuppetry policy now refers to "temporary accounts" where it previously referred to IP addresses, effective 2025-11-04. **[demonstrated]** (S19, S9)

- **Reviewer permission is separately granted and accountable.** 887 New Page Reviewers (1,703 hold the permission including admins) — and "reviewers have no technical authority over new articles: actual deletions can only be made by administrators." Checkusers are appointed by the Arbitration Committee with a 70% support threshold, must be 18+, and must sign a confidentiality agreement. **[demonstrated]** (S17, S10)
- **Procedures are a ladder:** talk page → third opinion → mediation → noticeboard → request for comment; conduct goes to the incidents noticeboard, then arbitration. At the bottom: "if your change is reverted, continue to explain yourself; do not start an edit war." **[demonstrated]** (S29, S6)
- **Rollback is cheap and asymmetric by design.** Any editor may revert; the burden sits with the reverter to explain. Two exceptions invert this: BLP removals are exempt from 3RR, and presumptive removal allows reverting "without review," with the reverser then required to review content and sources. **[demonstrated]** (S5, S13)
- **Policies change by proposal and high consensus, and most new policy ratifies existing practice** — "most commonly, new policies or guidelines document established practices." Essays are explicitly not policy. **[demonstrated]** (S6, S30)
- **Authority is layered.** The community is normally self-governing; the Foundation "reserves certain legal rights" and can act via office actions, described as rare; the Universal Code of Conduct is Board-ratified and "enforced at the most relevant local level possible." **[demonstrated]** (S30, S31)

**Borrow.** Two-track onboarding — open proposal track, separate reviewer permission track. Published activity thresholds. **Reviewers cannot delete**: separate "recommend" from "publish/remove." A "documents existing practice" fast path for policy.
**Don't.** That a persistent account is a person; or lifetime tenure for reviewers.
**Implies.** Identity as **a set of claims, each with a source and confidence** — observed, declared, or verified, never a boolean.
**Open.** What is the appeal path for an *agent* account that has been throttled? **[open]**

---

## 6. Sybil resistance and coordinated campaigns

**Findings.** **Technical sybil detection is weak and its practitioners say so.** CheckUser can tie accounts to IPs and user agents, and its policy still concludes that findings have "limited usefulness" and that "a negative finding… rarely precludes obvious sockpuppetry." **[demonstrated]** (S10)

**The strongest documented enforcement action still needed luck.** Orangemoody (2015) was a paid-editing extortion scheme: get a promotional draft into article space — "it will frequently be marked reviewed by another sock" — then demand payment to "protect" the article, sometimes nominating it for deletion when payment stopped. The investigation blocked 381 accounts, "all… linked by both technical data **and** behavioural evidence," needed many functionaries plus WMF Community Advocacy, and was limited to accounts active late April–early August by checkuser retention. The page states the scheme "had been in place for some time before it was fortuitously identified." This is the most instructive artifact I found, because the attack targeted the **review pipeline**: a sock marking another sock's article as reviewed is a sybil attack on the reviewer role, and no content-level check catches it. **[demonstrated]** (S20)

- **Community defences are judgment rules, not rate limits.** Canvassing policy prohibits "any effort to gather participants to a community discussion that has the effect of biasing that discussion" while permitting neutral notices; consensus policy holds that "off-wiki discussions… are not taken into account"; sockpuppetry policy holds that "policies apply per person, not per account" — unenforceable in software. **[demonstrated]** (S32, S6, S9)
- **Rate limits are crude and low:** new and temporary accounts 8 edits/minute; account creation 6/day per IP; rollbackers 100 rollbacks/minute. Anti-flooding, not sybil resistance. **[demonstrated]** (S19)
- **Backoff is undocumented.** I found no project publishing a calibrated backoff schedule — how long a throttled contributor waits, how it is computed, how it is appealed. **[open]**
- **Scaling review with automation has a supply-side cost.** Halfaker et al. document that algorithmic tools made quality control faster *and* that newcomers' first interactions became automated warnings — over half by late 2007, 75% by mid-2008 — alongside a sharp retention decline. **[demonstrated]** measurement, **[claimed]** causation (S24)

**Borrow.** **Weight reviews, not just edits**; **sampled re-review of reviewers** (NPP drives already award credit for re-reviewing others' patrols); behavioural clustering as a first-class signal.
**Don't.** IP-based identity, or "one account = one person" as a data-model invariant.
**Implies.** Sybil resistance is **review-capacity protection**: rate-limit proposal volume, require proposer–reviewer independence, sample-audit, publish results.
**Open.** Do agent-authored contributions make sybil attacks cheaper or more expensive? I found no measurement. **[open]**

---

## 7. Separation of factual review, editorial judgment, and community preference

**Findings.** Mature projects keep three questions apart, and the separation is encoded in **venue**, not just principle.

- **Factual/sourcing** → the reliable-sources noticeboard, which "seeks to apply this policy to particular cases"; the output is a judgment about a source for a statement, not about whether the statement belongs. **[demonstrated]** (S2, S3)
- **Editorial/neutrality** → the NPOV noticeboard, resolved by editing and talk-page consensus. **[demonstrated]** (S1)
- **Community preference** (does this topic merit an article) → deletion discussions, where consensus is "ascertained by the quality of the arguments… as viewed through the lens of Wikipedia policy" — explicitly not headcount. **[demonstrated]** (S6)
- **Conduct** → incidents noticeboard, then arbitration, which "does not rule on content." **[demonstrated]** (S7)

Two further separations: **content review ≠ contributor review** — "the purpose of new pages patrol is to review the *content* of new pages, not the *conduct* of the editors who created them"; and **recommendation ≠ authority** — reviewers mark pages reviewed, only administrators delete. **[demonstrated]** (S17)

The known failure mode is **forum shopping**: "raising essentially the same issue on multiple noticeboards… in the hope of finding one where you get the answer you *want*." The policy names it but has no detection mechanism beyond editor vigilance. **[demonstrated]** (S6)

**Borrow.** Venue as a type (factual / editorial / scope / conduct), with the system refusing to route a factual objection to a preference vote; policy-grounded closing; one open venue per dispute.
**Don't.** That a well-informed generalist can adjudicate all three; noticeboards work because thousands of specialists self-select.
**Implies.** Three review types with different reviewers, rubrics, and appeal paths; collapsing them into "review" is the likeliest governance failure in an agent-heavy system.
**Open.** Who adjudicates when a factual and a scope question are entangled? **[open]**

---

## 8. Abuse, prompt injection, malicious source material

**Findings.** **Indirect prompt injection is a demonstrated structural vulnerability.** Greshake et al. show that LLM-integrated applications "blur the line between data and instructions," that an adversary can "remotely… exploit LLM-integrated applications by strategically injecting prompts into data likely to be retrieved," and demonstrate attacks against "real-world systems, such as Bing's GPT-4 powered Chat." Conclusion: "effective mitigations… are currently lacking." **[demonstrated]** attacks; the mitigations claim is the authors' 2023 assessment. (S25)

**Defences exist but are benchmark-level, and they cost capability.** *Spotlighting* (Hines et al., 2024) transforms untrusted input so the model can distinguish provenance, reporting a reduction in attack success "from greater than 50% to below 2%" — **[claimed]**, the authors' benchmark, not a field measurement. *CaMeL* (Debenedetti et al., 2025) extracts control and data flow from the trusted query so untrusted data "can never impact the program flow," solving "77% of tasks with provable security (compared to 84% undefended)" on AgentDojo — **[demonstrated]** in that benchmark, with a ~7-point capability gap as the honest headline. (S26, S27)

**Wikipedia's response is procedural, not technical.** It prohibits LLM generation of article content and has built **presumptive removal**: once an editor is determined to have a history of AI use, "edits to existing pages may be reverted without review," and sole-authored articles may go through a special proposed-deletion process. The safeguard: "any editor can reverse a presumptive removal," and must then review content and sources. Note the contradiction the policy concedes — sanctioning LLM use "requires evidence beyond basic stylistic or linguistic indications," because "the writing style of some editors may appear similar to the output of LLMs." Detection is unreliable, so the policy shifts the burden of proof onto the contributor. **[demonstrated]** (S12, S13)

**Borrow.** Every fetched page is data: the reading agent holds no publication authority and no write tools; provenance signalling on input; presumptive removal with a cheap reversal path.
**Don't.** Any claim that a defence is "solved" — both defence papers are benchmarks, not deployment data.
**Implies.** A source snapshot is **hostile input**; ingestion must not invoke tools, change policy, or write to the claim graph without a separate typed step.
**Open.** Does the read/write split survive a workflow where one agent must both read and propose? **[open]** What happens when a snapshot changes after capture? **[open]**

---

## Cross-cutting

### What is machine-checkable

| Check | Why mechanical | Basis |
|---|---|---|
| Claim text is a substring of the cited snapshot | String containment against immutable capture | S3, S11 |
| Quoted passage appears verbatim | Same, with normalisation | S3 |
| Snapshot hash unchanged since capture | Content addressing | Workshop |
| Cited URL is dead / non-200 | HTTP fetch | Workshop |
| DOI is retracted | Crossref `update-type:retraction`, `update-to` | S28 (81,345 records) |
| Source on deprecated/blocked list | List lookup | S3, S17 |
| Source is self-published by the subject | Domain/ownership match | S3, S4 |
| Two citations share publisher, author, or DOI ancestor | Graph query over metadata | S11, S22 |
| Claim contradicts a later typed claim in the same topic | Structured comparison | S21 |
| Revision unchanged since review | Hash comparison | Workshop |
| Contributor is proposer and reviewer of the same revision | Identity comparison | S9, S20 |
| Review arrived within N seconds of proposal | Timestamp delta | S17 |
| Account age / edit count / prior rejections | Counters | S19 |
| Edit rate exceeds threshold | Rate counter | S19 |
| Article exceeds size band | Word/claim count | S14 |
| Claim added by an account later blocked for a stated cause | Join | S13 |
| Objection anchor resolves to an existing sentence | Anchor resolution | S1 |

### What remains judgment

Whether a source is **independent in substance** (metadata can be identical for a wire story and an original report) · whether **weight** matches source prevalence (depth, placement, juxtaposition are readable, not computable) · whether a **counter-view was omitted** and whether the omission is proportionate or a framing choice · whether two differently-named sources share an origin (same embargo, stringer, PR firm) · whether a source is **stale** in a way that matters · whether **coverage is adequate** for a declared scope (no inspected system computes it; Wikidata says so explicitly) · whether a **split is a POV fork** · whether an account is a **distinct person** (CheckUser's own policy calls this weak) · whether a **review was competent** (only sampling and re-review addresses this, and the sampling decision is itself judgment) · whether an **appeal is in good faith** · whether retrieved text contained an **injection** the model failed to resist (you can detect the effect, not the intent).

---

### Review capacity arithmetic

- 887 New Page Reviewers; 1,703 users hold the permission including administrators. **[demonstrated]** (S17)
- Unreviewed backlog on 2026-09-01: **31,105** articles, **56,894** redirects. **[demonstrated]** (S17)
- After a month-long, barnstar-incentivised drive (2026-10-01): **26,281** articles, **48,836** redirects — ~4,800 articles and ~8,100 redirects cleared, roughly 15% of each queue. **[demonstrated]** (S17)
- Top ~100 patrollers: ~**77,600** actions in the trailing 30 days (~2,600/day) as of 2026-11-04. One account: **21,658** article reviews in 365 days (~59/day); another 24,064 redirect reviews. **[demonstrated]** (S18)

**What that implies.** 31,105 ÷ 887 ≈ 35 items per reviewer — trivial. The binding constraint is the number of *active* reviewers and time per item. One account doing 59 article reviews a day, every day, for a year is a single point of failure, and it is the production system for the world's largest reference work. If the queue is persistently ~30,000 and drives recur every ~4 months, inflow is approximately maximum surge capacity and the backlog is the buffer, not an accident. **[proposed adaptation]** — inference from persistence, not measured inflow.

**Why "open the gates" fails, three distinct ways.**

1. *Arithmetic.* At ~2,600 review actions/day, any proposal volume rising faster makes review into sampling. Sampling is not automatically bad, but it must be **risk-weighted**; uniform sampling systematically misses low-volume, high-consequence cases — exactly the ones that matter.
2. *Timing.* Review value decays fast: 90% of ever-detected hoaxes caught within an hour, and by a month the marginal review finds almost nothing new. Content that survives a day has ~50% odds of surviving a month. Late review is mostly wasted effort. **[demonstrated]** (S23)
3. *Supply.* The machinery that makes high-volume review possible is the machinery that drives contributors away: automated warnings reached 75% of new users by mid-2008 and coincided with a retention collapse. Opening the gates while scaling enforcement is self-defeating — you review more submissions from a shrinking pool. **[demonstrated]** measurement, **[claimed]** causation (S24)

**Calibration.** The only calibration data I found is the hoax study's human-vs-machine comparison: 66% vs 86% on one task class. It should not be treated as a general estimate of reviewer accuracy. **[demonstrated]** but narrow (S23). The workshop's policy lab currently assumes catch rates and correlation; the research gives no basis for those beyond this one number, and the honest position is that they remain **[open]** until measured from recorded review runs.

**Operating rule [proposed adaptation]:** review at creation or not at all; treat post-hoc review as audit, not gatekeeping; cap proposal volume per account well below reviewer capacity; publish the ratio of proposals to available review hours so that "open the gates" is an argument about a number rather than a sentiment.

---

## Sources checked

All accessed **2026-11-04**. Every source cited inline has a row here. Two pages were fetched only to confirm cross-references and are not otherwise relied on: Wikipedia:Summary_style and Wikipedia:Ownership_of_content.

| # | URL | What it is | Label | Lesson borrowed |
|---|---|---|---|---|
| S1 | https://en.wikipedia.org/wiki/Wikipedia:Neutral_point_of_view | NPOV policy | [demonstrated] | Weight by source prevalence, not editor opinion; false balance named; structure creates a hierarchy of fact |
| S2 | https://en.wikipedia.org/wiki/Wikipedia:Verifiability | Verifiability policy | [demonstrated] | Exceptional claims need multiple high-quality sources; mirrors and Wikipedia itself are not sources |
| S3 | https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources | Reliable sources guideline | [demonstrated] | Self-publishing defined by absence of independent review; sponsored content is primary; LLM output unreliable |
| S4 | https://en.wikipedia.org/wiki/Wikipedia:Independent_sources | Independence supplement | [demonstrated] | Independence ≠ even-handedness; negative vested interest also disqualifies |
| S5 | https://en.wikipedia.org/wiki/Wikipedia:Biographies_of_living_persons | BLP policy | [demonstrated] | Immediate removal without discussion; no eventualism for biographies; does not cover companies |
| S6 | https://en.wikipedia.org/wiki/Wikipedia:Consensus | Consensus policy | [demonstrated] | Quality of argument, not headcount; no-consensus default asymmetric for BLPs; off-wiki discussion ignored |
| S7 | https://en.wikipedia.org/wiki/Wikipedia:Arbitration/Policy | Arbitration policy | [demonstrated] | "The Committee does not rule on content" |
| S8 | https://en.wikipedia.org/wiki/Wikipedia:Conflict_of_interest | COI guideline | [demonstrated] | COI is situational, not a judgment of integrity; COI and bias orthogonal; paid disclosure required |
| S9 | https://en.wikipedia.org/wiki/Wikipedia:Sockpuppetry | Sockpuppetry policy | [demonstrated] | Meatpuppetry prohibited; "policies apply per person, not per account"; temporary accounts replaced IPs 2025-11-04 |
| S10 | https://en.wikipedia.org/wiki/Wikipedia:CheckUser | CheckUser policy | [demonstrated] | Technical sybil evidence weak by its own account; 70% arb support, 18+, NDA |
| S11 | https://en.wikipedia.org/wiki/Wikipedia:List_of_citogenesis_incidents | Curated circular-reporting incidents | [demonstrated] | Citation count cannot distinguish corroboration from a shared ancestor; closed loop is the definition |
| S12 | https://en.wikipedia.org/wiki/Wikipedia:Writing_articles_with_large_language_models | LLM content guideline | [demonstrated] | LLM output "produced at a rate that makes review… infeasible"; detection needs evidence beyond style |
| S13 | https://en.wikipedia.org/wiki/Wikipedia:Presumptive_removal_of_AI-generated_content | Deletion guideline | [demonstrated] | Revert without review on established pattern; any editor may reverse but must then review |
| S14 | https://en.wikipedia.org/wiki/Wikipedia:Article_size | Size guideline | [demonstrated] | Published thresholds end arguments: 15k split, 9k probably, 6k no, 150 words merge |
| S15 | https://en.wikipedia.org/wiki/Wikipedia:Splitting | Splitting procedure | [demonstrated] | Two reasons only (size, relevance); splits expensive to undo, so discuss first |
| S16 | https://en.wikipedia.org/wiki/Wikipedia:Content_forks | Forking guideline | [demonstrated] | POV fork as evasion; single source of truth preferred |
| S17 | https://en.wikipedia.org/wiki/Wikipedia:New_pages_patrol | NPP information page | [demonstrated] | 887 reviewers; content review ≠ conduct review; reviewers cannot delete; 31,105→26,281 articles, 56,894→48,836 redirects |
| S18 | https://en.wikipedia.org/wiki/Wikipedia:Database_reports/Top_new_article_reviewers | Bot-generated leaderboard | [demonstrated] | Extreme concentration: one account, 21,658 article reviews in 365 days |
| S19 | https://en.wikipedia.org/wiki/Wikipedia:User_groups | User access levels | [demonstrated] | All permissions are observed-behaviour thresholds; 8 edits/min, 6 accounts/day/IP; 2.65M autoconfirmed |
| S20 | https://en.wikipedia.org/wiki/Wikipedia:Long-term_abuse/Orangemoody | Incident record | [demonstrated] | 381 accounts blocked on technical + behavioural evidence; attack targeted the review role itself |
| S21 | https://www.wikidata.org/wiki/Wikidata:Glossary | Wikidata data model | [demonstrated] | Claim/statement/reference/rank; deprecate not delete; no completeness indicator; verifiability not truth |
| S22 | https://pmc.ncbi.nlm.nih.gov/articles/PMC4232290/ | Rekdal, "Academic urban legends", *Soc. Stud. Sci.* 44(4), 2014 | [demonstrated] | Mechanisms of citation laundering; the laundered claim is often false in its particulars |
| S23 | https://dlab.epfl.ch/people/west/pub/Kumar-West-Leskovec_WWW-16.pdf | Kumar, West & Leskovec, "Disinformation on the Web", WWW 2016 | [demonstrated] | 90% of hoaxes caught within an hour; survivors self-legitimise; humans 66% vs classifier 86% |
| S24 | https://stuartgeiger.com/papers/abs-rise-and-decline-wikipedia.pdf | Halfaker et al., *Am. Behav. Sci.* 57(5), 2013 | [demonstrated] / [claimed] | Algorithmic enforcement reached 75% of new users by mid-2008; efficiency coupled to retention collapse |
| S25 | https://arxiv.org/abs/2302.12173 | Greshake et al., indirect prompt injection, 2023 | [demonstrated] | Data/instruction boundary unenforced; attacks shown against Bing Chat; mitigations lacking |
| S26 | https://arxiv.org/abs/2403.14720 | Hines et al., "Spotlighting", 2024 | [claimed] | Provenance signalling cuts attack success >50% → <2% in the authors' benchmark |
| S27 | https://arxiv.org/abs/2503.18813 | Debenedetti et al., "CaMeL", 2025 | [demonstrated] | Provable security via control/data-flow separation, at ~7 points of task capability |
| S28 | https://api.crossref.org/works?filter=update-type:retraction | Crossref REST API, retraction filter | [demonstrated] | 81,345 retraction records with `update-to` links; retraction status machine-checkable |
| S29 | https://en.wikipedia.org/wiki/Wikipedia:Dispute_resolution | Dispute resolution policy | [demonstrated] | Escalation ladder; explain, do not edit-war |
| S30 | https://en.wikipedia.org/wiki/Wikipedia:Policies_and_guidelines | Policy process | [demonstrated] | High-consensus bar; new policy usually ratifies practice |
| S31 | https://foundation.wikimedia.org/wiki/Policy:Universal_Code_of_Conduct/Enforcement_guidelines | UCoC enforcement guidelines | [demonstrated] | Board-ratified, part of ToU, enforced at the most local level possible |
| S32 | https://en.wikipedia.org/wiki/Wikipedia:Canvassing | Canvassing guideline | [demonstrated] | Bias effect, not intent, is the test |

---

## What I could not verify

- **COPE retraction guidelines.** `publicationethics.org` returned HTTP 403 behind Cloudflare on every attempt (PDF and guidance page). I substituted Crossref retraction metadata, which is different evidence: it tells you a retraction exists, not what COPE advises an editor to do. "How to handle a retraction" remains **[open]**.
- **Actual proposal inflow rates** for any project. Backlog snapshots give net change, not gross inflow; my "surge capacity ≈ inflow" is inference.
- **Any measurement of sybil-resistance effectiveness** — cost per successful campaign, detection rate, false-positive rate. The Orangemoody record is narrative, not evaluation.
- **Any project that computes coverage adequacy.** Wikidata explicitly does not; Wikipedia's notability proxy measures attention. I looked and did not find one.
- **Adversarial deployment data for prompt-injection defences.** Both defence papers are benchmark evaluations; I found no field report under sustained attack.
