# Experiment backlog

**Version:** 1.0, 2026-11-04.
**Purpose:** turn the open decisions into cheap, pre-registered experiments. Each entry names the competing
options, the cases, the measurements, the cost, the stopping rule, and what decision it would change.
**Rule:** pre-register the question, options, cases, metrics, stopping rule and cost before running. Store the
result with the spec. Do not call a re-execution "reproducible"; record model, seed and prompt hash (spec §8.6).
**Priority:** P0 = needed before private alpha; P1 = before public beta; P2 = later.

| ID | Experiment | Priority | Decision it informs | Effort |
|---|---|---|---|---|
| E1 | Reader task success: summary-first vs article-first | P0 | D-02, D-08, reader spec | 2–3 weeks |
| E2 | Review-at-creation vs post-hoc review | P0 | D-19, D-26 | 2 weeks |
| E3 | Reviewer independence: same-model vs mixed panel | P0 | D-18, D-20 | 3–4 weeks |
| E4 | Correction intake and triage cost | P0 | D-13, D-25 | 1–2 weeks |
| E5 | Derived view staleness and re-review cost | P0 | D-08, view roadmap | 1–2 weeks |
| E6 | API idempotency/retry storm | P1 | D-27, D-28 | 1 week |
| E7 | Source assessment calibration | P1 | D-09, D-10 | 2–3 weeks |
| E8 | Search recall on a query set | P1 | D-29 | 1 week |
| E9 | Coordinated campaign simulation | P1 | D-24, D-25 | 2 weeks |
| E10 | Quota calibration from review time | P1 | D-25, D-26 | 2–3 weeks |
| E11 | Translation/reading-level pilot | P2 | D-04, D-39 | 4–6 weeks |
| E12 | Naming test (Galactica vs T5/t5.wiki) | P1 (before public beta) | D-01 | 2 weeks |
| E13 | Backup/restore drill and incident tabletop | P0 | D-32 | 1 week |
| E14 | Accessibility and mobile audit | P1 | reader spec | 2 weeks |
| E15 | Autonomous publication shadow mode | P2 (after E3/E2) | D-20 | 4–6 weeks |

---

## E1 — Reader task success: summary-first vs article-first

**Question:** Does a self-contained summary/at-a-glance surface, with the full article one click away, improve
task success over a single long article for overview and quick-fact readers?

**Why it matters:** the reader research shows shallow needs dominate (overview 39–47%, quick fact 25–38%) and
citations are rarely clicked (0.29% of page views). The spec proposes a summary surface; this is the test.

**Options**
- A: current article page (lead + body + evidence drawer).
- B: summary surface first (lead + at-a-glance + "read more" + "where this comes from"), full article second.
- C: summary surface plus a visible "evidence" strip that does not require opening the drawer.

**Cases:** 6 topics from the seed corpus (2 ordinary, 2 contested, 2 structured), 5–8 target readers per
condition, counterbalanced. Tasks: "explain this in one minute", "find the 2018 figure", "find who disputes
this", "cite this claim".

**Measurements:** task success (rubric), time to answer, confidence calibration (self-reported vs correct),
evidence-open rate, "would you trust this to cite?"; qualitative think-aloud. Report intervals, not just means.

**Cost:** 2–3 weeks; 30–48 sessions; no model cost. Recruitment is the bottleneck.

**Stopping rule:** stop after 30 sessions if one condition is clearly better on the primary task and no
condition has a safety problem. If no difference, keep the simpler page (A) and revisit after 100 readers.

**Would change:** if B/C is not better, drop the summary surface from launch and keep the lead + evidence drawer.
If C improves evidence use without hurting clarity, keep the strip.

---

## E2 — Review-at-creation vs post-hoc review

**Question:** Does reviewing proposals at creation (before publication) catch more defects per reviewer-minute
than reviewing after publication (audit + correction)?

**Why it matters:** hoax data shows 90% of ever-detected hoaxes are flagged within an hour; late review catches
little new and content legitimizes itself. But review-at-creation is the capacity bottleneck. The spec claims
"review at creation" as the launch gate policy; this tests the claim in our workflow.

**Options**
- A: review before publish (current human gate), all risk classes.
- B: publish cosmetic/low immediately, audit a sample; review standard/high before publish.
- C: publish everything, audit a risk-weighted sample, rely on correction.

