# Launch and participation plan

**Version:** 1.0, 2026-11-04.
**Purpose:** a staged path from the local workshop to a public reference, with dependencies, observable readiness
criteria, and an explicit definition of "strong launch". This is a proposal, not a schedule commitment. Dates are
relative to a go-ahead decision.
**Companion:** [product spec](PRODUCT-SPEC.md) · [decision register](DECISION-REGISTER.md) ·
[experiments](EXPERIMENTS.md) · [worked examples](WORKED-EXAMPLES.md) · [technical research](research/03-technical-launch.md).

---

## 1. Premise

The historical evidence is consistent on one point: **content supply is not the binding constraint; review
capacity and a credible correction path are.** Nupedia approved roughly 24 articles in about three years under
expert review; Wikipedia produced about 18,000 in its first year once review friction dropped. Citizendium fell
below 100 active members. Knol never found an audience and deleted its corpus. Grokipedia reached 800,000 articles
at launch, then went effectively frozen for months; its traffic fell from a launch spike to a much smaller
baseline. Article count is the cheapest possible metric and the least informative.

The plan therefore gates each stage on **review health, correction responsiveness and demonstrated usefulness**,
not on corpus size.

---

## 2. Who the first readers and contributors are

**First readers (private alpha / public beta):**
- Practitioners and researchers who need a citable overview of a narrow domain (methods, standards, regulated
  topics, software ecosystems).
- Students and analysts who need to verify a specific claim and see its evidence.
- Journalists and policy staff who need a revision they can cite and a correction path.
- Agent operators whose agents need a stable reference with claim IDs and an API.
- Experienced Wikipedia editors who want a claim-level evidence model and a faster correction loop.

**What makes them return:** a specific recurring task, a stable permalink to cite, visible correction history,
notification when a claim they care about is challenged, fast review turnaround, and attribution. Experts invest
when they can cite a revision; agents return when the API is reliable and the evidence resolves.

**First contributors (10–20 invited):**
- 3–5 domain experts with a topic they already maintain or teach.
- 3–5 experienced Wikipedia/other wiki editors who understand sourcing and dispute culture.
- 2–4 agent operators with a concrete agent use case and a track record.
- 1–2 organizations with factual material and a willingness to disclose (not to advertise).
- 1 translator/reviewer for the language pilot.

**What makes them return:** a topic they care about, a review queue that responds, a visible correction they
made, attribution, and a citable revision. Do not recruit with volume incentives or paid growth.

**Not first:** the general public, SEO traffic, adversarial subjects, real living-person/company cases without
legal/privacy review, and contributors who only want a backlink.

**How to recruit:** personal invitations, relevant practitioner communities, wiki noticeboards, agent-operator
forums, and existing professional networks. Ask for one topic, not a commitment to a platform.

---

## 3. Stage 0 — Internal dogfood (2–4 weeks)

**Objective:** prove the full loop works without data loss and that the team can operate it.

**Scope**
- 3–5 topics, including at least one ordinary topic and one contested topic.
- 2 human operators (Justin + one trusted reviewer) and 1 agent contributor.
- No public contribution; a private preview is allowed.
- Use the existing Django workshop; no deployment beyond a private host.

**Work**
1. Implement the minimum reliable core (see §8): publication events, permalink URLs, idempotency keys, stale-base
   errors, backup/restore drill, export manifest, license fields, FTS5 index.
2. Run the existing editorial loop end to end: draft → propose → review → decide → publish → correct → revert.
3. Exercise the correction intake manually (a form + spreadsheet is acceptable for dogfood).
4. Run the first view pilot: a timeline and a table pinned to a revision; change the base and verify staleness.
5. Run a restore drill: restore the backup into a fresh environment, boot the app, verify row counts and a content
   hash; record the time.
6. Write the contributor guide, reviewer guide and correction policy v0; they will be wrong, but writing them
   exposes gaps.

**Dependencies**
- Decision on the minimum topic/assertion schema (D-03/D-05) or a deliberate interim.
- A second human reviewer with enough time to review 10–20 proposals.
- A backup target (local + off-host) and a restore procedure.

**Readiness criteria (observable)**
- 10 published revisions across 3–5 topics, each with claim-level citations and snapshots.
- 5 corrections processed end to end, with public notices.
- 3 proposals reviewed by 2+ reviewers, including one rejection and one appeal (manual is fine).
- A timeline/table view published and then marked stale by a base change; a new version published.
- Restore drill passed with row counts and a content hash; RPO/RTO recorded.
- No P0 data-loss, security or legal issue open.
- The test suite passes; a smoke script exercises the public read path.

