# E1 — Reader task success: summary-first vs article-first

**Status: PRE-REGISTERED DRAFT — NOT RUN.**
No sessions have been conducted. No participant data exists in this directory. This kit contains a
protocol, an empty data template, and an analysis script. **E1 cannot be completed by an agent:** it
requires human readers, recruitment, consent and observed sessions. An agent may prepare materials and
run `analysis.py` on data that humans collected; it may not invent sessions or results.

**Source:** `docs/EXPERIMENTS.md` §E1 (priority P0; decision it informs: D-02, D-08, reader spec).
**Owner:** _unassigned_. **Pre-registration date:** _fill in before the first session_. **Version:** 0.1.

---

## 1. Question

Does a self-contained summary/at-a-glance surface, with the full article one click away, improve task
success over a single long article for overview and quick-fact readers?

**Primary decision.** Whether the reader surface proposed in `docs/PRODUCT-SPEC.md` §4.1 (summary /
quick-fact state) ships at all, and in what form. E1 informs D-02 (article-first product center) and
D-08 (view/derived-content contract) and the reader spec.

**Why it matters (from the backlog).** Shallow reader needs dominate (overview 39–47%, quick fact
25–38%) and citations are rarely clicked (0.29% of page views). The spec proposes a summary surface;
this is the test. A null or harmful result removes a surface from launch rather than adding one.

---

## 2. Conditions (exactly as E1 specifies)

| Arm | Condition | What the participant sees |
|---|---|---|
| **A** | Current article page | Lead + body + evidence drawer. Evidence is one interaction away. No summary surface. |
| **B** | Summary surface first | Lead + at-a-glance + "read more" + "where this comes from". The full article is one click away. |
| **C** | Summary surface plus visible evidence strip | B plus a visible "evidence" strip that shows source/claim status **without** opening the drawer. |

The only differences between arms are the reader surface elements named above. Typography, content
revision, instrumentation, task wording, room and device are held constant. C's strip must not add new
facts not present in the article revision; it exposes existing claim/source status. Do not ship a
different article revision to different arms: all arms read the **same revision** (`revision_id`
recorded per session).

---

## 3. Design and allocation

- **Unit:** one session = one participant × one arm × one topic × all four tasks (randomised order).
- **Primary design:** between-subject at session level (no participant sees two arms, so no carry-over).
- **Target:** **18–24 sessions** (minimum 18, target 24), **5–8 sessions per arm**. The backlog says
  5–8 target readers per condition; treat 6–8 per arm as the planning target. If the interval is
  still too wide after 24, extend to the E1 stop point of **30 sessions** (9–10 per arm) and record
  that as a deviation from the 5–8 planning range. Do not go beyond 30 without a new
  pre-registration. (The backlog's "5–8 per condition" and "stop after 30 sessions" imply different
  arm sizes; this protocol resolves the conflict explicitly rather than silently.)
- **Full topic × arm crossing:** 6 topics × 3 arms = 18 sessions. At 18 sessions every topic appears
  in every arm exactly once; at 24, four cells are repeated. This is the counterbalancing that matters
  most: **topic is not confounded with arm**.
- **Repeated sessions:** a participant may do more than one session only **in the same arm** and
  on a different topic; record a linkable but non-identifying `participant_code` (e.g. `P07`) so
  repeat sessions can be checked. Do not reuse a participant across the same topic, and do not let
  a participant see two arms (between-subject).
- **Randomisation:** arm assignment is fixed by the crossing plan, not chosen per participant. Within a
  cell, session order is randomised. Task order is randomised with a balanced 4×4 Latin square.
- **Sample-size honesty:** 6–8 per arm detects only large differences. Plan for intervals, not
  significance (see §12).

### Counterbalancing

1. **Topic ↔ arm:** a 6×3 assignment table in which each topic appears once per arm. Two waves:
   wave 1 uses rotation R1; wave 2 (sessions 19–24) uses rotation R2, shifting each topic to the next
   arm. This prevents "topic difficulty" from loading on one arm.