**Cases:** 40 seeded proposals with planted defects (unsupported claim, overgeneralization, dropped
qualification, number change, citation laundering, dead link, framing omission), balanced across risk classes.
Reviewers see the proposal, base, evidence; they do not know the condition.

**Measurements:** defect escape rate, false-object rate, reviewer minutes per proposal, time-to-detect for
post-hoc, correction rate, reviewer fatigue (self-report). Compare per reviewer-minute, not just per proposal.

**Cost:** 2 weeks; 2–3 reviewers; ~20 hours of review; no model cost if human; model cost if agent reviewers.

**Stopping rule:** stop at 40 proposals or when the confidence interval on escape rate is ±10 points. If A and B
are within 5 points on escape but B halves reviewer minutes, B is a candidate for low-risk only.

**Would change:** if B's escape rate for low-risk is acceptable (<2%) and reviewer minutes fall, propose a
tiered policy (still not auto-publication). If A is clearly better, keep the human gate and reduce scope.

---

## E3 — Reviewer independence: same-model vs mixed panel

**Question:** How much does reviewer independence (different model/provider, different evidence packet) reduce
defect escape compared with three roles on one model?

**Why it matters:** the policy lab's one-model panel (correlation 0.85) escapes 44.2% of standard defects;
mixed panel (0.30) escapes 22.3%. Those are assumptions. The spec proposes cross-model review and recorded
correlation; this measures it.

**Options**
- A: three roles, one model, shared evidence packet (current).
- B: three roles, three models/providers, shared evidence packet.
- C: three roles, three models/providers, independently assembled evidence packets (different source excerpts).

**Cases:** 60 proposals with planted defects, balanced across risk classes and defect types; 3 models available
in the local catalog; same prompts per role; randomize order. Human adjudication of each verdict.

