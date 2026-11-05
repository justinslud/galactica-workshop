#!/usr/bin/env python3
"""E1 reader-task analysis: summary-first vs article-first.

Reads a sessions CSV or JSONL, validates it, and prints descriptive results plus a
percentile-bootstrap interval for the pre-registered primary contrast B - A.

This script never invents participant data. If the data file has no rows it says so.
`--self-test` runs on a generated SYNTHETIC fixture and labels the output as such.

Usage:
    python3 analysis.py sessions.csv
    python3 analysis.py sessions.jsonl --format jsonl --bootstrap 5000
    python3 analysis.py --self-test

Stdlib only (Python 3.8+).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
import statistics
import sys
import tempfile
from pathlib import Path

COLUMNS = [
    "session_id",
    "condition",
    "topic",
    "participant_code",
    "task",
    "success_0_2",
    "seconds",
    "confidence_0_100",
    "correct",
    "evidence_opened",
    "would_cite_0_4",
    "notes",
]

CONDITIONS = ("A", "B", "C")
CONDITION_LABEL = {
    "A": "article-first (current page)",
    "B": "summary-first",
    "C": "summary + evidence strip",
}
TASKS = ("explain_1min", "find_2018_figure", "find_disputes", "cite_claim")
TASK_LABEL = {
    "explain_1min": "explain in one minute",
    "find_2018_figure": "find the 2018 figure",
    "find_disputes": "find who disputes this",
    "cite_claim": "cite this claim",
}
TASK_ALIASES = {
    "explain_1min": "explain_1min",
    "explain_in_one_minute": "explain_1min",
    "explain in one minute": "explain_1min",
    "find_2018_figure": "find_2018_figure",
    "find_2018_fig": "find_2018_figure",
    "find the 2018 figure": "find_2018_figure",
    "find_disputes": "find_disputes",
    "find_who_disputes": "find_disputes",
    "find who disputes this": "find_disputes",
    "cite_claim": "cite_claim",
    "cite_this_claim": "cite_claim",
    "cite this claim": "cite_claim",
}

CODE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{1,23}$")
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
PHONE_RE = re.compile(r"\d[\d\s().+-]{6,}\d")

DEFAULT_BOOTSTRAP = 2000
DEFAULT_SEED = 20261105
BOOTSTRAP_MIN_UNITS = 2  # sessions per arm, for an interval


class DataError(Exception):
    """Fatal problem with the input file (not a per-row validation error)."""


# --------------------------------------------------------------------------------------
# Loading and validation
# --------------------------------------------------------------------------------------


def infer_format(path: Path, fmt: str) -> str:
    if fmt != "auto":
        return fmt
    if path.suffix.lower() == ".jsonl":
        return "jsonl"
    if path.suffix.lower() == ".csv":
        return "csv"
    # Sniff: first non-empty line starting with "{" is JSONL.
    try:
        with path.open(encoding="utf-8-sig") as fh:
            for line in fh:
                if line.strip():
                    return "jsonl" if line.lstrip().startswith("{") else "csv"
    except OSError as exc:
        raise DataError(f"cannot read {path}: {exc}") from exc
    return "csv"


def load_raw(path: Path, fmt: str):
    """Return (rows, first_line_number, format_used, warnings)."""
    fmt = infer_format(path, fmt)
    raw = []
    warnings = []

    if fmt == "csv":
        try:
            with path.open(newline="", encoding="utf-8-sig") as fh:
                reader = csv.DictReader(fh)
                if reader.fieldnames is None:
                    raise DataError("CSV has no header row")
                fields = [(f or "").strip() for f in reader.fieldnames]
                missing = [c for c in COLUMNS if c not in fields]
                if missing:
                    raise DataError(
                        "CSV is missing required column(s): " + ", ".join(missing)
                    )
                extra = [f for f in fields if f not in COLUMNS]
                if extra:
                    warnings.append(
                        "CSV has extra column(s) ignored by this script: "
                        + ", ".join(extra)
                    )
                for line_no, row in enumerate(reader, start=2):
                    if not any((v or "").strip() for v in row.values() if v is not None):
                        continue
                    raw.append((line_no, {(k or "").strip(): v for k, v in row.items()}))
        except OSError as exc:
            raise DataError(f"cannot read {path}: {exc}") from exc
    else:
        try:
            with path.open(encoding="utf-8-sig") as fh:
                for line_no, line in enumerate(fh, start=1):
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise DataError(f"line {line_no}: invalid JSON: {exc}") from exc
                    if not isinstance(obj, dict):
                        raise DataError(f"line {line_no}: JSONL row is not an object")
                    raw.append((line_no, obj))
        except OSError as exc:
            raise DataError(f"cannot read {path}: {exc}") from exc

    return raw, fmt, warnings


def _text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_int(value, field, line_no, errors, lo, hi):
    text = _text(value)
    if text == "":
        errors.append(f"line {line_no}: {field} is empty")
        return None
    try:
        number = int(text)
    except ValueError:
        errors.append(f"line {line_no}: {field} must be an integer, got {text!r}")
        return None
    if not (lo <= number <= hi):
        errors.append(
            f"line {line_no}: {field}={number} is outside the allowed range {lo}-{hi}"
        )
        return None
    return number


def _parse_seconds(value, line_no, errors):
    text = _text(value)
    if text == "":
        errors.append(f"line {line_no}: seconds is empty")
        return None
    try:
        number = float(text)
    except ValueError:
        errors.append(f"line {line_no}: seconds must be a number, got {text!r}")
        return None
    if not math.isfinite(number) or number < 0:
        errors.append(f"line {line_no}: seconds must be a finite number >= 0")
        return None
    if number > 3600:
        errors.append(
            f"line {line_no}: seconds={number} looks implausible (> 3600); "
            "cap the task timer and record it"
        )
        return None
    return number


def validate(raw_rows):
    """Return (rows, errors, warnings). Rows are normalized dicts."""
    rows = []
    errors = []
    warnings = []
    seen_session_task = set()

    for line_no, raw in raw_rows:
        before = len(errors)

        session_id = _text(raw.get("session_id"))
        if not session_id:
            errors.append(f"line {line_no}: session_id is empty")
        elif len(session_id) > 64:
            errors.append(f"line {line_no}: session_id is longer than 64 characters")

        condition = _text(raw.get("condition")).upper()
        if condition not in CONDITIONS:
            errors.append(
                f"line {line_no}: condition={condition!r} is not one of A, B, C"
            )

        topic = _text(raw.get("topic"))
        if not topic:
            errors.append(f"line {line_no}: topic is empty")
        elif len(topic) > 80:
            errors.append(f"line {line_no}: topic is longer than 80 characters")

        participant = _text(raw.get("participant_code"))
        if not participant:
            errors.append(f"line {line_no}: participant_code is empty")
        else:
            if not CODE_RE.match(participant):
                errors.append(
                    f"line {line_no}: participant_code={participant!r} must be a short "
                    "code like P07 (letters, digits, dash, underscore; 2-24 chars)"
                )
            if EMAIL_RE.search(participant) or PHONE_RE.search(participant):
                errors.append(
                    f"line {line_no}: participant_code looks like PII (email/phone); "
                    "use a non-identifying code such as P07"
                )

        task_raw = _text(raw.get("task")).lower().replace("-", "_")
        task = TASK_ALIASES.get(task_raw)
        if task is None:
            errors.append(
                f"line {line_no}: task={_text(raw.get('task'))!r} is not one of "
                + ", ".join(TASKS)
            )

        success = _parse_int(raw.get("success_0_2"), "success_0_2", line_no, errors, 0, 2)
        seconds = _parse_seconds(raw.get("seconds"), line_no, errors)
        confidence = _parse_int(
            raw.get("confidence_0_100"), "confidence_0_100", line_no, errors, 0, 100
        )
        correct = _parse_int(raw.get("correct"), "correct", line_no, errors, 0, 1)
        evidence = _parse_int(
            raw.get("evidence_opened"), "evidence_opened", line_no, errors, 0, 1
        )
        would_cite = _parse_int(
            raw.get("would_cite_0_4"), "would_cite_0_4", line_no, errors, 0, 4
        )
        notes = _text(raw.get("notes"))

        if len(errors) > before:
            continue

        if correct is not None and success is not None and correct != int(success == 2):
            warnings.append(
                f"line {line_no}: correct={correct} but success_0_2={success}; "
                "the protocol defines correct=1 iff the rubric score is 2"
            )

        key = (session_id, task)
        if key in seen_session_task:
            errors.append(
                f"line {line_no}: duplicate task row for session {session_id}, task {task}"
            )
            continue
        seen_session_task.add(key)

        rows.append(
            {
                "session_id": session_id,
                "condition": condition,
                "topic": topic,
                "participant_code": participant,
                "task": task,
                "success_0_2": success,
                "seconds": seconds,
                "confidence_0_100": confidence,
                "correct": correct,
                "evidence_opened": evidence,
                "would_cite_0_4": would_cite,
                "notes": notes,
                "line_no": line_no,
            }
        )

    # Session-level consistency: one arm, topic and participant per session id.
    by_session = {}
    for row in rows:
        by_session.setdefault(row["session_id"], []).append(row)
    for session_id, session_rows in sorted(by_session.items()):
        conditions = {r["condition"] for r in session_rows}
        topics = {r["topic"] for r in session_rows}
        participants = {r["participant_code"] for r in session_rows}
        if len(conditions) > 1:
            errors.append(
                f"session {session_id}: mixed conditions {sorted(conditions)}; "
                "one session must be one arm"
            )
        if len(topics) > 1:
            errors.append(
                f"session {session_id}: mixed topics {sorted(topics)}; "
                "one session must be one topic"
            )
        if len(participants) > 1:
            errors.append(
                f"session {session_id}: mixed participant codes {sorted(participants)}"
            )
        if len(session_rows) != len(TASKS):
            warnings.append(
                f"session {session_id}: {len(session_rows)} task row(s), "
                f"expected {len(TASKS)} (incomplete session; kept but flagged)"
            )

    # Design checks.
    participant_arms = {}
    for row in rows:
        participant_arms.setdefault(row["participant_code"], set()).add(row["condition"])
    for participant, arms in sorted(participant_arms.items()):
        if len(arms) > 1:
            warnings.append(
                f"participant {participant}: appears in more than one arm "
                f"{sorted(arms)}; between-subject design violated (kept but flagged)"
            )

    total_sessions = len(by_session)
    topic_arms = {}
    for row in rows:
        topic_arms.setdefault(row["topic"], set()).add(row["condition"])
    if total_sessions >= 18:
        for topic, arms in sorted(topic_arms.items()):
            if len(arms) < len(CONDITIONS):
                warnings.append(
                    f"topic {topic}: appears in arm(s) {sorted(arms)} only; "
                    "full topic x arm crossing is incomplete"
                )

    synthetic = sum(1 for r in rows if "synthetic" in r["notes"].lower())
    return rows, errors, warnings, synthetic


# --------------------------------------------------------------------------------------
# Statistics helpers
# --------------------------------------------------------------------------------------


def _mean(values):
    return sum(values) / len(values) if values else None


def _median(values):
    return statistics.median(values) if values else None


def _sd(values):
    return statistics.stdev(values) if len(values) >= 2 else None


def wilson_interval(k: int, n: int, z: float = 1.96):
    """Wilson score interval for a proportion; returns (low, high) or None."""
    if n <= 0:
        return None
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def percentile(values, q):
    """Linear-interpolation percentile; q in [0, 1]."""
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - pos) + ordered[hi] * (pos - lo)


def bootstrap_diff(
    arm_a, arm_b, n_boot=DEFAULT_BOOTSTRAP, seed=DEFAULT_SEED
):
    """Percentile bootstrap CI for mean(B) - mean(A), resampling within arm.

    Returns (low, high, point) or None when an arm has too few rows.
    """
    if len(arm_a) < BOOTSTRAP_MIN_UNITS or len(arm_b) < BOOTSTRAP_MIN_UNITS:
        return None
    if n_boot < 100:
        raise ValueError("bootstrap resamples must be >= 100")
    rng = random.Random(seed)
    la, lb = len(arm_a), len(arm_b)
    diffs = []
    for _ in range(n_boot):
        mean_a = sum(arm_a[rng.randrange(la)] for _ in range(la)) / la
        mean_b = sum(arm_b[rng.randrange(lb)] for _ in range(lb)) / lb
        diffs.append(mean_b - mean_a)
    return percentile(diffs, 0.025), percentile(diffs, 0.975), (_mean(arm_b) - _mean(arm_a))


def _fmt(value, digits=2, suffix=""):
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.{digits}f}{suffix}"
    return f"{value}{suffix}"


def _pct(value, digits=1):
    if value is None:
        return "-"
    return f"{value * 100:.{digits}f}%"


# --------------------------------------------------------------------------------------
# Summaries and report
# --------------------------------------------------------------------------------------


def summarize(rows):
    arms = {c: [r for r in rows if r["condition"] == c] for c in CONDITIONS}
    summary = {}
    for condition, arm_rows in arms.items():
        scores = [r["success_0_2"] for r in arm_rows]
        session_scores = {}
        for r in arm_rows:
            session_scores.setdefault(r["session_id"], []).append(r["success_0_2"])
        session_means = [_mean(v) for v in session_scores.values()]
        times = [r["seconds"] for r in arm_rows]
        conf = [r["confidence_0_100"] / 100.0 for r in arm_rows]
        accuracy = [r["correct"] for r in arm_rows]
        evidence = [r["evidence_opened"] for r in arm_rows]
        cite = [r["would_cite_0_4"] for r in arm_rows]
        n = len(arm_rows)
        full = sum(1 for s in scores if s == 2)
        summary[condition] = {
            "n": n,
            "sessions": len({r["session_id"] for r in arm_rows}),
            "success_mean": _mean(session_means),
            "attempt_mean": _mean(scores),
            "success_median": _median(scores),
            "success_sd": _sd(scores),
            "full_k": full,
            "full_rate": (full / n) if n else None,
            "full_ci": wilson_interval(full, n),
            "time_mean": _mean(times),
            "time_median": _median(times),
            "timeouts": sum(1 for t in times if t >= 180),
            "evidence_k": sum(evidence),
            "evidence_rate": (sum(evidence) / n) if n else None,
            "evidence_ci": wilson_interval(sum(evidence), n),
            "conf_mean": _mean(conf),
            "accuracy": _mean(accuracy),
            "calibration_pp": (
                (_mean(conf) - _mean(accuracy)) * 100 if n else None
            ),
            "cite_mean": _mean(cite),
            "scores": session_means,
        }
    return summary, arms


def _task_cell(rows, task, condition, metric):
    vals = [
        r[metric]
        for r in rows
        if r["task"] == task and r["condition"] == condition
    ]
    if not vals:
        return "-"
    if metric == "success_0_2":
        return f"{_mean(vals):.2f} (n={len(vals)})"
    if metric == "confidence_0_100":
        return f"{_mean(vals):.0f}% (n={len(vals)})"
    return str(len(vals))


def build_report(
    rows, path_label, n_boot=DEFAULT_BOOTSTRAP, seed=DEFAULT_SEED, warnings=None,
    synthetic=0,
):
    warnings = list(warnings or [])
    lines = []
    add = lines.append

    add("E1 - READER TASK SUCCESS: SUMMARY-FIRST vs ARTICLE-FIRST")
    add(f"Data: {path_label}")
    sessions = len({r["session_id"] for r in rows})
    add(f"Task rows: {len(rows)}  |  Sessions: {sessions}  |  "
        f"Bootstrap: {n_boot} resamples (seed {seed})")
    add("")

    if synthetic:
        add("!" * 78)
        add(f"WARNING: {synthetic} row(s) are marked SYNTHETIC. This is NOT real "
            "participant data.")
        add("Do not report these numbers as an experimental result.")
        add("!" * 78)
        add("")

    if not rows:
        add("No task rows found. The template is empty, so there is nothing to analyse.")
        add("This is the expected state before any sessions have been run.")
        return "\n".join(lines)

    summary, arms = summarize(rows)
    add("DESIGN BALANCE")
    add(f"  Sessions per arm: "
        + "  ".join(f"{c}={summary[c]['sessions']}" for c in CONDITIONS))
    add(f"  Task rows per arm: "
        + "  ".join(f"{c}={summary[c]['n']}" for c in CONDITIONS))
    topic_arms = {}
    for row in rows:
        topic_arms.setdefault(row["topic"], {}).setdefault(row["condition"], 0)
        topic_arms[row["topic"]][row["condition"]] += 1
    for topic in sorted(topic_arms):
        cells = "  ".join(
            f"{c}={topic_arms[topic].get(c, 0)}" for c in CONDITIONS
        )
        add(f"  Topic {topic}: {cells}")
    if sessions < 18:
        add(f"  NOTE: {sessions} sessions is below the 18-session full-crossing plan; "
            "descriptive only.")
    add("")

    add("PER-CONDITION TASK SUCCESS, TIME AND EVIDENCE USE")
    add(f"  {'Arm':<4}{'Sess':>5}{'Att':>5}{'Mean':>8}{'SD':>7}{'Full(2)':>15}"
        f"{'Median s':>11}{'Mean s':>9}{'Evidence':>10}")
    for c in CONDITIONS:
        s = summary[c]
        full = f"{s['full_k']}/{s['n']} ({_pct(s['full_rate'])})" if s["n"] else "-"
        add(
            f"  {c:<4}{s['sessions']:>5}{s['n']:>5}"
            f"{_fmt(s['success_mean']):>8}{_fmt(s['success_sd']):>7}"
            f"{full:>15}{_fmt(s['time_median'], 1):>11}"
            f"{_fmt(s['time_mean'], 1):>9}{_pct(s['evidence_rate']):>10}"
        )
    add("  Mean is the mean of per-session task-success means (the pre-registered unit);")
    add("  full-success rate and evidence use are attempt-level.")
    add("")

    add("PER-CONDITION CONFIDENCE CALIBRATION (mean confidence - accuracy)")
    add(f"  {'Arm':<4}{'Mean conf':>10}{'Accuracy':>10}{'Calib pp':>10}"
        f"{'Would cite':>12}   Evidence 95% CI")
    for c in CONDITIONS:
        s = summary[c]
        ci = s["evidence_ci"]
        ci_text = f"[{_pct(ci[0])}, {_pct(ci[1])}]" if ci else "-"
        add(
            f"  {c:<4}{_pct(s['conf_mean']):>10}{_pct(s['accuracy']):>10}"
            f"{_fmt(s['calibration_pp'], 1):>10}{_fmt(s['cite_mean']):>12}"
            f"   {ci_text}"
        )
    add("  Calibration > 0 means overconfident; < 0 means underconfident.")
    add("")

    add("PER-TASK SUCCESS (mean score 0-2, attempts)")
    for task in TASKS:
        cells = "  ".join(
            f"{c}={_task_cell(rows, task, c, 'success_0_2')}" for c in CONDITIONS
        )
        add(f"  {TASK_LABEL[task]:<24} {cells}")
    add("")

    add("PER-TASK CALIBRATION (mean confidence - accuracy, attempts)")
    for task in TASKS:
        cells = []
        for c in CONDITIONS:
            task_rows = [r for r in rows if r["task"] == task and r["condition"] == c]
            if task_rows:
                cal = (
                    _mean([r["confidence_0_100"] / 100.0 for r in task_rows])
                    - _mean([r["correct"] for r in task_rows])
                ) * 100
                cells.append(f"{c}={cal:+.1f}pp (n={len(task_rows)})")
            else:
                cells.append(f"{c}=- (n=0)")
        add(f"  {TASK_LABEL[task]:<24} " + "  ".join(cells))
    add("")

    add("PRIMARY CONTRAST (B - A, mean rubric score 0-2; positive favours summary-first B)")
    a = summary["A"]
    b = summary["B"]
    add(f"  A: mean {_fmt(a['success_mean'])} (session-level), "
        f"n={a['sessions']} sessions / {a['n']} attempts")
    add(f"  B: mean {_fmt(b['success_mean'])} (session-level), "
        f"n={b['sessions']} sessions / {b['n']} attempts")
    result = bootstrap_diff(
        a["scores"], b["scores"], n_boot=n_boot, seed=seed
    )
    if result is None:
        add(f"  INSENSITIVE: insufficient data for a bootstrap interval "
            f"(need >= {BOOTSTRAP_MIN_UNITS} sessions per arm; "
            f"A={a['sessions']}, B={b['sessions']}). No interval is reported; do not "
            "read a difference from this.")
    else:
        low, high, point = result
        add(f"  Difference (B - A): {point:+.2f} rubric points")
        add(f"  Bootstrap 95% CI: [{low:+.2f}, {high:+.2f}] "
            f"({n_boot} session-level resamples within arm, seed {seed})")
        if low > 0:
            add("  Interval excludes 0 and favours B; apply the pre-registered "
                "stopping/benefit threshold, not this line alone.")
        elif high < 0:
            add("  Interval excludes 0 and favours A (article-first).")
        else:
            add("  Interval includes 0: this dataset does not distinguish the arms.")
    add("")

    add("FULL-SUCCESS RATE (score 2) AS A SECONDARY DISPLAY (attempt-level)")
    for c in CONDITIONS:
        s = summary[c]
        ci = s["full_ci"]
        ci_text = f"[{_pct(ci[0])}, {_pct(ci[1])}]" if ci else "-"
        add(f"  {c}: {s['full_k']}/{s['n']} = {_pct(s['full_rate'])}  "
            f"Wilson 95% CI {ci_text}")
    binary_a = [1 if r["success_0_2"] == 2 else 0 for r in arms["A"]]
    binary_b = [1 if r["success_0_2"] == 2 else 0 for r in arms["B"]]
    binary_result = bootstrap_diff(binary_a, binary_b, n_boot=n_boot, seed=seed)
    if binary_result is not None:
        low, high, point = binary_result
        add(f"  Difference B - A: {point * 100:+.1f} pp; "
            f"bootstrap 95% CI [{low * 100:+.1f}, {high * 100:+.1f}] pp")
    else:
        add("  Difference B - A: insufficient data for an interval.")
    add("")

    if warnings:
        add(f"VALIDATION WARNINGS ({len(warnings)})")
        for warning in warnings:
            add(f"  - {warning}")
        add("")

    add("READING GUARD")
    add("  * These are descriptive estimates with intervals, not a significance test.")
    add("  * Small samples give wide intervals; do not treat a point estimate as the effect.")
    add("  * The pre-registered decision rule is in PROTOCOL.md sections 10-12.")
    if any(summary[c]["sessions"] < 5 for c in CONDITIONS):
        add("  * At least one arm has fewer than 5 sessions: descriptive only, no ship/drop "
            "decision.")
    add("  * Evidence-open rate measures navigation, not understanding; confidence is "
        "self-report.")
    if synthetic:
        add("  * SYNTHETIC rows present: code-path check only, not participant evidence.")

    return "\n".join(lines)


# --------------------------------------------------------------------------------------
# Self-test (SYNTHETIC only)
# --------------------------------------------------------------------------------------


def _synthetic_rows():
    """Deterministic 18-session fixture: 6 topics x 3 arms x 4 tasks. SYNTHETIC."""
    rows = []
    session_no = 0
    pattern = {
        "A": [0, 1, 1, 1, 1, 2],  # mean 1.00
        "B": [1, 2, 2, 1, 2, 1],  # mean 1.50
        "C": [1, 2, 1, 2, 1, 2],  # mean 1.50
    }
    for topic_i in range(6):
        if topic_i < 2:
            stratum = "ordinary"
        elif topic_i < 4:
            stratum = "contested"
        else:
            stratum = "structured"
        topic = f"t{topic_i + 1}-{stratum}"
        for arm_i, condition in enumerate(CONDITIONS):
            session_no += 1
            session_id = f"SYN-S{session_no:02d}"
            participant = f"SYN-P{session_no:02d}"
            tasks = TASKS[arm_i:] + TASKS[:arm_i]
            for task_i, task in enumerate(tasks):
                score = pattern[condition][(topic_i + task_i) % 6]
                correct = 1 if score == 2 else 0
                confidence = 60 + 20 * correct + 5 * ((topic_i + task_i) % 3)
                seconds = 30 + 12 * task_i + 5 * ((topic_i + arm_i) % 4)
                seconds += 25 if condition == "A" else 0
                evidence = 1 if (
                    (condition == "C" and (task_i + arm_i) % 2 == 0)
                    or (condition in ("A", "B") and (topic_i + task_i) % 7 == 0)
                ) else 0
                would_cite = min(4, 2 + correct + (1 if condition == "C" else 0))
                rows.append(
                    {
                        "session_id": session_id,
                        "condition": condition,
                        "topic": topic,
                        "participant_code": participant,
                        "task": task,
                        "success_0_2": score,
                        "seconds": float(seconds),
                        "confidence_0_100": confidence,
                        "correct": correct,
                        "evidence_opened": evidence,
                        "would_cite_0_4": would_cite,
                        "notes": "SYNTHETIC self-test row; not a real participant.",
                    }
                )
    return rows


def _write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in COLUMNS})


def run_self_test():
    print("=" * 78)
    print("E1 ANALYSIS SELF-TEST")
    print("ALL DATA BELOW IS SYNTHETIC. It is generated by this script to exercise code")
    print("paths. It is not participant evidence and must never be reported as a result.")
    print("=" * 78)
    print("")

    checks = []
    with tempfile.TemporaryDirectory(prefix="e1-selftest-") as tmp:
        tmp_path = Path(tmp)
        fixture = tmp_path / "SYNTHETIC_sessions.csv"
        rows = _synthetic_rows()
        _write_csv(fixture, rows)
        expected_columns = set(COLUMNS)
        assert set(COLUMNS) == expected_columns

        raw, fmt, load_warnings = load_raw(fixture, "auto")
        assert fmt == "csv", fmt
        val_rows, errors, warnings, synthetic = validate(raw)
        if errors:
            print("VALIDATION ERRORS IN FIXTURE:")
            for error in errors:
                print("  -", error)
            raise AssertionError("synthetic fixture did not validate")
        assert len(val_rows) == 72, len(val_rows)
        assert len({r["session_id"] for r in val_rows}) == 18
        assert synthetic == 72, synthetic
        warnings = load_warnings + warnings

        report = build_report(
            val_rows,
            "SYNTHETIC_sessions.csv (generated fixture)",
            n_boot=1000,
            seed=DEFAULT_SEED,
            warnings=warnings,
            synthetic=synthetic,
        )
        assert "PRIMARY CONTRAST" in report
        assert "Bootstrap 95% CI" in report
        assert "WARNING: 72 row(s) are marked SYNTHETIC" in report
        print(report)
        print("")
        checks.append("fixture CSV: 72 rows / 18 sessions / 6 topics x 3 arms validated")
        checks.append("bootstrap interval computed (1000 resamples, synthetic)")
        checks.append("SYNTHETIC banner rendered")

        # Tiny data: one row per arm must not crash and must not invent an interval.
        tiny = tmp_path / "tiny.csv"
        _write_csv(
            tiny,
            [
                {
                    "session_id": "T1", "condition": "A", "topic": "tiny",
                    "participant_code": "P90", "task": "explain_1min",
                    "success_0_2": 1, "seconds": 40.0, "confidence_0_100": 70,
                    "correct": 0, "evidence_opened": 0, "would_cite_0_4": 2,
                    "notes": "SYNTHETIC tiny fixture",
                }
            ],
        )
        tiny_raw, _, _ = load_raw(tiny, "auto")
        tiny_rows, tiny_errors, tiny_warnings, tiny_syn = validate(tiny_raw)
        assert not tiny_errors, tiny_errors
        tiny_report = build_report(
            tiny_rows, "tiny.csv (SYNTHETIC)", n_boot=1000, seed=1,
            warnings=tiny_warnings, synthetic=tiny_syn,
        )
        assert "insufficient data" in tiny_report.lower(), tiny_report
        checks.append("tiny data (1 row): no crash, no bootstrap interval reported")

        # Empty header-only template.
        empty = tmp_path / "empty.csv"
        empty.write_text(",".join(COLUMNS) + "\n", encoding="utf-8")
        empty_raw, _, _ = load_raw(empty, "auto")
        empty_rows, empty_errors, empty_warnings, empty_syn = validate(empty_raw)
        assert not empty_errors, empty_errors
        empty_report = build_report(
            empty_rows, "empty.csv", warnings=empty_warnings, synthetic=empty_syn
        )
        assert "No task rows" in empty_report
        checks.append("empty template: no crash, explicit 'No task rows' message")

        # Invalid row: bad condition + PII-looking participant code must be caught.
        bad = tmp_path / "bad.csv"
        _write_csv(
            bad,
            [
                {
                    "session_id": "B1", "condition": "D", "topic": "x",
                    "participant_code": "person@example.com", "task": "unknown",
                    "success_0_2": 9, "seconds": -1, "confidence_0_100": 101,
                    "correct": 2, "evidence_opened": 3, "would_cite_0_4": 5,
                    "notes": "SYNTHETIC invalid fixture",
                }
            ],
        )
        bad_raw, _, _ = load_raw(bad, "auto")
        _, bad_errors, _, _ = validate(bad_raw)
        assert len(bad_errors) >= 6, bad_errors
        assert any("condition" in e for e in bad_errors)
        assert any("PII" in e for e in bad_errors)
        checks.append(f"invalid row: {len(bad_errors)} validation errors caught")

        # JSONL path.
        jsonl = tmp_path / "SYNTHETIC_sessions.jsonl"
        with jsonl.open("w", encoding="utf-8") as fh:
            for row in _synthetic_rows()[:8]:
                fh.write(json.dumps(row) + "\n")
        jsonl_raw, jsonl_fmt, _ = load_raw(jsonl, "auto")
        jsonl_rows, jsonl_errors, _, _ = validate(jsonl_raw)
        assert jsonl_fmt == "jsonl"
        assert not jsonl_errors, jsonl_errors
        assert len(jsonl_rows) == 8
        checks.append("JSONL input parsed and validated (8 synthetic rows)")

    print("SELF-TEST CHECKS")
    for check in checks:
        print(f"  PASS  {check}")
    print("")
    print("SELF-TEST PASSED (SYNTHETIC data only; no participant results).")
    return 0


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="E1 reader task analysis (stdlib only). Empty and tiny data are handled."
    )
    parser.add_argument(
        "path", nargs="?", default="sessions.csv",
        help="sessions CSV or JSONL (default: sessions.csv)",
    )
    parser.add_argument(
        "--format", choices=("auto", "csv", "jsonl"), default="auto",
        help="input format (default: infer from extension/content)",
    )
    parser.add_argument(
        "--bootstrap", type=int, default=DEFAULT_BOOTSTRAP,
        help=f"bootstrap resamples (default {DEFAULT_BOOTSTRAP}; minimum 100)",
    )
    parser.add_argument(
        "--seed", type=int, default=DEFAULT_SEED,
        help=f"bootstrap RNG seed (default {DEFAULT_SEED})",
    )
    parser.add_argument(
        "--self-test", action="store_true",
        help="run the built-in SYNTHETIC fixture and validation checks",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        try:
            return run_self_test()
        except AssertionError as exc:
            print(f"SELF-TEST FAILED: {exc}", file=sys.stderr)
            return 1

    if args.bootstrap < 100:
        print("error: --bootstrap must be >= 100", file=sys.stderr)
        return 2

    path = Path(args.path)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        print("Run `python3 analysis.py --self-test` to check the script itself.",
              file=sys.stderr)
        return 2

    try:
        raw, fmt, load_warnings = load_raw(path, args.format)
    except DataError as exc:
        print(f"DATA ERROR: {exc}", file=sys.stderr)
        return 2

    rows, errors, warnings, synthetic = validate(raw)
    warnings = load_warnings + warnings

    if errors:
        print(f"VALIDATION FAILED - {len(errors)} error(s), {len(warnings)} warning(s):",
              file=sys.stderr)
        for error in errors[:50]:
            print(f"  - {error}", file=sys.stderr)
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more", file=sys.stderr)
        print("Fix the data file; analysis was not run.", file=sys.stderr)
        return 1

    report = build_report(
        rows, str(path), n_boot=args.bootstrap, seed=args.seed,
        warnings=warnings, synthetic=synthetic,
    )
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
