# E4 — Correction intake and triage cost

**Status: PRE-REGISTERED DRAFT — NOT RUN.**
No corrections have been injected, no triage has been performed, and no timings exist in this
directory. The 30 cases in `cases.csv` are **SYNTHETIC** (fictional, written for this kit); they are
not real reports and do not describe real people or companies. **E4 cannot be completed by an
agent:** it requires a human steward to receive, triage and resolve cases in real time, and (for
reporter satisfaction) real reporters. An agent may prepare cases and run `analysis.py` on data that
humans collected; it may not fabricate timings or dispositions.

**Source:** `docs/EXPERIMENTS.md` §E4 (priority P0; decisions it informs: D-13, D-25).
**Owner:** _unassigned._ **Pre-registration date:** _fill in before injection 1._ **Version:** 0.1.

---

## 1. Question

What does a reader correction actually cost to triage and resolve, and what service level is realistic
for a solo steward?

**Decision.** Whether the public correction channel can launch with a simple form and a published
SLA, or needs structured claim linking, canned responses and/or a volunteer rota first (D-13). The
measured triage cost also calibrates the correction intake budget and the 2-day / 14-day service
levels in `docs/PRODUCT-SPEC.md` §4.4.

**Why it matters.** The spec proposes a 2-day acknowledgment and a 14-day resolution, but there is no
measured basis. A correction SLA that is promised but not staffed is worse than a longer, honest one.
Corrections are the least rate-limited and most promised surface; an anonymous channel can outrun a
solo triager.

---

## 2. Options (exactly as E4 specifies)

| Arm | Intake design | What changes for the steward |
|---|---|---|
| **A** | Email/form + manual triage in the current app | Free-text message; steward finds the article/claim, classifies, replies, edits. Baseline. |
| **B** | Structured form with claim linking and a correction queue | Required fields (article, claim/section, what is wrong, evidence, relationship); queue with states; claim link; canned responses. |
| **C** | B plus a volunteer triage rota | A second person handles a share of the queue; escalation and handover rules; rota creates coordination cost. |

The app currently has **no reader correction path**; this kit does not add one. Arm A is therefore a
manual process around the existing article/evidence pages (a shared inbox plus a spreadsheet is
sufficient to start). B/C are process prototypes; do not build product code for this experiment.

### Design note: what 30 cases can and cannot compare

30 cases over two weeks is enough to estimate **the cost of one intake design with a useful
interval**; it is not enough to compare three designs with power. Pre-registered plan:

1. **Wave 1 (primary): all 30 cases under arm A.** This produces the decision-critical number: the
   median minutes to triage for the current/manual process, compared with the 15-minute threshold.
   Run this even if B is already built.
2. **Wave 2 (optional, only with a fresh case set): arm B.** Do **not** re-inject the identical 30
   cases into the same steward and call it a comparison; the steward has seen them. Draw a new
   30-case set from the same generator and same mix, or stop at a descriptive pilot of 10–15 cases.
3. **Arm C** is evaluated only after B, with the rota actually staffed; a rota that is not staffed
   during the study is not arm C.

If only wave 1 runs, report A's cost against the threshold and explicitly say "no A/B comparison was
run". `analysis.py` groups by `intake_option` and refuses to imply a comparison from a single arm.

---

## 3. The 30-case mix (fixed)

| Category | n | Expected disposition | Severity | What it tests |
|---|---|---|---|---|
| `valid` | 10 | `accepted` | low–medium | Can the steward find the claim, verify the correction, and accept a legitimate fix? |
| `wrong` | 10 | `rejected` | low–medium | Can the steward resist plausible-sounding but unsupported, POV or factually wrong claims? |
| `duplicate` | 5 | `duplicate` | low | Does intake clustering link near-duplicates instead of re-triaging them? |
| `legal_privacy_coi` | 5 | `accepted` (1), `rejected` (1), `needs_info` (3) | high–critical | Does the steward escalate privacy/COI/safety correctly within 24 h? |

**Composition rules (pre-registered):**

- Exactly 10 / 10 / 5 / 5. The analysis script fails if the mix differs.
- `valid` → `accepted`; `wrong` → `rejected`; `duplicate` → `duplicate`. Legal/privacy/COI may be
  `accepted`, `rejected` or `needs_info`; each case has one expected disposition fixed before the run.
