# E4 — Correction intake and triage cost

**Status: kit only — NOT RUN. No corrections have been injected and no triage timings exist.**
E4 requires a human steward receiving, triaging and resolving cases in real time. This directory
gives you the pre-registered protocol, 30 **SYNTHETIC** fictional cases, an empty triage log, and
a stdlib-only analysis script. An agent can prepare and analyse; it cannot run E4 or invent
timings, dispositions or satisfaction scores.

- **Question:** what does a reader correction actually cost to triage and resolve, and what
  service level is realistic for a solo steward?
- **Options:** A email/form + manual triage; B structured form with claim linking + queue;
  C B plus a volunteer rota.
- **Primary run:** 30 cases under arm A over two weeks (3 per business day); the analysis
  compares the median triage time with E4's **15-minute threshold**.
- **Decision:** median triage > 15 min ⇒ add structured claim linking and canned responses
  before public beta.

Read [`PROTOCOL.md`](PROTOCOL.md) first. It fixes the case mix, injection schedule, disposition
rubric, measures, stopping rule, inter-rater subset and decision thresholds.

## Files

| File | Purpose |
|---|---|
| `PROTOCOL.md` | Pre-registration: options, 30-case mix, schedule, rubric, measures, thresholds, consent. |
| `cases.csv` | 30 **SYNTHETIC** fictional cases (10 valid, 10 wrong, 5 duplicate, 5 legal/privacy/COI). |
| `triage_log.csv` | **Empty template** — one row per case per intake arm. Header only. |
| `analysis.py` | Case/log validation, cost + correctness + SLA + kappa + threshold, `--self-test`. |
| `README.md` | This file. |

All 30 cases are labelled `SYNTHETIC` in `notes`; they are role-play material, not real
reports, and must not be sent to anyone outside the study. The article slugs are the three
demonstration articles seeded in `core/seeding.py`:
`subvocal-interfaces`, `quadratic-funding`, `encyclopedia-galactica`.

## Exact commands

Run from this directory:

```bash
cd experiments/E4-correction-triage

# 1. Prove the script works. Generates additional SYNTHETIC fixtures in a temp dir.
python3 analysis.py --self-test

# 2. Validate the 30-case file and the empty log template (no cost data yet).
python3 analysis.py

# 3. Analyse collected data (defaults: cases.csv and triage_log.csv).
python3 analysis.py --cases cases.csv --log triage_log.csv

# 4. Analyse a specific arm and an explicit open-case cutoff.
python3 analysis.py --arm A --threshold 15 --min-cases 10 \
  --as-of 2026-11-21T17:00:00-05:00
```

Options: `--cases FILE`, `--log FILE`, `--arm {A,B,C}` (primary arm for the threshold,
default A), `--threshold MINUTES` (default 15), `--min-cases N` (default 10),
`--as-of ISO_TIMESTAMP`, `--bootstrap N` (≥100, default 2000), `--seed N`,
`--self-test`.

Exit codes: `0` = analysis or empty log; `1` = case/log validation errors;
`2` = file/argument error.

## Filling `triage_log.csv`

One row per case per intake arm. The template header is:

```text
case_id,intake_option,received_at,first_response_at,triaged_at,resolved_at,minutes_to_triage,minutes_to_resolve,disposition,correct_0_1,reviewer_code,second_reviewer_code,second_disposition,notes
```

- `received_at` is when the steward could first see the case (inbox arrival), **not** the planned
  `injected_at`. `triaged_at` and `resolved_at` are the actual times.
- `minutes_to_triage` / `minutes_to_resolve` may be left blank; the script derives them from the
  timestamps and warns if provided values disagree by more than 2 minutes.
- A case can be logged while still open: give `received_at` (and optionally
  `first_response_at`), leave `triaged_at`/`resolved_at` and disposition blank. The script reports
  open-case age against `--as-of`.
- `disposition` ∈ `accepted`, `rejected`, `duplicate`, `needs_info` (rubric in `PROTOCOL.md` §5).
- `correct_0_1` is optional; the script computes correctness from `disposition` vs the case's
  `expected_disposition` and warns if the supplied flag disagrees.
- `reviewer_code` / `second_reviewer_code` are short codes (`R1`, `R2`), never names or contact
  details. The 10-case inter-rater subset needs both `second_reviewer_code` and
  `second_disposition`.
- Mark synthetic/test entries `SYNTHETIC` in `notes`.

Validation rejects: unknown `case_id`, bad intake option, invalid disposition or timestamp
order, duplicate rows for the same case+arm, invalid minutes, incomplete second-review pairs,
and PII-looking reviewer codes. Warnings flag timestamp/minute disagreements, an inter-rater
subset smaller than 10, and duplicate-parent timing mistakes.

## What the analysis prints

- **Case mix:** counts vs the pre-registered 10/10/5/5 and severity distribution.
- **Cost:** per arm, median/mean/p90 minutes to triage, median time to first response, median
  minutes to resolve; overall too.
- **Queue age:** open cases, median wait to first response, oldest open case at the cutoff.
- **Correctness:** exact match rate, false-accept and false-reject rates with denominators, a
  confusion matrix (expected × observed), and per-category correctness.
- **E4 threshold:** `E4 THRESHOLD: CROSSED / NOT CROSSED / UNDETERMINED` for the primary arm,
  with the E4 action. It requires at least `--min-cases` (default 10) triaged cases.
- **SLA:** acknowledgement > 2 business days, resolution > 14 days, legal first response > 24 h.
- **Inter-rater:** pair count, raw agreement, Cohen's κ.
- **Stability:** first-half vs second-half median and a bootstrap median CI.
- **Reporter satisfaction:** explicitly "not recorded" — never imputed.

## Notes and limits

- The 30 cases are fictional and the article content is demonstration material. This experiment
  measures **triage cost and disposition correctness**, not whether the article is true.
- The synthetic run cannot measure reporter satisfaction. Do not report it as zero; collect it
  separately from consenting real reporters.
- Do not re-inject the same 30 cases as an A/B comparison; the steward has seen them. A second
  wave needs a fresh case set from the same mix (see `PROTOCOL.md` §2).
- `--self-test` generates 30 additional synthetic cases and two synthetic logs (one crossing the
  15-minute threshold, one not), plus empty/broken/tiny cases. Everything is printed with a
  **SYNTHETIC** banner; it is a code check, not a correction-cost result.
- No external dependencies; Python 3.8+ stdlib only.
- No invented results: the shipped log is empty, so the analysis prints "No triage entries found".