2. **Task order:** four tasks in a balanced Latin square (4 orders, each order used equally within each
   arm). No task depends on another; task order is recorded.
3. **Within-block order:** the order of the at-a-glance items and the evidence strip is fixed by the
   revision, not varied, so variation cannot leak into the comparison.
4. **Session time of day / device:** record device, viewport, and time; balance across arms where
   possible. Do not switch a participant mid-session.
5. **Facilitator:** rotate facilitators across arms if more than one; the facilitator reads the same
   script.

---

## 4. Topic selection (6 slots: 2 ordinary, 2 contested, 2 structured)

### Global inclusion criteria (all slots)

- Exists in the app as a published revision with a working evidence drawer and a recorded
  `revision_id`; readable on the study device and viewport.
- **No real living-person or real-company subject allegation.** D-12 remains in force: no real-subject
  content until a named policy/legal reviewer and counsel exist. Fictional/demo and historical topics
  only.
- Not under an active legal/privacy complaint; no confidential material.
- Stable during the study window: no publication or revert of the studied revision while sessions run
  (freeze the revision; record its hash).
- Article length allows all four tasks within 15 minutes per session.
- At least one pre-registered "cite this claim" target with a source and one pre-registered dated
  figure (for the "find the 2018 figure" task).

### The six slots and their criteria

| Slot | Stratum | Selection criterion (what the topic must contain) | Assignment status |
|---|---|---|---|
| T1 | Ordinary | Mature, uncontested in reliable sources; no open dispute; lead + body + evidence stable; reader job is overview/quick fact. | **Open** — pick from the chosen 5–8 anchor topics. |
| T2 | Ordinary | Same as T1, different domain and different article shape (e.g. one with a table, one without), so "ordinary" is not one layout. | **Open** |
| T3 | Contested | At least two documented positions in reliable sources, summarised as adjudication (not a raw thread); article has a disputes/uncertainty panel; the disagreement can be described without defaming a person. | **Open** — candidate: `subvocal-interfaces` (2018/2019 publication record) but it is a demonstration draft; pilot only. |
| T4 | Contested | A different *kind* of contest (e.g. empirical disagreement vs interpretive/priority dispute); positions have named evidence, not just opinion. | **Open** — candidate: `quadratic-funding` (wealth/collusion objections), demonstration draft; pilot only. |
| T5 | Structured | Core content includes a table with ≥3 rows and per-row sources; dated figures with "as of" semantics; supports "find the 2018 figure". | **Open** — candidate: `quadratic-funding` (comparison table), demonstration draft; pilot only. |
| T6 | Structured | Core content includes a timeline with ≥5 dated events and per-event sources; dates are structured claims, not prose-only. | **Open** — candidate: `encyclopedia-galactica` (timeline), demonstration draft; pilot only. |

### Corpus reality (important honesty note)

The app currently seeds **three demonstration articles** (`subvocal-interfaces`, `quadratic-funding`,
`encyclopedia-galactica`). They are explicitly demonstration drafts, not reference-quality articles,
and they overlap the contested/structured strata. **They are suitable for piloting the instrumentation
and the task script, not for the E1 decision run.** Fill all six slots from the 5–8 anchor topics once
they are chosen (D-36/open wedge). Do not present a demo draft to a participant as a verified reference
article. Record the final topic list and revision IDs in the table below before session 1.

| Slot | Slug | Revision ID | Maturity | Why it fits | Frozen hash |
|---|---|---|---|---|---|
| T1 | | | | | |
| T2 | | | | | |
| T3 | | | | | |
| T4 | | | | | |
| T5 | | | | | |
| T6 | | | | | |

**Exclusions:** opinion pieces; topics whose only interest is the demo's planted defect; topics a
participant has edited; topics the participant wrote; topics with an unresolved factual challenge that
would make the task unanswerable.

---

## 5. Tasks (four, identical wording across arms)