- All five legal/privacy/COI cases have severity `high` or `critical`; none is `low`.
- Duplicates are near-duplicates of an **earlier** case (different wording, same target claim). At
  least one duplicate pair is injected on the same day to test clustering at intake, and the rest
  lag by 1–2 business days.
- Cases are spread across the demo article slugs that exist in `core/seeding.py`:
  `subvocal-interfaces`, `quadratic-funding`, `encyclopedia-galactica`. They are demonstration
  drafts; that is acceptable because this experiment measures **triage cost**, not content truth.
- Cases are fixed before injection 1 and are not edited during the run. If a case is found to be
  ambiguous, log it and adjudicate **after** the run; do not quietly rewrite it.

### Case construction rules

- **Fictional only.** No real living person, company or organisation is the subject. Messages are
  written for role-play and must not be sent to anyone outside the study.
- **No PII.** Reporter identities are roles (`reader`, `researcher`, `subject`, `representative`,
  `organization`, `anonymous`), never names or contact details. Placeholders such as "my personal
  contact details" are used instead of actual data.
- **No defamation.** A "wrong" case is wrong about a fact, not an allegation about a person.
- The expected disposition is the **correct editorial outcome under the rubric in §6**, not the
  steward's preference. It is recorded in `cases.csv` before the run.
- All rows are labelled `SYNTHETIC` in the `notes` column. The analysis script counts the labels and
  warns if rows are unlabelled.

---

## 4. Injection schedule (two weeks, 30 cases)

Planned schedule: **Mon 2026-11-09 → Fri 2026-11-20 (10 business days), 3 cases per day**, staggered
through the working day so the steward is not hit with a burst. Legal/privacy/COI cases go early
enough that the 24-hour escalation can be observed. Duplicate pairs lag their original by 1–2
business days; C10 and C25 (same-day pair) test intake clustering.

| Day | Date | Cases (time) |
|---|---|---|
| 1 | Mon 2026-11-09 | C01 09:10, C11 10:40, C26 13:20 (privacy, critical) |
| 2 | Tue 2026-11-10 | C02 09:05, C12 11:15, C21 14:00 (dup of C01) |
| 3 | Wed 2026-11-11 | C03 09:30, C13 10:20, C04 13:45 |
| 4 | Thu 2026-11-12 | C05 09:00, C14 11:30, C22 15:10 (dup of C02) |
| 5 | Fri 2026-11-13 | C06 09:40, C15 13:00, C27 14:30 (COI, high) |
| 6 | Mon 2026-11-16 | C07 09:15, C16 11:45, C28 13:10 (COI, high) |
| 7 | Tue 2026-11-17 | C08 09:25, C17 10:50, C23 14:20 (dup of C05) |
| 8 | Wed 2026-11-18 | C09 09:05, C18 12:00, C29 15:00 (privacy, critical) |
| 9 | Thu 2026-11-19 | C10 09:35, C19 11:20, C24 13:40 (dup of C08) |
| 10 | Fri 2026-11-20 | C20 09:10, C25 10:30 (dup of C10), C30 13:00 (safety, critical) |

**Rules:**

- The `injected_at` column in `cases.csv` is the **planned** time. Record the **actual** send/arrival
  time in the triage log's `received_at`; do not overwrite the planned time. If the schedule slips,
  record the actual time and note it; do not renumber cases.
- Do not add hints, labels or category names to the message the steward sees. The steward sees the
  article slug, the message, and the reporter role only. Expected disposition and category stay in
  `cases.csv`, not in the inbox.
- The steward works normally, including breaks, other duties and a realistic working day. Do not
  batch all triage into one sitting; the queue-age measure is part of the experiment.
- If a case is accidentally seen with its metadata (category/expected disposition), mark it invalid
  in `notes` and exclude it; record why.
- No case is sent to a real external party. Injection is into the study inbox/manual process only.

---

## 5. Disposition rubric

Reader-visible states follow the spec: `received → triaged → accepted / rejected / duplicate /
needs_info`. The triage log records the final disposition.