**Exit decision:** proceed to private alpha only if the loop is boring and repeatable. If review takes longer
than expected, that is a finding, not a failure; adjust scope.

---

## 4. Stage 1 — Private alpha (6–8 weeks)

**Objective:** calibrate review capacity and editorial quality with real contributors on a small anchor corpus.

**Scope**
- 10–20 invited contributors: domain experts, experienced Wikipedia editors, agent operators, one or two
  organizations (with disclosure).
- **5–8 anchor topics in one wedge**, plus internal fixtures in `/sandbox`.
- Private or unlisted public read; contribution by invitation.
- One language (English) and one reading level; no maps/charts unless a topic demands it.

**Work**
1. Implement topic/scope, assertion tracking (at least for disputed/high-value claims), correction intake with
   states, and the review-role split.
2. Build the anchor corpus with a named steward per topic and a coverage checklist.
3. Measure review time by risk class on at least 50 proposals; derive the first quota/capacity numbers.
4. Run the reviewer calibration set (known cases) and record false-support/false-object rates.
5. Run a source-assessment pilot on 30 sources; record disagreements and appeals.
6. Run a small reader usability test (5–8 target readers) on 3 articles; measure task success and evidence use.
7. Write the appeals procedure and run one simulated appeal.
8. Confirm the working name for alpha branding; the final name decision (D-01, open — keep Galactica, T5/t5.wiki
   short-listed) is deferred until before public beta.

**Dependencies**
- Review capacity: at least 2 active human reviewers besides Justin, or a reduced scope.
- A legal/privacy review for BLP/company content; hypothetical cases first.
- A privacy-respecting analytics plan (aggregate, no cross-site tracking).

**Readiness criteria**
- 10 articles meet the quality bar (scope, coverage, citations, neutrality checks, readability, mobile).
- Median review time measured by risk class; review demand ≤ 80% of measured capacity for 4 consecutive weeks.
- 5 reader corrections resolved; median acknowledgment < 2 business days; substantive resolution < 14 days.
- 3 agent API consumers (internal or partner) can read a revision, propose, and receive a reviewable outcome.
- Reviewer calibration results recorded; at least one reviewer coached or removed.
- One source-assessment appeal handled with a public reason.
- No unresolved legal/COI issue.

**Exit decision:** public read + correction intake only if the correction path and review health are credible.
If not, stay in alpha and fix the bottleneck.

---

## 5. Stage 2 — Public beta: read + corrections (8–12 weeks)

**Objective:** learn whether the reference is useful to real readers and whether corrections arrive and get
resolved.

**Scope**
- 20–30 topics in the wedge and adjacent areas; public reading; public correction intake; contribution by
  application/waitlist.
- Search, evidence drawer, history, dispute pages, and 2–3 view types.
- No public auto-publication; no open agent write access beyond invited/approved operators.

**Work**
1. Public launch of the read surface with a clear "beta" label and a public changelog.
2. Correction intake at the top of every article; a public correction log; a status page for correction SLAs.
3. Search quality evaluation: 50 queries with expected topics; recall@3, MRR, zero-result review.
4. Accessibility audit on article, evidence drawer, history, correction form; fix P0/P1 issues.
5. Mobile pass on the same flows; test on a low-end device and a slow connection.
6. Reader survey + 10 interviews; "would you miss it?" and task-based questions.
7. Downstream citation pilot: 3–5 agents/services cite specific revisions; track resolution.
8. Publish the first transparency report (proposals, reviews, corrections, appeals, incidents).

**Dependencies**
- Counsel sign-off on licensing (D-30) before public exports or API redistribution. The license choice itself was
  accepted 2026-11-04 (CC BY-SA 4.0 articles + CC0 identifiers/templates), subject to counsel.
- Terms of use, privacy policy, takedown process.
- A named person for correction triage and a backup.
- Monitoring/alerting and an incident runbook.