Task IDs are the values used in `sessions.csv.task`. The backlog's task names map to them as
follows: "explain this in one minute" (`explain_1min`), "find the 2018 figure"
(`find_2018_figure`), "find who disputes this" (`find_disputes`), "cite this claim"
(`cite_claim`).

| Task ID | Script (read verbatim) | What the facilitator records |
|---|---|---|
| `explain_1min` | "Explain this topic to me in one minute, as if I were a colleague who has not read it." | 60-second answer (audio recorded only with consent, else live notes); success rubric; whether the participant used the summary/at-a-glance. |
| `find_2018_figure` | "Find the 2018 figure in this article and tell me what it is and where you found it." | The pre-registered target value/date per topic; the answer; location; seconds to answer. If the topic has no 2018 datum, substitute the pre-registered dated figure and record the substitution in `notes`. |
| `find_disputes` | "Is anything in this article disputed? If so, who disputes it, and what do they say?" | Whether the article is disputed; the position(s); where the participant found them; seconds. |
| `cite_claim` | "Give me a citation for this claim that I could put in a report: title, revision, access date, and license." | The pre-registered claim; which four elements were produced; whether any element was invented. |

**Procedure per task:** facilitator reads the script, starts the timer, does not help for 15 seconds,
may repeat the script once, and stops at **180 seconds**. Hints are recorded and cap the score at 1.
No task feedback is given until the end of the session. The participant may navigate anywhere in the
product; external search is allowed unless the pre-registration says otherwise (default: **no external
search**; record violations). If the participant asks "which surface should I use?", the answer is
"whatever you would normally use".

**Session length:** 45–60 minutes including consent, four tasks, confidence ratings, debrief.

---

## 6. Success rubric (0–2)

Global anchors, applied per task by a coder blind to arm:

- **0 — incorrect / absent / fabricated.** The answer is wrong, missing, or contains a fact, figure or
  citation not supported by the revision. *Any fabricated citation or number is scored 0 and recorded
  as a safety event.*
- **1 — partial.** Correct gist or correct value but a required element is missing, the location is
  wrong, the answer needed a hint, or a secondary detail is wrong.
- **2 — correct and complete** per the task-specific checklist below, with no fabricated detail.

Task-specific checklists:

| Task | Score 2 requires |
|---|---|
| `explain_1min` | Correct definition + at least one of significance/limits/uncertainty + no factual error or fabrication. |
| `find_2018_figure` | Correct pre-registered value/date **and** a correct location (section/claim/source) within 180 s. |
| `find_disputes` | Correctly states whether the article is disputed; if disputed, names at least one position and where it is shown. If undisputed, states that and does not invent a dispute. |
| `cite_claim` | All four elements (article title, revision, access date, license) and the correct claim; no invented element. |

**Coding.** Two coders independently score a stratified 20% sample (at least 8 sessions), blind to arm
(transcripts stripped of page/arm cues). Report Cohen's κ. Target κ ≥ 0.7; if κ < 0.6, revise the
codebook and re-code before analysis. Disagreements are adjudicated by the owner; the adjudicated score
is used, and the pre-adjudication scores are retained. The `correct` column in the CSV is the binary
accuracy used for calibration: `1` if the adjudicated rubric score is **2**, else `0`.

---

## 7. Measures

### Primary

- **Task success score**, mean of the four task rubric scores (0–2) per session, compared **B − A**.
  Positive values favour the summary-first surface. This is the only pre-registered primary contrast.
- **Full-success rate** (proportion of task attempts scored 2) is the key secondary representation of
  the same outcome; report it with intervals, not as a substitute for the primary estimand.

### Secondary

- Time to answer per task (seconds; median and mean; cap at 180 s).
- Evidence-open rate (§9).
- Confidence calibration (§8).
- "Would you trust this to cite?" 0–4 after each task (the CSV `would_cite_0_4`).
- Task-level success (4 tasks × 3 arms), topic-level descriptives.
- Qualitative think-aloud themes (clarity, finding the evidence, uncertainty, trust).
- Safety events: fabricated citation accepted by the participant, privacy exposure, misleading claim.
- Completion/abandonment, device and viewport.