| Disposition | Definition | Required action |
|---|---|---|
| `accepted` | The report is substantiated and actionable: the article/evidence is wrong, incomplete, ambiguous, or contains private data that should be removed. | Make the change (or queue the proposal), add a public correction note (date, what changed, why, link to revision), close the case. |
| `rejected` | The report is not substantiated, contradicts better evidence, is out of scope, or asks to remove well-sourced criticism/POV. | Reply with the reason and the strongest evidence; close. For COI removal requests, route through policy review. |
| `duplicate` | Substantively the same complaint (same target claim + same underlying issue) as an earlier case, even if worded differently. | Link to the parent case, reply once, close as duplicate. Do not re-triage the underlying issue. |
| `needs_info` | Potentially valid but missing a required element: which claim/section, what it should say, evidence, relationship to the subject, or identity for privacy requests. | Ask specific questions; set a follow-up date; escalate legal/privacy/COI. |

**Escalation (not a disposition):** every `legal_privacy_coi` case is escalated to the policy/legal
reviewer within **24 hours**, regardless of disposition. Privacy redaction (C29) can be `accepted`
and actioned; COI removal requests are not actioned by the triager alone.

**Correctness scoring.** The second reviewer (or the steward after the run) sets `correct_0_1`:

- `1` = disposition exactly matches the pre-registered expected disposition.
- `0` = mismatch. Record the mismatch type in `notes`:
  - **major**: accepted a wrong/duplicate/COI-removal case, or rejected a valid/privacy case;
  - **minor**: `accepted` vs `needs_info`, `rejected` vs `needs_info`, or an otherwise defensible
    alternative that still moves the case forward.

Near-misses are not upgraded to `1`. Report both exact correctness and the major-error count, because
"accepted a plausible wrong claim" is the failure that matters for correction credibility.

---

## 6. Measures (definitions)

All times are computed from the actual timestamps in `triage_log.csv`; `minutes_to_triage` and
`minutes_to_resolve` are derived if blank (the script derives them from timestamps and warns on large
disagreements).

| Measure | Definition | Notes |
|---|---|---|
| **Minutes to triage** | `triaged_at − received_at` | Primary cost measure. `received_at` = first time the steward could see it (inbox arrival); not `injected_at`. |
| **Minutes to resolve** | `resolved_at − received_at` | Resolution = final disposition + reply + (if accepted) change queued/published + public note. |
| **Time to first response** | `first_response_at − received_at` | Human acknowledgment or substantive reply; auto-acknowledgements are not a response (record them in `notes`). |
| **Correctness** | `disposition == expected_disposition` | Exact match, 0/1; major/minor recorded in notes. |
| **False accept rate** | accepted cases whose expected disposition is not `accepted` ÷ all logged cases whose expected disposition is not `accepted` | Accepted a wrong/duplicate/COI-removal case. |
| **False reject rate** | rejected cases whose expected disposition is `accepted` ÷ all logged cases whose expected disposition is `accepted` | Rejected a valid/privacy case. |
| **Intake lag** | `received_at − injected_at` | Measures schedule realism; not the steward's cost. |
| **Queue age** | `received_at → first_response_at`, plus the age of any case still unresolved at the analysis cut-off | Report median, p90, max, and oldest open. |
| **Reporter satisfaction** | Follow-up rating 1–5 from real reporters | **Not collected in the synthetic run.** Do not impute. If the study uses role-play only, record "not collected". |
| **SLA misses** | First response > 2 business days; resolution > 14 calendar days; legal first response > 24 h | Report counts and which cases. Missing the window is itself a reported metric. |
| **Inter-rater agreement** | Cohen's κ on the double-triaged subset | Raw agreement is also reported. |

**Capacity readout:** median triage minutes × expected daily corrections gives the staffing estimate;
report it as an interval (median with bootstrap CI if n ≥ 10), not a single number.

---

## 7. Inter-rater subset

- **10 of 30 cases** are double-triaged: stratified 3 valid, 3 wrong, 2 duplicate, 2 legal/privacy/COI.
  Select them before the run using a fixed seed; do not choose the easy ones afterwards.
- The second reviewer is **blind to the first disposition** and to the expected disposition. They see
  the same message, article slug and role; they record `second_disposition` and
  `second_reviewer_code`.
- They do **not** change the first reviewer's case; the first disposition is the one scored for cost.
- Disagreements are adjudicated by the steward/owner after the run; the adjudicated disposition is
  recorded in `notes`. The pre-adjudication dispositions are retained.