**Readiness criteria**
- Reader task success ≥ baseline +10 points on two tasks, with ≥24 participants and a named baseline.
- Correction p90 acknowledgment ≤2 business days; p90 substantive resolution ≤14 days; backlog <1 week.
- Review-hour ratio ≤80% for 4 consecutive weeks; no proposal older than 30 days without a decision.
- 3 external citations from uninvolved parties that still resolve after 30 days.
- Search recall@3 ≥80% on the query set; zero-result rate <10%.
- WCAG 2.2 AA audit: no open P0/P1 issues on core flows.
- 10 active contributors (human or agent operators); 5–8 anchor-quality articles in the wedge.
- Backup/restore drill repeated; incident runbook tested with a tabletop exercise.
- Distribution: at least one named channel and one partner target active; referral source measured.

**Exit decision:** open contribution only if review capacity can absorb it without lowering quality. If
correction volume exceeds capacity, fix triage before opening writes.

---

## 6. Stage 3 — Public contribution with tiered review (3–6 months)

**Objective:** a sustainable contributor community with risk-based review, credible appeals, and a measured
case for (or against) limited autonomy.

**Scope**
- 100–200 topics; public proposals; agent contributions at scale with quotas.
- Risk-tiered review: human gate for standard/high/contentious; a shadow-mode evaluation for cosmetic/low.
- 1–2 additional languages, only with named reviewers.
- Dispute/appeal process with a panel.

**Work**
1. Open proposals with quotas and admission control; publish the queue/capacity dashboard.
2. Run the shadow-mode autonomy evaluation for cosmetic/low; compare would-be auto-publications to human
   decisions; measure false-approval and escape rates.
3. Implement appeals with a 3-person panel and public reasons; run 5 real appeals.
4. Implement disputes for assertions/scope; run 3 disputes to resolution.
5. Keep summary/timeline/table as revision content; implement the derived-view lifecycle for one
   translation/audio/chart pilot; measure staleness and re-review cost.
6. Add one language pilot with a named reviewer and translation review.
7. Publish quarterly transparency reports; hold a public policy comment period for one change.
8. Review the published transition trigger and decide whether to create a foundation earlier (D-34 accepted
   2026-11-04: published-trigger approach; a foundation can wait or come earlier, but none is created now).

**Dependencies**
- Measured review capacity and catch rates (from alpha/beta).
- A policy version for tiered review, with a kill switch.
- A second reviewer pool and an appeals panel.
- Legal review for the language pilot and any real BLP/company content.

**Readiness criteria**
- Review demand ≤ 80% of capacity for 8 consecutive weeks.
- 30 active contributors; 5+ returning domain experts; contributor 90-day retention measured.
- 5 appeals decided; reversal rate and reasons published.
- 3 disputes resolved; no unresolved conduct incident.
- Shadow-mode evaluation meets the published threshold (or autonomy is rejected and documented).
- One policy change completed via public comment.
- Two languages with named reviewers and a translation quality check.
- No P0 security/legal incident; incident postmortems published.

**Exit decision:** expansion (more languages, maps/charts, commercial API, governance transition) only after the
trust loop is stable and measured. Do not expand to mask a review or correction problem.

---

## 7. Seed corpus

**Public launch corpus: 5–8 topics in one narrow, citation-costly domain**, with a named expert reviewer. The
12-topic matrix below is for **internal fixtures and `/sandbox` demonstrations**, not the public corpus. A broad
sampler competes with Wikipedia on its strongest ground; a wedge gives a reader a reason to choose this site and
an expert a reason to contribute. Candidate wedges: a regulated technical domain, methods/statistics, or an
ecosystem's operational knowledge. Choose one with a named expert.

The capability matrix:

| # | Topic | Why it earns a slot | Views / evidence | Risk |
|---|---|---|---|---|
| 1 | Cardboard / corrugated fiberboard | Ordinary object; clear definitions, history, manufacture, recycling; tests the everyday reader path | Table of material types; timeline of patents; recycling data | Low |
| 2 | Invention of the telephone | Contested history with multiple claimants and national narratives; tests neutrality, attribution and due weight | Timeline; comparison table of claimants; source assessment | Standard |
| 3 | A hypothetical company with a regulatory finding | Tests company submission, COI, negative information, right of reply, legal review | `/sandbox` only; excluded from search/exports | High (hypothetical) |
| 4 | A hypothetical living person with a retraction | Tests BLP, privacy, correction, appeal, emergency rollback | `/sandbox` only; excluded from search/exports | High (hypothetical) |
| 5 | A fast-moving science/technology topic | Tests currency, stale views, uncertainty, rapid corrections | Timeline; "as of" panel; change log | Standard |
| 6 | A river basin or mountain range | Tests map/spatial data, regional variation, data sources | Map; table of tributaries; "as of" | Low/standard |
| 7 | A historical event with a timeline | Tests dates, causality, sourcing, commemoration disputes | Timeline; dispute page | Standard |
| 8 | A contested term (e.g., "open-source AI") | Tests definitions, disputed terminology, scope, regional usage | Definition box; terminology note | Contentious |
| 9 | A practical process (e.g., paper recycling) | Tests how-to clarity, safety, regional rules, accessibility | Step table; "check local rules" | Low |
| 10 | A dataset-backed topic (e.g., electricity mix) | Tests chart/table views, data provenance, "as of", licensing | Chart/table; dataset manifest | Standard |
| 11 | A well-supported but controversial health topic | Tests consensus vs false balance, negative information, BLP-adjacent care | Internal fixture; public only with policy/legal reviewer | High (out of scope at launch) |
| 12 | A topic with strong non-English sources | Tests language edition, translation review, shared assertions | Language variant; translation note | Standard |

**Rules for the first pass**
- Hypothetical company/person cases live in `/sandbox`, excluded from search, exports and anchor counts; real
  living-person/company content is out of scope at launch.
- Every public anchor topic has a named steward, a scope statement, a coverage checklist and at least one
  reviewer independent of the author.
- Do not choose a topic solely because it is easy to generate; choose it because a target reader would use it.
- Do not launch a topic category without a maintenance plan and a reviewer.

**What not to seed**
- Breaking news or a topic where being wrong could cause immediate harm.
- A living person's contested allegations without legal review.
- A topic that exists only to demonstrate a view type (e.g., a map with no data).
- A topic copied from Wikipedia without attribution and independent review.

---

## 8. Minimum reliable core vs. deliberately later

### Must be reliable at launch (public beta)

| Item | Why it cannot wait |
|---|---|
| Immutable revisions, content hash, stable permalink URL | Every citation, correction, export and review depends on a citable address. Retrofitting breaks external citations. |
| Append-only publication events | "Published on date X" cannot be reconstructed from a mutable pointer after the next publish. |
| Claim/citation bound to revision with snapshot hash | The core promise is inspectable evidence; a hash added later cannot prove what was cited. |
| Optimistic concurrency + explicit stale-base error | Concurrent agents are normal; silent overwrite is unrecoverable trust damage. |
| Idempotency keys on proposal/review/job creation | Retries are guaranteed; duplicates poison the queue. |
| Nightly backup + restore drill + off-host copy | The first data loss is the last chance to test recovery. |
| Nightly export with manifest (even if private) | The only independent copy; forces a serializable schema. |
| License and attribution fields | Cannot be retroactively imposed on contributors. |
| FTS5 index of published revisions with rebuild + integrity check | Search is the primary read path; a drifted index teaches readers the site is unreliable. |
| Rate limits, `Retry-After`, problem+json error codes | External agents will find the limits anyway; undocumented limits produce bans and bug reports. |
| Correction intake + tracking + public notice | The correction path is the product's credibility; a form alone is not a process. |
| Moderation queue metrics + incident log | Launch is when actual review capacity is learned; measuring later means guessing. |
| Accessibility on core flows | Retrofitting accessibility is expensive and excludes readers. |

### Deliberately later

| Item | Why it can wait |
|---|---|
| CRDT co-editing | Only pays off with many simultaneous editors of one draft; adds merge semantics nobody reviews. |
| Dedicated search cluster | One SQLite file handles the launch corpus; a projection table keeps the migration path open. |
| Multi-region/streaming replication | Single-host SQLite is the stated envelope; replication without tested failover is decoration. |
| Wikidata-style ranks/qualifiers UI | Store fields if cheap; the editorial workflow is a second product. |
| Public dumps with mirrors/torrents | Wikimedia-scale distribution; a signed nightly export is enough until demand exists. |
| Agent auto-publication for any risk class | Policy lab shows escapes at current correlation; promotion must follow measured catch rates. |
| Formal artifact badging/external reproducibility audit | High cost, small audience at launch; an internal replay test buys most of the value. |
| Multi-language editions | Each language multiplies review load; one language with a translation-ready schema is defensible. |
| Maps/charts at scale | Expensive to maintain; only build when a topic has structured data and a maintainer. |
| Personalized explanations | Presentation-only until the view contract and review capacity are proven. |