**Do not** report only means; every estimate gets an interval or an explicit "too few observations".

---

## 8. Confidence calibration

After each task, before any feedback, the participant answers one item:

> "How confident are you that your answer is correct?" (0 = not at all, 100 = completely)

- **Accuracy** = mean of `correct` (0/1) for that cell.
- **Mean confidence** = mean of `confidence_0_100` divided by 100.
- **Calibration** = mean confidence − accuracy, in percentage points. Positive = overconfident;
  negative = underconfident.
- Report **mean confidence and accuracy separately** as well as the difference; the difference alone is
  uninterpretable.
- Report per arm and per task; do not interpret cells with fewer than 10 task attempts.
- Calibration is a **secondary** measure. It cannot by itself reject a surface, but a surface that
  raises confidence without raising accuracy is a trust risk and blocks shipping until fixed.

`analysis.py` implements exactly this difference per arm (and overall). It does not compute Brier
scores; add them only if pre-registered before the run.

---

## 9. Evidence-open instrumentation

Goal: measure whether the surface changes evidence use, without changing the layout.

**Events (append-only, one row per event; exported per session):**

| Event | When | Fields |
|---|---|---|
| `session_start` | Consent complete | `session_id`, `arm`, `topic`, `revision_id`, `device`, `viewport`, timestamp |
| `task_start` / `task_end` | Task boundary | `session_id`, `task`, timestamp |
| `claim_open` | Claim marker/affordance activated | `session_id`, `task`, `claim_id`, timestamp |
| `drawer_open` / `drawer_close` | Evidence drawer | `session_id`, `task`, `claim_id`, timestamp |
| `source_link_click` | Outbound source link | `session_id`, `task`, `source_id`, timestamp |
| `strip_exposure` | C only: strip in viewport ≥1 s | `session_id`, `task`, timestamp |

**Definition used in `sessions.csv`:** `evidence_opened = 1` if, during that task window, the
participant triggered any of `claim_open`, `drawer_open`, `source_link_click`, or (C only) actively
expanded the evidence strip. Passive `strip_exposure` is recorded separately and **does not** count as
opening. Record `0` otherwise. Task windows come from `task_start`/`task_end`, not wall-clock guesses.

**Rules:**

- Instrumentation is identical across arms except the affordances themselves. The C strip must not
  auto-open the drawer.
- No IP address, user agent, cookie ID, or account identifier in the event log. Use the random
  `session_id`; delete the mapping to any contact list before analysis.
- Log locally; export CSV/JSONL with the session data; hash the export.
- Pilot with 2 non-participants before session 1. If logging fails or is incomplete for a session,
  mark the session invalid (`notes`), exclude it, and record why. Do not reconstruct missing events.
- Verify the "find the 2018 figure" task is answerable without opening evidence; if the only path is
  the drawer, the instrumentation is measuring navigation, not evidence use.

---

## 10. Stopping rule (from E1, operationalised)

The backlog rule: *stop after 30 sessions if one condition is clearly better on the primary task and no
condition has a safety problem. If no difference, keep the simpler page (A) and revisit after 100
readers.*

This protocol pre-registers the reading of "clearly better" and how the 5–8/arm target and the
30-session stop point fit together:

- **Primary analysis at 24 sessions** (the planned target; 8 per arm). This is the only pre-registered
  look unless the interval is still too wide.
- **Stop for benefit** if the bootstrap 95% CI for **B − A** excludes 0 **and** the point estimate is
  ≥ **0.5 rubric points** (25% of the 0–2 scale), with no safety event in any arm.
- **Stop for futility** if the CI excludes the 0.5-point benefit (upper bound < 0.5); keep A and
  record the negative result.
- **Extend, do not keep looking:** if the 24-session CI is wider than **1.0 rubric point** and no
  safety event has occurred, add the remaining sessions up to the E1 stop point of **30**
  (9–10 per arm; report the deviation). Decide at 30 and stop. Do not continue beyond 30 for this
  decision without a new pre-registration.