- Report raw agreement and **Cohen's κ** (`analysis.py` computes both). Target κ ≥ 0.6 for the rubric
  to be usable; if κ < 0.4, the disposition categories are being applied inconsistently and the cost
  numbers are not yet decision-grade. Do not hide the disagreement by re-coding.

**Assignment:** the second reviewer must have the same rubric and a 30-minute calibration on 3
practice cases (not in the 30) before the run.

---

## 8. Stopping rule (from E4, operationalised)

The backlog rule: *stop at 30 corrections or when the median triage time is stable. If the 2-day/14-day
SLA is not achievable with one person, publish a longer SLA rather than miss it.*

Pre-registered reading:

- **Stop at 30 cases.** This is the planned n; do not stop early because the median looks good.
- **Stability check:** split the 30 into first 15 / last 15. If the medians differ by ≤ 20% **and**
  the bootstrap 95% CI width for median triage is < 10 minutes, declare the estimate stable. If not,
  report the instability and do not extend the study with the same cases (order effects); a fresh
  wave is a new pre-registration.
- **Safety stop:** if a legal/privacy case is publicly mishandled (data exposed, a reporter
  identified, a 24 h escalation missed), pause the study, fix the process, and restart with a fresh
  case set. Do not pool the affected cases.
- **SLA stop:** if the 2-day acknowledgment or 14-day resolution is missed for a case, log it as a
  miss and continue; a missed SLA is data, not a reason to stop. At the end, if the measured capacity
  cannot meet the promise, recommend a longer published SLA (per E4).
- **Minimum for a decision:** 30 cases and ≥ 10 in the primary arm. Fewer → descriptive only, no
  threshold decision.

---

## 9. Decision thresholds (pre-registered, from E4)