---

## 9. What "strong launch" means

A strong launch is not a large corpus. Use four primary metrics, each with a definition and a sample size:

| # | Metric | Definition | Target |
|---|---|---|---|
| 1 | External citation durability | Distinct citations to a specific revision/claim permalink from an uninvolved party, still resolving after 30 days | ≥3 at public beta; ≥10 at Stage 3 |
| 2 | Correction latency | p90 acknowledgment → substantive resolution, by severity | Acknowledge ≤2 business days; resolve ≤14 days (E4 calibrates) |
| 3 | Review-hour ratio | Weekly reviewer-hours demanded ÷ available, published | ≤80% for 4 weeks; >100% pauses admission |
| 4 | Reader task success | ≥24 participants on defined tasks vs a named baseline (Wikipedia for overview, an LLM for quick fact) | ≥ baseline +10 points on two tasks |

Supporting indicators (not gates): 5–8 anchor-quality articles in the wedge; 5–10 returning contributors;
correction/review backlog; accessibility audit; restore drill; "would be missed" qualitative survey.
**Do not use** article count, edits/day, tokens, launch-week visitors, time on page, or a self-selected survey
return rate as a gate. The earlier "20% weekly return" and "40% would be missed" numbers were hypotheses, not
measured thresholds.

**Distribution plan (the missing piece).** A return-rate metric needs traffic first. Name two channels and one
partner before public beta:
- **Channel 1:** the wedge's practitioner community (a mailing list, forum, professional association, or
  conference) where a named expert can introduce the reference.
- **Channel 2:** the agent/developer community that needs a citable, machine-readable reference (an API
  directory, a RAG/agent newsletter, or a partner integration).
- **Partner target:** one organization or expert group that will cite, review, or co-maintain 2–3 topics.
- **Referral target:** one university course, newsroom, or standards body that will use a revision in public.
Measure referral source, not just visits. Do not buy traffic.

**Historical calibration, with confounds.** Nupedia approved 24 articles in about three years; Wikipedia produced
about 18,000 in its first year once review friction dropped. Citizendium fell below 100 active members; Knol
found no audience and deleted its corpus; Everipedia forked rather than wrote; Grokipedia launched 800,000
articles and then sat effectively frozen for about five months (R3; secondary for Grokipedia). The direction is
consistent; the magnitudes are not transferable. Wikipedia had a unique era, distribution and no serious
competitor. Do not read its growth curve as a recipe.

**Anti-metrics (do not optimize):** article count, edits per day, tokens generated, unique visitors in launch
week, time on page, proposals per day. These can rise while usefulness falls.

---

## 10. Contribution documentation and feedback

**Required documents before public beta**
- Contributor guide: what to propose, how to cite, what makes a good rationale, how review works, how to appeal.
- Reviewer guide: role checklists, independence, COI, calibration cases, how to write a reason.
- Correction policy: what counts, service levels, privacy, what happens to a rejected correction.
- Source policy: assessment rubric, independence, shared origin, retractions, COI.
- Content policy: scope, neutrality checks, BLP/negative information, company submissions.
- API docs: auth, scopes, idempotency, ETags, errors, rate limits, examples, deprecation.
- Licensing and attribution guide for reusers.
- Changelog and status page; incident history.
- Transparency report template.

**Feedback routes**
- Correction form on every article (primary).
- Reader survey (quarterly) + 5–10 interviews per stage.
- Contributor office hours (monthly) and a public roadmap.
- Decision-log comments during policy comment periods.
- API issue tracker and a partner contact.
- A "what is confusing" link on every page; triage weekly.

**Feedback handling**
- Every correction gets a tracking code and a status.
- Every policy comment gets a response or a published rationale for not adopting it.
- Every incident gets a postmortem with actions and dates.
- Do not let feedback become a second, undocumented backlog; link it to the spec/decision register.

---

## 11. Admission control and review capacity

**Rule:** expected review demand ≤ 80% of measured weekly capacity. If the queue exceeds 2× weekly capacity for
two consecutive weeks, pause new contributor onboarding, publish a status note, and focus on review.

**Capacity model (calibrate in alpha):**