**Measurements:** catch rate per defect type, false-object rate, correlation of verdicts (pairwise agreement,
Krippendorff's alpha), reviewer minutes, cost per proposal. Compare A/B/C per defect type, not just aggregate.

**Cost:** 3–4 weeks; model calls (free/local models preferred); human adjudication ~20 hours.

**Stopping rule:** stop at 60 proposals or when the catch-rate interval is ±10 points. If B/C does not improve
catch rate by ≥10 points over A, the independence hypothesis is not supported in our setting; record it.

**Would change:** if B/C improves catch rate, make cross-model review the default for standard/high and record
provider in every review. If not, the policy lab's assumption is wrong and autonomy is even less justified.

---

## E4 — Correction intake and triage cost

**Question:** What does a reader correction actually cost to triage and resolve, and what service level is
realistic for a solo steward?

**Why it matters:** the spec proposes 2-day acknowledgment and 14-day resolution. There is no measured basis.

**Options**
- A: email/form + manual triage in the current app.
- B: structured form with claim linking and a correction queue.
- C: B plus a volunteer triage rota.

**Cases:** 30 realistic corrections (10 valid, 10 wrong, 5 duplicate, 5 legal/privacy/COI), injected over 2
weeks; a second reviewer handles a subset for inter-rater agreement.

**Measurements:** minutes to triage, minutes to resolve, time-to-first-response, correctness of disposition,
false-accept/false-reject rate, reporter satisfaction. Track queue age.

**Cost:** 1–2 weeks; 20–30 hours; no model cost.

**Stopping rule:** stop at 30 corrections or when the median triage time is stable. If the 2-day/14-day SLA is
not achievable with one person, publish a longer SLA rather than miss it.

**Would change:** if triage is >15 minutes per correction, add structured claim linking and canned responses
before public beta; if legal/privacy cases exceed capacity, defer real-subject content.

---

## E5 — Derived view staleness and re-review cost

**Question:** How often do views go stale, and how long does it take to re-review and republish them?

**Why it matters:** the view contract is the highest-consequence addition, and maintenance is the binding
constraint. The spec proposes summary/timeline/table now; this tests the cost.

**Options**
- A: a view is a block in the article (current).
- B: a view is a separate object with a manifest, reviewed, stale flag.
- C: B plus auto-generated draft on base change (human reviews).

**Cases:** 2 anchor topics; one timeline, one table, one summary each; 10 base revisions over 3 weeks; a
source retraction in one case.

**Measurements:** time to create, time to review, time to re-review after a base change, stale-view count,
reader use of the view, citation resolution. Track whether the view introduced a new fact (it should not).

**Cost:** 1–2 weeks; 10–20 hours; no model cost if human-authored.

**Stopping rule:** stop after 10 base changes or when the re-review time is stable. If re-review is >2× the
original review, the view is not worth it at launch.

**Would change:** if B/C is affordable, ship summary/timeline/table; if not, ship only the summary and defer
timelines/tables until the data is structured. Add per-event/per-row source fields if the timeline case shows
the view-level `as_of` is insufficient.

---

## E6 — API idempotency and retry storm

**Question:** Do `Idempotency-Key` + `If-Match` prevent duplicate proposals/reviews under realistic retries, and
what is the cost?

**Why it matters:** the current API has no idempotency, ETag or rate limit; agents retry. The spec proposes a
contract; this tests it.

**Options**
- A: current API (no key, no ETag).
- B: `Idempotency-Key` + `If-Match` + `409/412/422` contract.
- C: B plus client-side SDK/retry helper.

**Cases:** a simulated agent that submits 100 proposals with 10% timeouts, 5% duplicate retries, 2% stale bases;
a second agent that retries a review; a burst of 50 parallel requests.

**Measurements:** duplicate proposals created, lost updates, 409/412/422 correctness, retry success rate,
latency, server errors, operator time to reconcile. Include a "kill the worker mid-request" case.

**Cost:** 1 week; no model cost; test harness.

**Stopping rule:** stop at 100 requests or when duplicate rate is stable. If B does not reduce duplicates to
near zero, the contract is wrong or the client is not using it.

**Would change:** if B works, make it the API default and document the error contract; if not, keep writes
human-only until the contract is fixed.

---

## E7 — Source assessment calibration

**Question:** Do reviewers agree on source quality/independence ratings, and does a rubric improve agreement
over unaided judgment?

**Why it matters:** the spec proposes per-use source assessment with dimensions; independence is not
even-handedness; COI is orthogonal to bias. If reviewers cannot agree, the rating is not useful.

**Options**
- A: unaided judgment ("is this source reliable?").
- B: the 7-dimension rubric with reasons.
- C: B plus a shared-origin/DOI graph and funding disclosure.

**Cases:** 30 sources across 5 topics, including a press release, a company site, a peer-reviewed paper, a
government statistic, a retracted paper, two syndicated copies, and a source with a disclosed funder.

**Measurements:** inter-rater agreement (alpha), agreement with a human expert panel, time per assessment,
false-strong/false-weak rate, appeal rate. Track whether the shared-origin signal changes ratings.

**Cost:** 2–3 weeks; 20–30 hours; no model cost if human; Crossref API free.

**Stopping rule:** stop at 30 sources or when alpha is stable. If alpha <0.5, the rubric is not ready for
automated use; keep it advisory and require reasons.

**Would change:** if B/C improves agreement, use the rubric in review; if not, reduce to a simpler
"independent/not independent/unknown" field and rely on reviewer reasons.

---

## E8 — Search recall on a query set

**Question:** Does SQLite FTS5 over titles, openings, headings and claims meet a recall@3 target for realistic
queries?

**Why it matters:** the current library search is title/opening `icontains`; the spec proposes FTS5 first.
Search is the primary read path.

**Options**
- A: current `icontains`.
- B: FTS5 with BM25 and filters.
- C: B plus embeddings/hybrid.

**Cases:** 50 queries from 3 reader personas (quick fact, overview, verify), including 10 zero-result queries,
5 misspellings, 5 multi-word concepts, 5 non-English terms. Expected topics labeled by 2 humans.

**Measurements:** recall@3, MRR, zero-result rate, latency, index size, rebuild time. Track query type.

**Cost:** 1 week; no model cost for A/B; embedding cost for C.

**Stopping rule:** stop at 50 queries or when recall@3 is stable. If B <80% recall@3, add C or improve metadata
before public beta.

**Would change:** if B meets the target, ship it and defer C; if not, prioritize synonyms/redirects before
embeddings.

---

## E9 — Coordinated campaign simulation

**Question:** Can the proposed signals (operator, source overlap, timing, text similarity) distinguish a
coordinated campaign from legitimate advocacy/translation work at an acceptable false-positive rate?

**Why it matters:** sybil defence is review-capacity protection, not identity verification; CheckUser is weak
by its own account; a campaign can target the review pipeline.

**Options**
- A: rate limits only.
- B: clustering + human review + campaign label.
- C: B plus sampled re-review of reviews and reviewer weighting.

**Cases:** 3 simulated campaigns (20 accounts each: sockpuppet, PR firm, advocacy) and 2 legitimate groups
(translation team, classroom) submitting 20 proposals each; a human reviewer labels each cluster.

**Measurements:** detection rate, false-positive rate, reviewer time, proposals merged, reviewer-pipeline
attack success (a sock reviewing a sock), appeal rate. Include a "reviewer collusion" variant.

**Cost:** 2 weeks; test harness; no model cost if scripted.

**Stopping rule:** stop after 5 groups or when detection/false-positive is stable. If false positives >20%,
remove the automatic label and keep human-only triage.

**Would change:** if C detects the review-pipeline attack, add sampled re-review to the review model; if not,
the spec's sybil section is too optimistic and should say so.

---

## E10 — Quota calibration from review time

**Question:** What proposal quotas keep expected review demand at ≤80% of measured capacity?

**Why it matters:** the spec's quota ranges are guesses; review capacity is the binding constraint.

**Options**
- A: flat quota per account (5/day).
- B: trust-tier quotas (new/established/trusted).
- C: B plus risk-weighted quotas and a capacity dashboard.

**Cases:** 4 weeks of simulated proposals at 10/25/50/100 per day, with the measured review-time distribution
from E2/E3. One human reviewer with a fixed weekly budget.

**Measurements:** queue depth, median time-to-review, oldest unreviewed age, reviewer utilization, proposals
abandoned, contributor retention (simulated). Compare demand vs capacity.

**Cost:** 2–3 weeks; simulation + 1 human; no model cost.

**Stopping rule:** stop at 4 weeks or when the queue trend is clear. If C keeps the queue <1 week at 25/day,
set the quota accordingly; if not, lower admission.

**Would change:** the initial quota table and the admission-control threshold. Publish the measured numbers.

---

## E11 — Translation/reading-level pilot

**Question:** Does a view-over-one-claim-base translation/reading-level variant preserve meaning and uncertainty
at acceptable review cost?

**Why it matters:** Simple English is a fork with drift; Content Translation gates on modification ratio. The
spec proposes views, not forks.

**Options**
- A: separate article (fork).
- B: view of a source revision with a human reviewer and modification ratio.
- C: B plus a bilingual reviewer and a back-translation check.

**Cases:** 3 lead-sized articles (200–500 words) translated/simplified into one target language; 2 reviewers per
variant; a meaning-preservation rubric (claims, qualifications, numbers, uncertainty).

**Measurements:** claim preservation, qualification preservation, reviewer minutes, modification ratio, reader
comprehension (small test), drift after a source revision change.

**Cost:** 4–6 weeks; bilingual reviewers; no model cost if human.

**Stopping rule:** stop at 3 articles or when the preservation rate is stable. If B loses >10% of qualifications,
the view approach needs a stronger review or should be deferred.

**Would change:** whether to launch a language pilot at all; the translation review checklist.

---

## E12 — Naming test (Galactica vs T5/t5.wiki)

**Question:** Which name is more distinctive, credible and memorable for the target audience, and what risks
does each carry?

**Why it matters:** "T5" collides with a well-known model name; "Truth Attractor" overclaims a verifiability
model. The name is a D-01 decision.

**Options:** Galactica; T5; t5.wiki; "Truth Attractor"; a neutral placeholder.

**Cases:** 20 target readers/contributors (not the project team), 5 questions: what do you think this is? what
would you expect? does it sound credible? would you cite it? what does the name remind you of? Plus a search
collision check and a trademark/domain check (not legal advice).

**Measurements:** correct category guess, confusion with T5 model, credibility rating, recall, spelling,
qualitative associations.

**Cost:** 2 weeks; recruiting; no model cost.

**Stopping rule:** stop at 20 interviews or when the association pattern is clear. Do not run a public poll;
small qualitative is enough for a name decision.

**Would change:** D-01 recommendation. The name decision remains Justin's.

---

## E13 — Backup/restore drill and incident tabletop

**Question:** Can the project restore from backup within an acceptable RPO/RTO, and does the incident runbook
work under a simulated content incident?

**Why it matters:** GitLab's 2017 postmortem had five recovery mechanisms and all five failed; the control is a
drill, not a tool. The spec claims backups are a launch requirement.

**Cases:** (a) restore the current SQLite DB from the nightly backup into a fresh environment, boot the app,
verify row counts and a content hash; (b) tabletop a privacy violation: emergency unpublish, incident note,
post-mortem, second-person review; (c) tabletop a source-retraction correction.

**Measurements:** restore time, data loss window, row-count/hash match, number of runbook gaps, time to
emergency-unpublish, time to public note.

**Cost:** 1 week; no model cost.

**Stopping rule:** one drill; fix P0 gaps and repeat within 30 days. If restore fails, block public beta.

**Would change:** RPO/RTO claims, runbook, on-call expectations. No public launch without a passing drill.

---

## E14 — Accessibility and mobile audit

**Question:** Do the core flows meet WCAG 2.2 AA on mobile and with a screen reader?

**Why it matters:** 63–65% of readers are on mobile; accessibility is a launch criterion. The evidence drawer
and tables are the risk areas (2.4.11 focus not obscured, 2.5.8 target size, 1.4.10 reflow).

**Options:** current UI; fixed UI after audit; fixed UI plus a text/table fallback for every view.

**Cases:** article, evidence drawer, history, correction form, table, timeline; iOS/Android small screen;
keyboard-only; one screen reader (NVDA or VoiceOver); 200% zoom; slow connection.

**Measurements:** WCAG 2.2 AA pass/fail per criterion, task completion with screen reader, number of blockers,
time to fix.

**Cost:** 2 weeks; no model cost; manual testing.

**Stopping rule:** stop after the core flows; fix P0/P1 and re-test. No public beta with open P0 accessibility
issues.

**Would change:** the launch readiness table; the evidence drawer design; the view fallback requirement.

---

## E15 — Autonomous publication shadow mode

**Question:** If the system had auto-published cosmetic/low edits under a proposed policy, how many defective
edits would have escaped, and how does that compare with human decisions?

**Why it matters:** no autonomy at launch; the policy lab is simulated. This is the only path to a defensible
tiered policy.

**Options**
- A: human-all (baseline).
- B: shadow `auto_publish` for cosmetic only, 10% audit.
- C: shadow `auto_publish` for cosmetic/low, 20% audit, with a kill switch.

**Cases:** 500 real proposals from alpha/beta, with human decisions as labels; planted defects for a subset;
reviewer panel from E3.

**Measurements:** false-approval rate (published defective / auto-published), escape rate, human audit load,
agreement with human decisions, reviewer disagreement. Report confidence intervals; pre-register the threshold
(e.g., false-approval ≤1% over ≥500 edits).

**Cost:** 4–6 weeks; depends on volume; model + human audit cost.

**Stopping rule:** stop at 500 edits or when the interval is tight enough to decide. If the false-approval rate
is above the threshold, reject autonomy and document it; do not keep tuning until it passes.

**Would change:** D-20. Autonomy is a policy version with a kill switch; it is never a code default.

---

## Experiment hygiene

- **Pre-register** in a file next to the spec: question, options, cases, metrics, stopping rule, cost, owner,
  date.
- **Preserve raw outputs** (model outputs, reviewer verdicts, human labels) with hashes.
- **Label** simulated vs human vs model results.
- **Report intervals**, not point estimates, for small samples.
- **Record negative results**; they are as useful as positive ones.
- **Do not run experiments on real people/companies** without consent/legal review; use hypothetical cases.
- **One substantive critique-and-revision pass** per experiment report; avoid circular review.

---

## What would change the spec most

1. **E1** (reader task success) could remove the summary surface or change the article anatomy.
2. **E2** (review at creation) could force a different publication policy and admission model.
3. **E3** (reviewer independence) could either justify cross-model review or undermine the independence thesis.
4. **E5** (view staleness) could reduce the view roadmap to summary only.
5. **E13/E14** (ops/accessibility) are launch blockers, not research.
