# E1 — Reader task success (summary-first vs article-first)

**Status: kit only — NOT RUN. No sessions have happened and no results exist.**
E1 needs human readers. This directory gives you the pre-registered protocol, an empty data
template, and a stdlib-only analysis script. An agent can prepare and analyse; it cannot
complete E1 or invent participant data.

- **Question:** does a self-contained summary/at-a-glance surface, with the full article one
  click away, improve reader task success over a single long article?
- **Arms:** A article-first (current page); B summary-first; C summary + visible evidence strip.
- **Design:** 18–24 sessions, 5–8 per arm, 6 topics (2 ordinary, 2 contested, 2 structured),
  full topic × arm crossing, counterbalanced task order.
- **Primary outcome:** mean task-success score (0–2); primary contrast B − A.

Read [`PROTOCOL.md`](PROTOCOL.md) before touching the data file. It fixes the rubric, the
stopping rule, the consent rules and what result would change the product.

## Files

| File | Purpose |
|---|---|
| `PROTOCOL.md` | Pre-registration: conditions, topics, tasks, rubric, measures, stopping rule, analysis, consent. |
| `sessions.csv` | **Empty template** — one row per task attempt. Header only until real sessions exist. |
| `analysis.py` | Validation + descriptive analysis + bootstrap CI + `--self-test`. Stdlib only. |
| `README.md` | This file. |

## Exact commands

Run from this directory:

```bash
cd experiments/E1-reader-task

# 1. Prove the script works. Uses generated SYNTHETIC data, clearly labelled.
python3 analysis.py --self-test

# 2. Analyse the (empty) template. Should print "No task rows found" and exit 0.
python3 analysis.py sessions.csv

# 3. Analyse collected data (CSV).
python3 analysis.py sessions.csv

# 4. Analyse collected data (JSONL), with a larger bootstrap.
python3 analysis.py sessions.jsonl --format jsonl --bootstrap 5000
```

Options: `--format {auto,csv,jsonl}`, `--bootstrap N` (≥100, default 2000),
`--seed N` (default 20261105), `--self-test`.

Exit codes: `0` = analysis or empty template; `1` = validation errors (fix the data);
`2` = file/argument error.

## Filling `sessions.csv`

One row per **task attempt**; a session has four rows with the same `session_id`,
`condition`, `topic` and `participant_code`.

```text
session_id,condition,topic,participant_code,task,success_0_2,seconds,confidence_0_100,correct,evidence_opened,would_cite_0_4,notes
S01,A,quadratic-funding,P01,explain_1min,1,58.0,70,0,0,2,SYNTHETIC EXAMPLE ONLY - not a real session
```

The row above is **SYNTHETIC** and is shown only to illustrate the format. Do not paste it into
`sessions.csv` and report it. Real rows must never contain names, emails, phone numbers or
other PII: use a code such as `P07` and keep the contact list elsewhere.

| Column | Allowed values |
|---|---|
| `session_id` | Short identifier; repeated across the session's four task rows. |
| `condition` | `A`, `B` or `C`. |
| `topic` | The article slug for that session. |
| `participant_code` | `P01`-style code only; email/phone-like values are rejected. |
| `task` | `explain_1min`, `find_2018_figure`, `find_disputes`, `cite_claim`. |
| `success_0_2` | `0`, `1`, `2` (rubric in `PROTOCOL.md` §6). |
| `seconds` | Time to answer; cap at 180. |
| `confidence_0_100` | Self-reported confidence, 0–100. |
| `correct` | `1` if rubric score is 2, else `0` (used for calibration). |
| `evidence_opened` | `1` if evidence was opened during that task, else `0`. |
| `would_cite_0_4` | "Would you trust this to cite?", 0–4. |
| `notes` | Free text; mark any synthetic/test row `SYNTHETIC`. |

Validation rejects: bad arm, unknown task, out-of-range numbers, duplicate task rows, mixed
arm/topic/participant inside one session, and PII-looking participant codes. Warnings flag
incomplete sessions (≠4 tasks), a participant in more than one arm, and incomplete topic × arm
crossing. Errors block the analysis; the script never silently drops rows.

## What the analysis prints

- Sessions and task rows per arm, topic coverage.
- Per arm: mean/median success score, SD, full-success rate (score 2), median/mean seconds,
  evidence-open rate and Wilson interval, mean confidence, accuracy, calibration
  (mean confidence − accuracy), mean would-cite.
- Per task: mean success and calibration.
- **Primary contrast:** B − A mean success score with a percentile-bootstrap 95% interval
  (2,000 session-level resamples within arm, fixed seed). If either arm has fewer than two
  sessions it prints "insufficient data" instead of inventing an interval.
- Full-success difference with a bootstrap interval.
- Validation warnings and a reading guard.

The script reports intervals, not p-values. With 5–8 readers per arm the intervals will be wide;
that is the point. The stopping rule is in `PROTOCOL.md` §10.

## Notes and limits

- The three demo articles currently in the app (`subvocal-interfaces`, `quadratic-funding`,
  `encyclopedia-galactica`) are **demonstration drafts**. Use them to pilot the script and the
  instrumentation; do **not** run the E1 decision on them as if they were reference articles.
  Fill the six topic slots from the chosen anchor topics (see `PROTOCOL.md` §4).
- `--self-test` generates an 18-session synthetic fixture in a temporary directory and prints
  it with a **SYNTHETIC** banner. It checks code paths only; it is not evidence about readers.
- No external dependencies; Python 3.8+ stdlib only.
- No invented results: an empty template reports "No task rows found". Only real, consented,
  human-collected data can produce an E1 result.