| Threshold | Metric | Action if crossed |
|---|---|---|
| **> 15 minutes per correction (median triage)** | Median `minutes_to_triage` over the primary arm | Add **structured claim linking and canned responses** before public beta (E4's stated action); do not launch with plain email triage. |
| ≤ 15 minutes | Median triage | Simple form + manual triage is defensible for launch; keep measuring. |
| 2-day acknowledgement not achievable | % first responses within 2 business days | Publish a longer acknowledgment SLA rather than miss it. |
| 14-day resolution not achievable | % resolved within 14 calendar days | Publish a longer resolution SLA; do not promise what one person cannot staff. |
| Legal/privacy cases exceed capacity | 24 h escalation misses, time to escalate | Defer real-subject content until a named policy/legal reviewer and capacity exist (E4). |
| False-accept rate high | accepted wrong/duplicate/COI cases | Add a second-reader check for non-obvious dispositions; tighten the rubric before launch. |
| κ < 0.4 | inter-rater agreement | The rubric is not decision-grade; revise it before using the cost numbers. |

The 15-minute threshold is the E4 decision rule: **if triage is > 15 minutes per correction, add
structured claim linking and canned responses before public beta.** The analysis script prints
`E4 THRESHOLD: CROSSED` / `NOT CROSSED` / `UNDETERMINED` (fewer than 10 cases in the arm).

---

## 10. Analysis plan

`analysis.py` implements the descriptive and threshold pieces. Additional analysis is pre-registered
before it is run.

1. **Validate the case file:** exactly 30 rows; 10/10/5/5 mix; category→expected-disposition
   consistency; legal cases high/critical; case IDs unique; slugs known (warn if unknown); all rows
   marked SYNTHETIC (warn otherwise); timestamps parse.
2. **Validate the log:** known case IDs; one row per case per arm; dispositions in the state set;
   timestamps ordered; minutes non-negative; `correct_0_1` consistent with expected vs observed
   (warn if not); reviewer codes look non-identifying; second-reviewer pairs complete.
3. **Cost descriptives:** n, median/mean minutes to triage, to first response, to resolve; p90 and
   max queue age; oldest open case at the cut-off; intake lag. Overall and per intake option.
4. **Correctness:** exact-match count and rate per category; false-accept and false-reject counts and
   rates with denominators; confusion matrix expected × observed.
5. **Threshold:** median triage vs 15.0 minutes; require ≥ 10 logged cases in the arm; print
   CROSSED / NOT CROSSED / UNDETERMINED and the E4 action.
6. **Inter-rater:** pairs count, raw agreement %, Cohen's κ; interpret only with n ≥ 10 pairs.
7. **SLA:** first response ≤ 2 business days, resolution ≤ 14 calendar days, legal first response
   ≤ 24 h; list misses.
8. **Reporting discipline:** report intervals and exact n; no invented satisfaction; label synthetic;
   archive the raw cases/log, the analysis output, and hashes; record the negative result if the
   threshold is not crossed.

---

## 11. Consent, privacy and ethics

- **Synthetic run:** the 30 cases are fictional. Do not send them to real people, and do not attribute
  them to real reporters. The steward is role-playing a reader-support process.
- **Real reporters (later):** if the study is repeated with real reports, the correction form must
  state what is collected, why, how long it is kept, who sees it, and how to request deletion. No
  account is required; a tracking code is enough for follow-up. Do not publish a reporter's identity
  or contact details without consent.
- **Data minimisation:** no PII in `cases.csv` or `triage_log.csv`; reporter roles only; reviewer
  codes only. The analysis script rejects obvious email/phone-like codes.
- **Privacy cases:** treat the content as sensitive even though fictional; do not quote the
  "unpublished notebook" or "minor child" scenarios outside the study debrief.
- **COI:** the steward does not triage a case where they have a relationship with the subject; record
  the recusal and hand it to the second reviewer.
- **Retention:** study data (cases, log, analysis output) retained locally for 12 months, then
  deleted; real-reporter data follows the published privacy policy, not this kit.
- **No deception:** the steward knows this is a timed study; the reporters (if any) know they are
  testing a correction process, not a real dispute.

---

## 12. What result would change the product

| Result | Product action |
|---|---|
| Median triage **> 15 min** | Add **structured claim linking + canned responses** before public beta (E4's threshold). Do not launch plain email triage. |
| Median triage ≤ 15 min, no safety problem | Launch a simple form + manual triage with a **published, measured** SLA; keep measuring. |
| Duplicate rate/material cost high | Add intake clustering/near-duplicate detection before public beta (spec §4.4). |
| False-accept rate high on wrong/COI cases | Add a second-reader check for non-obvious dispositions; tighten the response template. |
| Legal/privacy escalation misses 24 h | Do not open real-subject content; defer until policy/legal capacity exists (D-12). |
| 2-day/14-day SLA not achievable | Publish a **longer** SLA rather than miss the promised one (E4). |
| κ < 0.4 | Rubric not decision-grade; revise and re-test before using the cost numbers. |
| Queue age grows over the two weeks | Intake budget/admission control (D-25) before public launch, not after. |

---

## 13. Threats to validity / what this cannot show

- 30 cases is a small, synthetic convenience sample; the messages are written by the team and may be
  easier to triage than real reports.
- One steward's speed is not a capacity model; a second steward may be faster or slower.
- Role-play has no real reputational or legal pressure; legal/privacy triage in reality is slower.
- Reporter satisfaction cannot be measured in the synthetic run; do not report it as zero or as a
  result.
- The demo articles are demonstration drafts; triage may be easier because the claims are short.
- Timestamps depend on the steward actually working a realistic day; batching invalidates queue-age.

---

## 14. Pre-injection checklist

- [ ] Question, arms, case mix, rubric, measures, thresholds and stopping rule frozen before
      injection 1.
- [ ] `cases.csv` validated by `analysis.py` (30 cases, 10/10/5/5, all SYNTHETIC).
- [ ] Inbox/queue prepared; steward does not see category or expected disposition.
- [ ] Second reviewer trained on 3 practice cases; double-triage subset selected with a fixed seed.
- [ ] `triage_log.csv` header confirmed; reviewer codes prepared (no names).
- [ ] Actual send times will be recorded in `received_at`; planned times stay in `cases.csv`.
- [ ] Result note template created; it must say **not run** until injections actually happen.

## 15. Files

- `PROTOCOL.md` — this pre-registration.
- `cases.csv` — 30 SYNTHETIC cases (10 valid, 10 wrong, 5 duplicate, 5 legal/privacy/COI).
- `triage_log.csv` — empty log template; one row per case per intake arm.
- `analysis.py` — stdlib-only validation, cost statistics, threshold check, `--self-test`.
- `README.md` — exact commands.
