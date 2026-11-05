# Experiment kits

Two runnable **pre-registration kits** prepared from `docs/EXPERIMENTS.md`:

| Kit | Backlog item | Status | Who can complete it |
|---|---|---|---|
| [`E1-reader-task/`](E1-reader-task/) | E1 — reader task success: summary-first vs article-first | **Not run** — no sessions, no results | Human readers + a facilitator. An agent can prepare and analyse only. |
| [`E4-correction-triage/`](E4-correction-triage/) | E4 — correction intake and triage cost | **Not run** — no injections, no timings | A human steward (and a second reviewer for the inter-rater subset). An agent can prepare and analyse only. |

Both kits are deliberately honest about this: the documents, cases and analysis scripts exist,
but neither experiment has been executed. There are **no empirical results** in this directory.
`cases.csv` in E4 and the `--self-test` fixtures are marked **SYNTHETIC**; they are role-play or
code-check material, not evidence about readers, reporters or capacity.

## What is here

- `E1-reader-task/PROTOCOL.md` — conditions A/B/C, 6-topic selection criteria, counterbalancing,
  four tasks, 0–2 rubric, measures, confidence calibration, evidence-open instrumentation,
  stopping rule, analysis plan (intervals, bootstrap), consent/privacy, and the product decision.
- `E1-reader-task/sessions.csv` — empty template (one row per task attempt).
- `E1-reader-task/analysis.py` — stdlib-only validation, per-arm success/time/evidence/
  calibration, bootstrap 95% interval for B − A, `--self-test`.
- `E4-correction-triage/PROTOCOL.md` — options A/B/C, 30-case mix (10 valid, 10 wrong, 5
  duplicate, 5 legal/privacy/COI), two-week injection schedule, disposition rubric, measures,
  inter-rater subset, stopping rule, and the E4 thresholds (>15 min triage ⇒ structured claim
  linking before public beta).
- `E4-correction-triage/cases.csv` — 30 SYNTHETIC fictional cases using the seeded demo slugs.
- `E4-correction-triage/triage_log.csv` — empty log template.
- `E4-correction-triage/analysis.py` — stdlib-only mix validation, cost/queue statistics,
  observed-vs-expected dispositions, SLA and κ, threshold check, `--self-test`.
- `SELF-TEST-TRANSCRIPTS.txt` — captured output of both `--self-test` commands (SYNTHETIC only).

## Exact self-test commands

```bash
cd experiments/E1-reader-task && python3 analysis.py --self-test
cd experiments/E4-correction-triage && python3 analysis.py --self-test
```

Both are stdlib-only (Python 3.8+) and exit 0 when the checks pass. The output is a code-path
check on SYNTHETIC fixtures; it is not a result and must not be cited as one.

## Constraints respected

- No external dependencies, no server restart, no DB modification.
- No edits outside `experiments/`; no commits or pushes.
- No PII in any file; participant/reviewer codes only.
- No invented empirical results and no claim that sessions, injections or triage happened.