- **Safety stop immediately** on a fabricated-citation acceptance, a privacy exposure, or a credible
  report that a surface misled a participant. Fix and restart; do not pool the affected sessions.
- **Administrative stop:** if recruitment yields <5 sessions per arm by the planned end date, report
  descriptive results only and do not make the ship/drop decision; extend or re-scope.

The stopping decision, the session count at which it was made, and the interval are recorded in the
result note. No optional stopping based on a p-value.

---

## 11. Analysis plan

`analysis.py` is the reference implementation for the descriptive and interval pieces below. Any
additional analysis is pre-registered in the result note before it is run.

1. **Data validation.** Every row is checked: arm ∈ {A,B,C}; task ID known; `success_0_2` ∈ {0,1,2};
   `seconds` ≥ 0; confidence 0–100; `correct` 0/1; `evidence_opened` 0/1; `would_cite_0_4` 0–4;
   `participant_code` contains no email/phone pattern; session IDs are internally consistent. Invalid
   data blocks the analysis (fix the source, do not silently drop rows).
2. **Descriptives.** Per arm: n sessions, n task attempts, mean and median success score, full-success
   rate (2s), mean/median seconds, evidence-open rate, mean confidence, accuracy, calibration,
   would-cite mean. Per task × arm: n, mean score, full-success count.
3. **Primary contrast.** B − A in mean success score (0–2). **Percentile bootstrap 95% CI**, 2,000
   resamples, resampling sessions within arm (fixed arm sizes), seed 20261105. Report point estimate,
   CI, n per arm. If either arm has <2 sessions, print "insufficient data" and do not compute.
4. **Full-success rate.** Wilson 95% interval per arm; bootstrap CI for the B − A difference in
   proportions as a secondary display.
5. **Time.** Median and mean seconds per arm and per task; report the 180 s cap count. Do not drop
   timeouts; they are failures/floors, not missing data.
6. **Calibration.** Mean confidence, accuracy, and the difference per arm and per task (§8).
7. **Evidence use.** Proportion of task attempts with `evidence_opened = 1`, with Wilson intervals;
   report C's strip exposure separately.
8. **Topic balance.** Print the topic × arm coverage; flag any topic missing from an arm (confounding
   check) and any session with fewer than four task rows.
9. **Missing/excluded data.** Pre-registered exclusions only: consent withdrawal, technical/logging
   failure, wrong arm shown, duplicate session. Performance is never an exclusion reason. Report the
   excluded count and reasons.
10. **Qualitative.** Two coders independently theme the think-aloud notes; disagreements resolved by
    discussion; quotes anonymised and checked for re-identifiability.
11. **Reporting discipline.** Report intervals, not just means; report exact n; label exploratory
    contrasts (A−C, B−C, task-level) as exploratory; no multiplicity-adjusted claim of significance
    from this sample; record negative and null results; archive the raw CSV/JSONL, the analysis output,
    and a hash of each.
12. **Reproducibility.** Record analysis script version/hash, Python version, bootstrap seed, and the
    exact command. `python3 analysis.py --self-test` proves the script runs on SYNTHETIC data; it is
    not evidence about readers.

---

## 12. Consent, privacy and ethics

- **Informed consent** before any task: purpose (comparing reader surfaces), what is recorded (answers,
  timings, confidence, optional audio, interaction events), voluntary participation, right to stop at
  any time, right to withdraw and have data deleted up to the analysis freeze, and who to contact.
- **Participants:** target readers (not the project team), 18+, recruited without pressure.
  Team members, co-authors and anyone who has seen the conditions are excluded. Compensation is modest
  and **not** contingent on performance.
- **No PII in the data file.** Use `participant_code` only (e.g. `P07`). The contact list, if any, is
  kept separately, access-controlled, and deleted after recruitment/analysis. `analysis.py` rejects
  codes that look like an email address or phone number.
- **Audio/notes:** record only with explicit consent; transcribe, then delete audio by the stated
  retention date (default 30 days after analysis freeze). Notes are anonymised before quoting.