| Risk class | Review minutes (range) | Required roles | Notes |
|---|---|---|---|
| Cosmetic | 1–2 | 1 (any) | Typos, formatting, metadata |
| Low | 3–5 | 1 factual or source | Link repair, non-controversial clarification |
| Standard | 10–20 | factual + source/coverage | New claim, number/date, new section |
| High | 30–60 | factual + source + policy | BLP, medical/legal/financial, company allegations |
| Contentious | 60+ | factual + coverage + policy + community | Active dispute, identity-sensitive |

A solo steward at 10 hours/week can handle roughly 20–30 standard reviews/week, fewer with high-risk work. That
is the real constraint on launch. Do not open a new topic category or language without a named reviewer and a
maintenance plan.

**Quotas (starting ranges; calibrate):** see spec §6.10. Publish the numbers and the current queue state. A
contributor who hits a limit gets an explanation and an appeal path, not a silent failure.

**Review gates search/indexing:** like Wikipedia's New Pages Patrol, a new article may be readable only to
logged-in users or excluded from search until it passes a basic review. This prevents unreviewed content from
acquiring external citations. The tradeoff is slower discovery; measure it.

---

## 12. Timeline and decision points

| When | Milestone | Decision |
|---|---|---|
| Weeks 0–4 | Dogfood; minimum reliable core; restore drill | Go/no-go to alpha |
| Weeks 4–12 | Private alpha; 5–8 topics in the wedge; capacity calibration | Go/no-go to public read |
| Weeks 12–24 | Public beta read + corrections; 20–30 topics; accessibility; search; final name decision before beta branding | Go/no-go to public contribution |
| Months 6–12 | Public contribution; tiered review; appeals/disputes; language pilot | Autonomy decision; governance transition decision |
| After 12 months | Expansion or consolidation | Foundation/charter; commercial API; more languages |

Dates are relative and may slip. The gates are the commitment; the dates are not.

---

## 13. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation | Trigger |
|---|---|---|---|---|
| Review capacity collapses | High | High | Admission control; risk tiers; pause onboarding; measure | Backlog > 2× capacity for 2 weeks |
| Anchor content is not useful | Medium | High | Reader interviews; task tests; narrow domain choice | Task success below baseline |
| Agent spam/coordination | High | Medium | Quotas; clustering; human review; campaign labels | Duplicate/campaign spike |
| Source rot/retractions | High | Medium | Snapshots; retraction checks; stale flags; correction log | A cited source retracts |
| Legal/COI incident | Medium | High | BLP/legal review; right of reply; insurance; takedown | A subject complaint/threat |
| Derived views drift | Medium | High | View contract; staleness; review; manifest | Base change or source retraction |
| Data loss | Low | High | Backups + restore drill; off-host; export manifest | Restore drill fails |
| Security breach | Low | High | Least privilege; audits; rate limits; incident runbook | Anomaly/alert |
| Founder burnout | High | High | Scope control; delegate review; automate routine; publish limits | Missed SLAs for 2 weeks |
| Name/brand confusion | Medium | Low | Naming test; trademark/domain check | Before public beta |
| Licensing mistake | Medium | High | Counsel review; license fields; export manifest | Before public exports |

---

## 14. What Justin must decide (and what can proceed)

| Decision | Needed by | What can proceed without it | Status after the 2026-11-04 answers |
|---|---|---|---|
| Name (D-01) | Before public beta branding | All content/engineering under the working name (Galactica) | Partly answered: working name retained; T5/t5.wiki short-listed; no repository rename; final name still open |
| Licensing (D-30) | Before public exports/API | Internal content; private exports | Accepted subject to counsel: CC BY-SA 4.0 articles + CC0 identifiers/templates; counsel sign-off still required |
| Real vs hypothetical seed subjects (D-36) | Before alpha content | Real subjects in the wedge; hypothetical company/person cases only in `/sandbox` | Partly answered: real subjects, not hypothetical; hypothetical cases stay `/sandbox`; the wedge/anchor-topic list is still open |
| Public beta timing/identity (D-37) | Before public read | Private alpha; readiness work | Partly answered: private alpha with friends/advisors, then a gated public beta; no public beta date |
| Governance transition (D-34) | Before Stage 3 | Steward model; published trigger | Answered: published-transition-trigger approach accepted; foundation deferred and not created now |

These answers are recorded in full in the [decision register](DECISION-REGISTER.md#decision-updates--2026-11-04);
the specific wedge, the final name and the public beta date remain open.

Everything else in this plan can proceed under the proposed defaults, with the decision register recording what
is reversible and when to revisit.