- **Instrumentation:** no IP, no user agent, no cookies beyond the session; local logs only; no
  third-party analytics. The event log is deleted or pseudonymised after analysis.
- **Stimulus honesty:** participants are told the articles are demonstration drafts that may contain
  errors and are not a verified reference. Hide nothing about the task; the arms differ only in the
  surface under test.
- **No deception about the purpose**; the debrief explains the comparison and shows the other surfaces
  if the participant is interested.
- **Safety and distress:** stop if a participant is uncomfortable; no sensitive topics; no real
  living-person/company content.
- **Storage:** local, access-limited, backed up only with the rest of the study data; retention 12
  months then deletion; withdrawal requests honoured before the freeze.
- **Ethics review:** this is product usability testing, not clinical research; apply the consent and
  data-minimisation rules anyway. If results are published, check whether local review is required.

---

## 13. What result would change the product

| Result | Product action |
|---|---|
| B − A ≥ 0.5 rubric points, CI excludes 0, no safety event | Ship the **summary-first** surface (B) for overview/quick-fact readers; keep the full article one click away. Update the reader spec (§4.1 reader state 2) and D-08 notes. |
| C ≈ B on success **and** C raises evidence-open rate without hurting time/clarity | Keep the **visible evidence strip** (C); add it to the summary surface. |
| C hurts success/time or clarity vs B | Drop the strip; keep B (or A if B also fails). Record the negative result. |
| No difference at 24–30 sessions | Keep the **simpler page A**; drop the summary surface from launch and revisit after 100 readers, as E1 pre-registers. Do not keep the surface because it was built. |
| B/C better on ordinary but worse on contested topics | Restrict the summary surface to ordinary/structured topics; contested topics keep the full article + adjudication summary. Segment the launch, do not average the harm away. |
| Confidence rises but accuracy does not (overconfidence) | Add explicit limits/uncertainty to the summary and strip; do not ship until calibration is no worse than A. |
| Any fabricated-citation acceptance or privacy exposure | Stop; treat as a safety defect; fix before any surface ships. |
| Evidence-open rate falls while success is unchanged | Do not claim the surface improves verification; report the trade-off and keep the drawer equally reachable. |

**If B/C is not better**, the backlog's stated action applies: drop the summary surface from launch and
keep the lead + evidence drawer. **If C improves evidence use without hurting clarity**, keep the strip.

---

## 14. Threats to validity / what this cannot show

- Small n (6–8/arm) detects only large effects; intervals will be wide.
- Demonstration drafts are not reference articles; results from them are **pilot** results, not the
  E1 decision.
- Lab tasks and a facilitator differ from real reading; mobile/accessibility is E14, not E1.
- Confidence is self-report and subject to demand characteristics; calibration is secondary.
- Within-session task order and the "find the 2018 figure" substitution must be recorded, not guessed.
- A positive result on success does not establish long-term trust, citation behaviour, or retention.

---

## 15. Pre-session checklist

- [ ] Question, arms, tasks, rubric, primary contrast, stopping rule and analysis plan frozen (this
      file, versioned) **before** session 1.
- [ ] Six topics selected, revision IDs and hashes recorded; revision frozen for the study window.
- [ ] Topic × arm crossing table and task Latin square generated.
- [ ] Instrumentation piloted with 2 non-participants; export and hash verified.
- [ ] Consent form, debrief, data-retention statement ready.
- [ ] Coders trained on 2 practice transcripts; codebook agreed; κ dry run.
- [ ] `sessions.csv` header confirmed; no PII in participant codes.
- [ ] Facilitator script and 180 s timer ready.
- [ ] Result note template created; it must say **not run** until sessions actually happen.

## 16. Files

- `PROTOCOL.md` — this pre-registration.
- `sessions.csv` — empty data template; one row per task attempt; header only until real data exists.
- `analysis.py` — stdlib-only validation and analysis; `--self-test` uses SYNTHETIC data.
- `README.md` — exact commands.
