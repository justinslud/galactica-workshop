#!/usr/bin/env python3
"""E4 correction-intake and triage-cost analysis.

Reads the 30-case file and the triage log, validates both, and prints cost, correctness,
SLA, inter-rater and threshold results.

This script never invents timings or dispositions. The case file shipped with this kit is
SYNTHETIC and is labelled as such. `--self-test` runs on additional generated SYNTHETIC data.

Usage:
    python3 analysis.py
    python3 analysis.py --cases cases.csv --log triage_log.csv --arm A
    python3 analysis.py --self-test

Stdlib only (Python 3.8+).
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import re
import statistics
import sys
import tempfile
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

CASE_COLUMNS = [
    "case_id",
    "category",
    "target_article_slug",
    "claim_text_or_section",
    "reporter_role",
    "message",
    "expected_disposition",
    "severity",
    "injected_at",
    "notes",
]

LOG_COLUMNS = [
    "case_id",
    "intake_option",
    "received_at",
    "first_response_at",
    "triaged_at",
    "resolved_at",
    "minutes_to_triage",
    "minutes_to_resolve",
    "disposition",
    "correct_0_1",
    "reviewer_code",
    "second_reviewer_code",
    "second_disposition",
    "notes",
]

EXPECTED_MIX = {
    "valid": 10,
    "wrong": 10,
    "duplicate": 5,
    "legal_privacy_coi": 5,
}
CATEGORY_EXPECTED = {
    "valid": "accepted",
    "wrong": "rejected",
    "duplicate": "duplicate",
}
CATEGORIES = tuple(EXPECTED_MIX)
DISPOSITIONS = ("accepted", "rejected", "duplicate", "needs_info")
SEVERITIES = ("low", "medium", "high", "critical")
ROLES = {"reader", "researcher", "subject", "representative", "organization", "anonymous"}
INTAKE_OPTIONS = ("A", "B", "C")
DEMO_SLUGS = {"subvocal-interfaces", "quadratic-funding", "encyclopedia-galactica"}
THRESHOLD_MINUTES = 15.0
MIN_CASES_FOR_THRESHOLD = 10
CODE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{1,23}$")
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
PHONE_RE = re.compile(r"\d[\d\s().+-]{6,}\d")
DEFAULT_BOOTSTRAP = 2000
DEFAULT_SEED = 20261105


class DataError(Exception):
    """Fatal problem with a file (not a per-row validation error)."""


# --------------------------------------------------------------------------------------
# Loading and parsing
# --------------------------------------------------------------------------------------


def _text(value) -> str:
    return "" if value is None else str(value).strip()


def parse_dt(text, field, line_no, errors, warnings):
    text = _text(text)
    if not text:
        errors.append(f"line {line_no}: {field} is empty")
        return None
    raw = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        value = datetime.fromisoformat(raw)
    except ValueError:
        errors.append(
            f"line {line_no}: {field}={text!r} is not an ISO 8601 timestamp "
            "(e.g. 2026-11-09T09:10:00-05:00)"
        )
        return None
    if value.tzinfo is None:
        warnings.append(
            f"line {line_no}: {field} has no timezone offset; assumed UTC "
            f"({text}). Record offsets to avoid ambiguity."
        )
        value = value.replace(tzinfo=timezone.utc)
    return value


def load_csv(path: Path, required_columns):
    if not path.exists():
        raise DataError(f"file not found: {path}")
    try:
        with path.open(newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                raise DataError(f"{path} has no header row")
            fields = [(f or "").strip() for f in reader.fieldnames]
            missing = [c for c in required_columns if c not in fields]
            if missing:
                raise DataError(
                    f"{path} is missing required column(s): " + ", ".join(missing)
                )
            extra = [f for f in fields if f not in required_columns]
            raw = []
            for line_no, row in enumerate(reader, start=2):
                if not any((v or "").strip() for v in row.values() if v is not None):
                    continue
                raw.append((line_no, {(k or "").strip(): v for k, v in row.items()}))
            return raw, extra
    except OSError as exc:
        raise DataError(f"cannot read {path}: {exc}") from exc


# --------------------------------------------------------------------------------------
# Case validation
# --------------------------------------------------------------------------------------


def validate_cases(raw_rows):
    cases = []
    errors = []
    warnings = []
    seen_ids = set()

    for line_no, raw in raw_rows:
        before = len(errors)
        case_id = _text(raw.get("case_id"))
        if not case_id:
            errors.append(f"line {line_no}: case_id is empty")
        elif not re.match(r"^[A-Za-z0-9_-]{1,16}$", case_id):
            errors.append(
                f"line {line_no}: case_id={case_id!r} must be 1-16 letters/digits/_/-"
            )
        elif case_id in seen_ids:
            errors.append(f"line {line_no}: duplicate case_id {case_id}")
        seen_ids.add(case_id)

        category = _text(raw.get("category")).lower()
        if category not in EXPECTED_MIX:
            errors.append(
                f"line {line_no}: category={category!r} is not one of "
                + ", ".join(CATEGORIES)
            )

        slug = _text(raw.get("target_article_slug"))
        if not slug:
            errors.append(f"line {line_no}: target_article_slug is empty")
        elif slug not in DEMO_SLUGS:
            warnings.append(
                f"line {line_no}: target_article_slug={slug!r} is not one of the "
                "seeded demo slugs; confirm the article exists"
            )

        claim = _text(raw.get("claim_text_or_section"))
        if not claim:
            errors.append(f"line {line_no}: claim_text_or_section is empty")

        reporter_role = _text(raw.get("reporter_role")).lower()
        if reporter_role not in ROLES:
            errors.append(
                f"line {line_no}: reporter_role={reporter_role!r} is not one of "
                + ", ".join(sorted(ROLES))
            )

        message = _text(raw.get("message"))
        if not message:
            errors.append(f"line {line_no}: message is empty")

        expected = _text(raw.get("expected_disposition")).lower()
        if expected not in DISPOSITIONS:
            errors.append(
                f"line {line_no}: expected_disposition={expected!r} is not one of "
                + ", ".join(DISPOSITIONS)
            )

        severity = _text(raw.get("severity")).lower()
        if severity not in SEVERITIES:
            errors.append(
                f"line {line_no}: severity={severity!r} is not one of "
                + ", ".join(SEVERITIES)
            )

        injected_at = parse_dt(
            raw.get("injected_at"), "injected_at", line_no, errors, warnings
        )
        notes = _text(raw.get("notes"))

        if len(errors) > before:
            continue

        if category in CATEGORY_EXPECTED and expected != CATEGORY_EXPECTED[category]:
            errors.append(
                f"line {line_no}: category {category} expects disposition "
                f"{CATEGORY_EXPECTED[category]!r}, got {expected!r}"
            )
        if category == "legal_privacy_coi" and severity not in ("high", "critical"):
            errors.append(
                f"line {line_no}: legal/privacy/COI case must be high or critical, "
                f"got {severity!r}"
            )

        cases.append(
            {
                "case_id": case_id,
                "category": category,
                "target_article_slug": slug,
                "claim_text_or_section": claim,
                "reporter_role": reporter_role,
                "message": message,
                "expected_disposition": expected,
                "severity": severity,
                "injected_at": injected_at,
                "notes": notes,
                "line_no": line_no,
            }
        )

    # Mix counts are checked on the rows that validated.
    if len(cases) != 30:
        errors.append(f"expected 30 cases, found {len(cases)}")
    counts = Counter(c["category"] for c in cases)
    for category, expected_count in EXPECTED_MIX.items():
        if counts.get(category, 0) != expected_count:
            errors.append(
                f"case mix: category {category} has {counts.get(category, 0)} "
                f"row(s), expected {expected_count}"
            )

    if cases:
        by_id = {c["case_id"]: c for c in cases}
        by_date = Counter(c["injected_at"].date() for c in cases)
        for day, count in sorted(by_date.items()):
            if day.weekday() >= 5:
                warnings.append(
                    f"injected_at falls on a weekend ({day.isoformat()}); "
                    "the planned schedule uses business days"
                )
            if count > 4:
                warnings.append(
                    f"{count} cases injected on {day.isoformat()}; that is a burst"
                )
        for case in cases:
            match = re.search(r"cluster\s+(C\d{2})", case["notes"], re.IGNORECASE)
            if case["category"] == "duplicate" and not match:
                warnings.append(
                    f"{case['case_id']}: duplicate case has no 'cluster Cxx' parent "
                    "reference in notes; check the duplicate pairing"
                )
            if case["category"] == "duplicate" and match:
                parent_id = match.group(1).upper()
                parent = by_id.get(parent_id)
                if parent is None:
                    warnings.append(
                        f"{case['case_id']}: duplicate notes reference {parent_id}, "
                        "which is not in the case set"
                    )
                elif parent["injected_at"] >= case["injected_at"]:
                    warnings.append(
                        f"{case['case_id']}: duplicate of {parent_id} but injected "
                        "before or at the same time as its parent"
                    )
            if not case["notes"]:
                warnings.append(
                    f"{case['case_id']}: notes are empty; every case should state "
                    "SYNTHETIC and its expected reasoning"
                )

    synthetic = sum(1 for c in cases if "synthetic" in c["notes"].lower())
    return cases, errors, warnings, synthetic


# --------------------------------------------------------------------------------------
# Log validation
# --------------------------------------------------------------------------------------


def _optional_minutes(value):
    text = _text(value)
    if text == "":
        return None
    return float(text)


def validate_log(raw_rows, cases_by_id):
    entries = []
    errors = []
    warnings = []
    seen = set()

    for line_no, raw in raw_rows:
        before = len(errors)
        case_id = _text(raw.get("case_id"))
        if not case_id:
            errors.append(f"line {line_no}: case_id is empty")
        elif case_id not in cases_by_id:
            errors.append(f"line {line_no}: case_id={case_id!r} is not in the case file")

        option = _text(raw.get("intake_option")).upper()
        if option not in INTAKE_OPTIONS:
            errors.append(
                f"line {line_no}: intake_option={option!r} is not one of A, B, C"
            )

        received = parse_dt(
            raw.get("received_at"), "received_at", line_no, errors, warnings
        )
        first_response = parse_dt(
            raw.get("first_response_at"), "first_response_at", line_no, errors, warnings
        ) if _text(raw.get("first_response_at")) else None
        triaged = parse_dt(
            raw.get("triaged_at"), "triaged_at", line_no, errors, warnings
        ) if _text(raw.get("triaged_at")) else None
        resolved = parse_dt(
            raw.get("resolved_at"), "resolved_at", line_no, errors, warnings
        ) if _text(raw.get("resolved_at")) else None

        disposition = _text(raw.get("disposition")).lower()
        if disposition and disposition not in DISPOSITIONS:
            errors.append(
                f"line {line_no}: disposition={disposition!r} is not one of "
                + ", ".join(DISPOSITIONS)
            )
        if triaged and not disposition:
            errors.append(
                f"line {line_no}: triaged_at is set but disposition is empty"
            )
        if disposition and not triaged:
            errors.append(
                f"line {line_no}: disposition is set but triaged_at is empty"
            )
        if resolved and not triaged:
            errors.append(
                f"line {line_no}: resolved_at is set but triaged_at is empty"
            )

        reviewer = _text(raw.get("reviewer_code"))
        if not reviewer:
            errors.append(f"line {line_no}: reviewer_code is empty")
        elif not CODE_RE.match(reviewer):
            errors.append(
                f"line {line_no}: reviewer_code={reviewer!r} must be a short code "
                "like R1"
            )
        if EMAIL_RE.search(reviewer) or PHONE_RE.search(reviewer):
            errors.append(
                f"line {line_no}: reviewer_code looks like PII; use a code such as R1"
            )

        second_reviewer = _text(raw.get("second_reviewer_code"))
        second_disposition = _text(raw.get("second_disposition")).lower()
        if bool(second_reviewer) != bool(second_disposition):
            errors.append(
                f"line {line_no}: second_reviewer_code and second_disposition must "
                "both be set or both be empty"
            )
        if second_disposition and second_disposition not in DISPOSITIONS:
            errors.append(
                f"line {line_no}: second_disposition={second_disposition!r} is "
                "invalid"
            )
        if second_reviewer and not CODE_RE.match(second_reviewer):
            errors.append(
                f"line {line_no}: second_reviewer_code={second_reviewer!r} must be "
                "a short code"
            )

        if len(errors) > before:
            continue

        key = (case_id, option)
        if key in seen:
            errors.append(
                f"line {line_no}: duplicate log row for {case_id} under arm {option}"
            )
            continue
        seen.add(key)

        # Timestamp ordering (a partial row may stop at any stage).
        timeline = [value for value in (received, first_response, triaged, resolved)
                    if value is not None]
        if any(b < a for a, b in zip(timeline, timeline[1:])):
            errors.append(
                f"line {line_no}: timestamps are out of order "
                "(received <= first_response <= triaged <= resolved)"
            )
            continue

        # Minutes are derived when blank, checked when provided.
        computed_triage = (
            (triaged - received).total_seconds() / 60.0 if triaged else None
        )
        computed_resolve = (
            (resolved - received).total_seconds() / 60.0 if resolved else None
        )
        provided_triage = None
        try:
            provided_triage = _optional_minutes(raw.get("minutes_to_triage"))
        except ValueError:
            errors.append(
                f"line {line_no}: minutes_to_triage must be numeric or empty"
            )
        provided_resolve = None
        try:
            provided_resolve = _optional_minutes(raw.get("minutes_to_resolve"))
        except ValueError:
            errors.append(
                f"line {line_no}: minutes_to_resolve must be numeric or empty"
            )
        for field, provided, computed in (
            ("minutes_to_triage", provided_triage, computed_triage),
            ("minutes_to_resolve", provided_resolve, computed_resolve),
        ):
            if provided is not None and provided < 0:
                errors.append(f"line {line_no}: {field} must be >= 0")
            elif provided is not None and computed is not None and abs(provided - computed) > 2:
                warnings.append(
                    f"line {line_no}: {field}={provided:.1f} disagrees with the "
                    f"timestamps ({computed:.1f}); timestamps are authoritative"
                )
        if provided_triage is None:
            provided_triage = computed_triage
        if provided_resolve is None:
            provided_resolve = computed_resolve

        correct_flag = None
        raw_correct = _text(raw.get("correct_0_1"))
        if raw_correct:
            try:
                correct_flag = int(raw_correct)
            except ValueError:
                errors.append(
                    f"line {line_no}: correct_0_1 must be 0 or 1 or empty"
                )
            else:
                if correct_flag not in (0, 1):
                    errors.append(
                        f"line {line_no}: correct_0_1 must be 0 or 1 or empty"
                    )
        if len(errors) > before:
            continue

        case = cases_by_id[case_id]
        computed_correct = int(disposition == case["expected_disposition"]) if disposition else None
        if correct_flag is not None and computed_correct is not None and correct_flag != computed_correct:
            warnings.append(
                f"line {line_no}: correct_0_1={correct_flag} but disposition "
                f"{disposition!r} vs expected {case['expected_disposition']!r} "
                f"implies {computed_correct}"
            )

        entries.append(
            {
                "case_id": case_id,
                "intake_option": option,
                "received_at": received,
                "first_response_at": first_response,
                "triaged_at": triaged,
                "resolved_at": resolved,
                "minutes_to_triage": provided_triage,
                "minutes_to_resolve": provided_resolve,
                "disposition": disposition or None,
                "correct_0_1": correct_flag,
                "reviewer_code": reviewer,
                "second_reviewer_code": second_reviewer or None,
                "second_disposition": second_disposition or None,
                "notes": _text(raw.get("notes")),
                "case": case,
                "line_no": line_no,
            }
        )

    pairs = [e for e in entries if e["second_disposition"]]
    if pairs and len(pairs) < 10:
        warnings.append(
            f"inter-rater subset has {len(pairs)} pair(s); target is 10 "
            "(3 valid, 3 wrong, 2 duplicate, 2 legal/privacy/COI)"
        )
    return entries, errors, warnings


# --------------------------------------------------------------------------------------
# Statistics helpers
# --------------------------------------------------------------------------------------


def _mean(values):
    return sum(values) / len(values) if values else None


def _median(values):
    return statistics.median(values) if values else None


def _p90(values):
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(math.ceil(0.9 * len(ordered))) - 1)
    return ordered[index]


def percentile(values, q):
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


def bootstrap_median_ci(values, n_boot=DEFAULT_BOOTSTRAP, seed=DEFAULT_SEED):
    if len(values) < 2:
        return None
    rng = random.Random(seed)
    medians = [
        statistics.median([values[rng.randrange(len(values))] for _ in range(len(values))])
        for _ in range(n_boot)
    ]
    return percentile(medians, 0.025), percentile(medians, 0.975)


def cohen_kappa(pairs):
    """pairs = [(first, second), ...]; returns (n, observed_agreement, kappa)."""
    n = len(pairs)
    if n == 0:
        return 0, None, None
    observed = sum(1 for a, b in pairs if a == b) / n
    first_counts = Counter(a for a, _ in pairs)
    second_counts = Counter(b for _, b in pairs)
    expected = sum(
        (first_counts[d] / n) * (second_counts[d] / n) for d in DISPOSITIONS
    )
    if expected >= 1:
        kappa = 1.0
    else:
        kappa = (observed - expected) / (1 - expected)
    return n, observed, kappa


def business_days_between(start, end):
    """Weekdays strictly after start's date through end's date (no holidays)."""
    if end < start:
        return -1
    days = 0
    cursor = start.date()
    while cursor < end.date():
        cursor += timedelta(days=1)
        if cursor.weekday() < 5:
            days += 1
    return days


def threshold_status(triage_values, min_cases=MIN_CASES_FOR_THRESHOLD,
                     threshold=THRESHOLD_MINUTES):
    if len(triage_values) < min_cases:
        return "UNDETERMINED", _median(triage_values), len(triage_values)
    median = statistics.median(triage_values)
    return ("CROSSED" if median > threshold else "NOT CROSSED", median,
            len(triage_values))


def _fmt(value, digits=1):
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def _pct(value, digits=1):
    if value is None:
        return "-"
    return f"{value * 100:.{digits}f}%"


# --------------------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------------------


def compute_option_metrics(entries, cutoff):
    triaged = [e for e in entries if e["disposition"]]
    resolved = [e for e in entries if e["resolved_at"]]
    open_entries = [e for e in entries if not e["resolved_at"]]
    triage_minutes = [e["minutes_to_triage"] for e in triaged
                      if e["minutes_to_triage"] is not None]
    resolve_minutes = [e["minutes_to_resolve"] for e in resolved
                       if e["minutes_to_resolve"] is not None]
    first_response_minutes = [
        (e["first_response_at"] - e["received_at"]).total_seconds() / 60.0
        for e in entries if e["first_response_at"]
    ]
    open_ages_hours = [
        (cutoff - e["received_at"]).total_seconds() / 3600.0 for e in open_entries
    ]
    correct = [e for e in triaged
               if e["disposition"] == e["case"]["expected_disposition"]]
    expected_non_accept = [e for e in triaged
                           if e["case"]["expected_disposition"] != "accepted"]
    expected_accept = [e for e in triaged
                       if e["case"]["expected_disposition"] == "accepted"]
    false_accepts = [e for e in expected_non_accept if e["disposition"] == "accepted"]
    false_rejects = [e for e in expected_accept if e["disposition"] == "rejected"]

    intake_lags = [
        (e["received_at"] - e["case"]["injected_at"]).total_seconds() / 60.0
        for e in entries
    ]
    return {
        "n": len(entries),
        "n_triaged": len(triaged),
        "intake_lag_median": _median(intake_lags),
        "intake_lag_mean": _mean(intake_lags),
        "n_resolved": len(resolved),
        "n_open": len(open_entries),
        "triage_median": _median(triage_minutes),
        "triage_mean": _mean(triage_minutes),
        "triage_p90": _p90(triage_minutes),
        "triage_max": max(triage_minutes) if triage_minutes else None,
        "triage_values": triage_minutes,
        "first_response_median": _median(first_response_minutes),
        "first_response_mean": _mean(first_response_minutes),
        "resolve_median": _median(resolve_minutes),
        "resolve_mean": _mean(resolve_minutes),
        "correct_k": len(correct),
        "correct_rate": (len(correct) / len(triaged)) if triaged else None,
        "false_accept_k": len(false_accepts),
        "false_accept_denominator": len(expected_non_accept),
        "false_accept_rate": (
            len(false_accepts) / len(expected_non_accept)
            if expected_non_accept else None
        ),
        "false_reject_k": len(false_rejects),
        "false_reject_denominator": len(expected_accept),
        "false_reject_rate": (
            len(false_rejects) / len(expected_accept) if expected_accept else None
        ),
        "oldest_open_hours": max(open_ages_hours) if open_ages_hours else None,
        "dispositions": Counter(e["disposition"] for e in triaged),
        "sla": sla_report(entries),
    }


def sla_report(entries):
    triaged = [e for e in entries if e["disposition"]]
    ack_misses = []
    resolution_misses = []
    legal_misses = []
    for e in entries:
        if e["first_response_at"]:
            days = business_days_between(e["received_at"], e["first_response_at"])
            if days > 2:
                ack_misses.append((e["case_id"], days))
        if e["resolved_at"]:
            days = (e["resolved_at"] - e["received_at"]).total_seconds() / 86400.0
            if days > 14:
                resolution_misses.append((e["case_id"], days))
        if e["case"]["category"] == "legal_privacy_coi" and e["first_response_at"]:
            hours = (e["first_response_at"] - e["received_at"]).total_seconds() / 3600.0
            if hours > 24:
                legal_misses.append((e["case_id"], hours))
    return {
        "ack_misses": ack_misses,
        "resolution_misses": resolution_misses,
        "legal_misses": legal_misses,
        "n_triaged": len(triaged),
    }


def compute_metrics(entries, cutoff):
    overall = compute_option_metrics(entries, cutoff)
    by_option = {}
    for option in INTAKE_OPTIONS:
        subset = [e for e in entries if e["intake_option"] == option]
        if subset:
            by_option[option] = compute_option_metrics(subset, cutoff)
    return {"overall": overall, "by_option": by_option}


def confusion_matrix(entries):
    expected_order = ("accepted", "rejected", "duplicate", "needs_info")
    observed_order = DISPOSITIONS + ("open",)
    matrix = {exp: {obs: 0 for obs in observed_order} for exp in expected_order}
    for e in entries:
        exp = e["case"]["expected_disposition"]
        obs = e["disposition"] or "open"
        matrix[exp][obs] += 1
    return matrix, expected_order, observed_order


# --------------------------------------------------------------------------------------
# Self-test fixtures (SYNTHETIC only)
# --------------------------------------------------------------------------------------


def _fixture_cases():
    """30 SYNTHETIC cases matching the required 10/10/5/5 mix."""
    start = date(2026, 11, 9)
    business_days = []
    cursor = start
    while len(business_days) < 10:
        if cursor.weekday() < 5:
            business_days.append(cursor)
        cursor += timedelta(days=1)
    cases = []
    for index in range(1, 31):
        if index <= 10:
            category, expected, severity = "valid", "accepted", "medium"
        elif index <= 20:
            category, expected, severity = "wrong", "rejected", "low"
        elif index <= 25:
            category, expected, severity = "duplicate", "duplicate", "low"
        else:
            category, expected, severity = "legal_privacy_coi", "needs_info", "critical"
        cases.append(
            {
                "case_id": f"C{index:02d}",
                "category": category,
                "target_article_slug": "subvocal-interfaces",
                "claim_text_or_section": f"SYNTHETIC fixture claim {index}",
                "reporter_role": "reader",
                "message": f"SYNTHETIC fixture message {index}",
                "expected_disposition": expected,
                "severity": severity,
                "injected_at": datetime(
                    business_days[(index - 1) // 3].year,
                    business_days[(index - 1) // 3].month,
                    business_days[(index - 1) // 3].day,
                    9 + 2 * ((index - 1) % 3), 0, tzinfo=timezone.utc,
                ),
                "notes": (
                    f"SYNTHETIC self-test case; expected duplicate cluster "
                    f"C{index - 20:02d}."
                    if category == "duplicate"
                    else "SYNTHETIC self-test case; not a real report."
                ),
            }
        )
    return cases


def _fixture_log(cases, triage_minutes):
    """30 log rows under arm A; `triage_minutes` maps index -> minutes."""
    rows = []
    pair_indices = {1, 2, 3, 11, 12, 13, 21, 22, 26, 27}
    for index, case in enumerate(cases, start=1):
        received = case["injected_at"] + timedelta(minutes=5)
        minutes = triage_minutes(index)
        first_response = received + timedelta(minutes=max(5, minutes / 3))
        triaged = received + timedelta(minutes=minutes)
        resolved = triaged + timedelta(minutes=60)
        correct = 1 if (case["category"] != "wrong" or index % 2 == 0) else 0
        # Keep dispositions plausible but deliberately not perfect: a few
        # wrong/duplicate cases are accepted to exercise false-accept logic.
        if case["category"] == "valid":
            disposition = "accepted"
            correct = 1
        elif case["category"] == "duplicate":
            disposition = "duplicate" if index % 2 == 0 else "accepted"
            correct = 1 if disposition == "duplicate" else 0
        elif case["category"] == "legal_privacy_coi":
            disposition = "needs_info" if index != 30 else "accepted"
            correct = 1 if disposition == "needs_info" else 0
        else:
            disposition = "rejected" if index % 2 == 0 else "accepted"
            correct = 1 if disposition == "rejected" else 0
        rows.append(
            {
                "case_id": case["case_id"],
                "intake_option": "A",
                "received_at": received,
                "first_response_at": first_response,
                "triaged_at": triaged,
                "resolved_at": resolved,
                "minutes_to_triage": minutes,
                "minutes_to_resolve": minutes + 60,
                "disposition": disposition,
                "correct_0_1": correct,
                "reviewer_code": "R1",
                "second_reviewer_code": "R2" if index in pair_indices else None,
                "second_disposition": (
                    disposition if index % 3 != 0 else
                    ("needs_info" if disposition != "needs_info" else "accepted")
                ) if index in pair_indices else None,
                "notes": "SYNTHETIC self-test log row.",
            }
        )
    return rows


# --------------------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------------------


def build_report(cases, entries, warnings, cutoff, n_boot=DEFAULT_BOOTSTRAP,
                 seed=DEFAULT_SEED, arm="A", threshold=THRESHOLD_MINUTES,
                 min_cases=MIN_CASES_FOR_THRESHOLD):
    lines = []
    add = lines.append
    add("E4 - CORRECTION INTAKE AND TRIAGE COST")
    add(f"Cases: {len(cases)}  |  Log entries: {len(entries)}  |  "
        f"Primary arm: {arm}  |  Threshold: > {threshold:g} min median triage")
    add(f"Analysis cutoff for open cases: {cutoff.isoformat(timespec='minutes')}")
    add("")

    synthetic_cases = sum(1 for c in cases if "synthetic" in c["notes"].lower())
    if synthetic_cases:
        add("!" * 78)
        add(f"NOTE: {synthetic_cases}/{len(cases)} cases are marked SYNTHETIC "
            "(fictional role-play).")
        add("Results describe this fixture, not real corrections or real reporters.")
        add("!" * 78)
        add("")

    add("CASE MIX (validated against the pre-registered 10/10/5/5)")
    counts = Counter(c["category"] for c in cases)
    add(f"  {'Category':<20}{'Cases':>7}{'Expected':>12}   Severities")
    for category in CATEGORIES:
        severities = Counter(c["severity"] for c in cases if c["category"] == category)
        exp = EXPECTED_MIX[category]
        add(f"  {category:<20}{counts.get(category, 0):>7}{exp:>12}   "
            + ", ".join(f"{k}={v}" for k, v in sorted(severities.items())))
    add("")

    if not entries:
        add("No triage entries found. The template is empty, so there is no cost data.")
        add("This is the expected state before any corrections have been injected.")
        add("")
        add("E4 THRESHOLD: UNDETERMINED (0 logged; minimum "
            f"{min_cases} for a decision)")
        add("")
        add("Reporter satisfaction: not recorded in triage_log.csv; do not impute it.")
        return "\n".join(lines)

    metrics = compute_metrics(entries, cutoff)
    overall = metrics["overall"]
    primary = metrics["by_option"].get(arm)

    add("COST AND THROUGHPUT")
    add(f"  {'Arm':<4}{'Cases':>7}{'Triaged':>9}{'Median triage':>15}"
        f"{'Mean':>9}{'p90':>9}{'Median 1st resp':>17}{'Median resolve':>16}")
    for option in sorted(metrics["by_option"]):
        m = metrics["by_option"][option]
        add(f"  {option:<4}{m['n']:>7}{m['n_triaged']:>9}"
            f"{_fmt(m['triage_median']):>15}{_fmt(m['triage_mean']):>9}"
            f"{_fmt(m['triage_p90']):>9}{_fmt(m['first_response_median']):>17}"
            f"{_fmt(m['resolve_median']):>16}")
    add(f"  {'All':<4}{overall['n']:>7}{overall['n_triaged']:>9}"
        f"{_fmt(overall['triage_median']):>15}{_fmt(overall['triage_mean']):>9}"
        f"{_fmt(overall['triage_p90']):>9}{_fmt(overall['first_response_median']):>17}"
        f"{_fmt(overall['resolve_median']):>16}")
    add("  Minutes are measured from received_at (inbox arrival), not injected_at.")
    add("")

    add("QUEUE AGE AND OPEN CASES")
    add(f"  Logged: {overall['n']}  |  Triaged: {overall['n_triaged']}  |  "
        f"Resolved: {overall['n_resolved']}  |  Open: {overall['n_open']}")
    add(f"  Median wait to first response: {_fmt(overall['first_response_median'])} min")
    add(f"  Median intake lag (injected -> received): "
        f"{_fmt(overall['intake_lag_median'])} min")
    add(f"  Oldest open case at cutoff: {_fmt(overall['oldest_open_hours'], 1)} h")
    for option in sorted(metrics["by_option"]):
        m = metrics["by_option"][option]
        add(f"  Arm {option}: open={m['n_open']}, oldest open "
            f"{_fmt(m['oldest_open_hours'], 1)} h")
    add("")

    add("CORRECTNESS OF DISPOSITION (observed vs expected)")
    add(f"  Exact match: {overall['correct_k']}/{overall['n_triaged']} "
        f"({_pct(overall['correct_rate'])})")
    add(f"  False accepts: {overall['false_accept_k']}/"
        f"{overall['false_accept_denominator']} "
        f"({_pct(overall['false_accept_rate'])}) of cases that should not be accepted")
    add(f"  False rejects: {overall['false_reject_k']}/"
        f"{overall['false_reject_denominator']} "
        f"({_pct(overall['false_reject_rate'])}) of cases that should be accepted")
    add("")
    matrix, expected_order, observed_order = confusion_matrix(entries)
    header = "  Expected \\ Observed"
    add(f"{header:<24}" + "".join(f"{obs:>11}" for obs in observed_order))
    for expected in expected_order:
        row = f"  {expected:<22}" + "".join(
            f"{matrix[expected][obs]:>11}" for obs in observed_order
        )
        add(row)
    add("")

    add("PER-CATEGORY CORRECTNESS")
    for category in CATEGORIES:
        category_entries = [e for e in entries
                            if e["case"]["category"] == category and e["disposition"]]
        if not category_entries:
            add(f"  {category:<20} no triaged cases")
            continue
        correct = sum(
            1 for e in category_entries
            if e["disposition"] == e["case"]["expected_disposition"]
        )
        add(f"  {category:<20} {correct}/{len(category_entries)} "
            f"({_pct(correct / len(category_entries))})")
    add("")

    add("E4 DECISION THRESHOLD")
    primary_metrics = metrics["by_option"].get(arm)
    if primary_metrics is None:
        add(f"  Arm {arm} has no logged cases. E4 THRESHOLD: UNDETERMINED")
    else:
        status, median, n = threshold_status(
            primary_metrics["triage_values"], min_cases, threshold
        )
        add(f"  Arm {arm}: median triage {_fmt(median)} min over {n} triaged case(s); "
            f"threshold > {threshold:g} min.")
        add(f"  E4 THRESHOLD: {status}")
        if status == "CROSSED":
            add("  ACTION (E4): add structured claim linking and canned responses "
                "before public beta.")
        elif status == "NOT CROSSED":
            add("  ACTION (E4): simple form + manual triage is defensible for launch; "
                "keep measuring.")
        else:
            add(f"  ACTION: collect at least {min_cases} triaged cases "
                "in the primary arm before deciding.")
    if len(metrics["by_option"]) == 1:
        add("  NOTE: only one intake arm has data; this is not an A/B/C comparison.")
    add("")

    add("SLA CHECK (spec starting points: ack 2 business days, resolve 14 days, "
        "legal 24 h)")
    sla = overall["sla"]
    add(f"  Acknowledgment misses (>2 business days): {len(sla['ack_misses'])}"
        + (f" {sla['ack_misses']}" if sla["ack_misses"] else ""))
    add(f"  Resolution misses (>14 days): {len(sla['resolution_misses'])}"
        + (f" {sla['resolution_misses']}" if sla["resolution_misses"] else ""))
    add(f"  Legal/privacy first-response misses (>24 h): {len(sla['legal_misses'])}"
        + (f" {sla['legal_misses']}" if sla["legal_misses"] else ""))
    add("")

    add("INTER-RATER SUBSET")
    pairs = [
        (e["disposition"], e["second_disposition"])
        for e in entries
        if e["disposition"] and e["second_disposition"]
    ]
    n_pairs, observed, kappa = cohen_kappa(pairs)
    if n_pairs == 0:
        add("  No double-triaged cases recorded.")
    else:
        add(f"  Pairs: {n_pairs}  |  Raw agreement: {_pct(observed)}  |  "
            f"Cohen's kappa: {_fmt(kappa, 2)}")
        if n_pairs < 10:
            add("  Fewer than 10 pairs: descriptive only (protocol target is 10).")
        elif kappa is not None and kappa < 0.4:
            add("  Kappa < 0.4: the disposition rubric is not decision-grade; "
                "revise it before using the cost numbers.")
        elif kappa is not None and kappa < 0.6:
            add("  Kappa is below the 0.6 target: use the cost numbers cautiously.")
    add("")

    add("STABILITY CHECK (first half vs second half, ordered by received_at)")
    ordered = sorted(entries, key=lambda e: e["received_at"])
    half = len(ordered) // 2
    first_half = [e["minutes_to_triage"] for e in ordered[:half]
                  if e["minutes_to_triage"] is not None]
    second_half = [e["minutes_to_triage"] for e in ordered[half:]
                   if e["minutes_to_triage"] is not None]
    if len(first_half) >= 2 and len(second_half) >= 2:
        m1, m2 = statistics.median(first_half), statistics.median(second_half)
        diff_pct = abs(m1 - m2) / max(1.0, (m1 + m2) / 2) * 100
        ci = bootstrap_median_ci(overall["triage_values"], n_boot=n_boot, seed=seed)
        width = (ci[1] - ci[0]) if ci else None
        stable = diff_pct <= 20 and (width is not None and width < 10)
        add(f"  First half median {m1:.1f} min; second half {m2:.1f} min; "
            f"difference {diff_pct:.1f}%.")
        add(f"  Median triage bootstrap 95% CI: "
            f"[{_fmt(ci[0]) if ci else '-'}, {_fmt(ci[1]) if ci else '-'}] min"
            f" (width {_fmt(width) if width is not None else '-'} min).")
        add(f"  STABILITY: {'STABLE by the protocol rule' if stable else 'NOT YET STABLE'}"
            " (rule: medians within 20% and CI width < 10 min).")
    else:
        add("  Not enough triaged cases for a split-half check.")
    add("")

    add("REPORTER SATISFACTION")
    add("  Not recorded in triage_log.csv and never imputed. The synthetic run cannot")
    add("  measure satisfaction; collect it from consenting real reporters separately.")
    add("")

    if warnings:
        add(f"VALIDATION WARNINGS ({len(warnings)})")
        for warning in warnings:
            add(f"  - {warning}")
        add("")

    add("READING GUARD")
    add("  * These are descriptive statistics over a small synthetic/role-play sample.")
    add("  * The decision rule is the 15-minute median triage threshold from E4; see "
        "PROTOCOL.md sections 8-10.")
    add("  * Do not report these numbers as real correction demand or capacity.")
    add("  * Queue age and SLA depend on a realistic working day; batching invalidates them.")
    return "\n".join(lines)


# --------------------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------------------


def run_self_test():
    print("=" * 78)
    print("E4 ANALYSIS SELF-TEST")
    print("ALL DATA BELOW IS SYNTHETIC. It is generated by this script to exercise")
    print("code paths. It is not real correction data and must never be reported as")
    print("a result about readers, reporters or the product.")
    print("=" * 78)
    print("")

    checks = []
    cutoff = datetime(2026, 11, 21, 17, 0, tzinfo=timezone.utc)
    cases = _fixture_cases()
    cases_by_id = {c["case_id"]: c for c in cases}

    # 1. Case-file validation: the fixture should be valid and marked SYNTHETIC.
    raw_cases = [(i + 2, c) for i, c in enumerate(cases)]
    valid_cases, case_errors, case_warnings, synthetic = validate_cases(raw_cases)
    assert not case_errors, case_errors
    assert len(valid_cases) == 30
    assert synthetic == 30
    checks.append("case file: 30 SYNTHETIC cases, mix 10/10/5/5 validated")

    # 2. Slow log (median > 15 min): threshold CROSSED.
    slow_log = _fixture_log(cases, lambda i: 12 + (i % 11))
    slow_entries, slow_errors, slow_warnings = validate_log(
        [(i + 2, r) for i, r in enumerate(slow_log)], cases_by_id
    )
    assert not slow_errors, slow_errors
    slow_cutoff = cutoff
    slow_report = build_report(
        valid_cases, slow_entries, case_warnings + slow_warnings, slow_cutoff,
        n_boot=1000, seed=DEFAULT_SEED, arm="A",
    )
    assert "E4 THRESHOLD: CROSSED" in slow_report, slow_report
    assert "False accepts" in slow_report
    assert "Cohen's kappa" in slow_report
    checks.append("slow fixture: threshold CROSSED (>15 min median), report rendered")
    print(slow_report)
    print("")

    # 3. Fast log (median < 15 min): threshold NOT CROSSED.
    fast_log = _fixture_log(cases, lambda i: 5 + (i % 4))
    fast_entries, fast_errors, _ = validate_log(
        [(i + 2, r) for i, r in enumerate(fast_log)], cases_by_id
    )
    assert not fast_errors, fast_errors
    fast_metrics = compute_metrics(fast_entries, slow_cutoff)
    fast_status, fast_median, fast_n = threshold_status(
        fast_metrics["by_option"]["A"]["triage_values"]
    )
    assert fast_status == "NOT CROSSED", (fast_status, fast_median, fast_n)
    checks.append(
        f"fast fixture: threshold NOT CROSSED (median {fast_median:.1f} min, "
        f"n={fast_n})"
    )

    # 4. Empty log: no crash, explicit message, threshold undetermined.
    empty_entries, empty_errors, _ = validate_log([], cases_by_id)
    assert not empty_errors
    empty_report = build_report(
        valid_cases, empty_entries, case_warnings, slow_cutoff, arm="A"
    )
    assert "No triage entries" in empty_report
    assert "E4 THRESHOLD: UNDETERMINED" in empty_report
    checks.append("empty log: no crash, explicit 'No triage entries' message")

    # 5. Broken case mix must fail validation.
    broken = _fixture_cases()[:-1]
    _, broken_errors, _, _ = validate_cases([(i + 2, c) for i, c in enumerate(broken)])
    assert any("expected 30 cases" in e for e in broken_errors), broken_errors
    assert any("category" in e for e in broken_errors), broken_errors
    checks.append(f"broken case file (29 cases): {len(broken_errors)} errors caught")

    # 6. Tiny log: one row must not crash and must stay undetermined.
    tiny_entries, tiny_errors, _ = validate_log(
        [(2, slow_log[0])], cases_by_id
    )
    assert not tiny_errors, tiny_errors
    tiny_report = build_report(
        valid_cases, tiny_entries, case_warnings + ["SYNTHETIC tiny fixture"],
        slow_cutoff, arm="A"
    )
    assert "UNDETERMINED" in tiny_report
    checks.append("tiny log (1 row): no crash, threshold UNDETERMINED")

    print("SELF-TEST CHECKS")
    for check in checks:
        print(f"  PASS  {check}")
    print("")
    print("SELF-TEST PASSED (SYNTHETIC data only; no real corrections).")
    return 0


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="E4 correction triage analysis (stdlib only)."
    )
    parser.add_argument("--cases", default="cases.csv", help="case file (default: cases.csv)")
    parser.add_argument("--log", default="triage_log.csv",
                        help="triage log (default: triage_log.csv)")
    parser.add_argument("--arm", choices=INTAKE_OPTIONS, default="A",
                        help="primary intake arm for the threshold (default: A)")
    parser.add_argument("--threshold", type=float, default=THRESHOLD_MINUTES,
                        help=f"triage threshold in minutes (default {THRESHOLD_MINUTES:g})")
    parser.add_argument("--min-cases", type=int, default=MIN_CASES_FOR_THRESHOLD,
                        help=f"minimum triaged cases for a decision "
                             f"(default {MIN_CASES_FOR_THRESHOLD})")
    parser.add_argument("--as-of", dest="as_of", default=None,
                        help="ISO timestamp for open-case age (default: now)")
    parser.add_argument("--bootstrap", type=int, default=DEFAULT_BOOTSTRAP,
                        help=f"bootstrap resamples for the median CI "
                             f"(default {DEFAULT_BOOTSTRAP})")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help=f"bootstrap seed (default {DEFAULT_SEED})")
    parser.add_argument("--self-test", action="store_true",
                        help="run built-in SYNTHETIC fixtures and validation checks")
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
    if args.min_cases < 1:
        print("error: --min-cases must be >= 1", file=sys.stderr)
        return 2

    try:
        raw_cases, extra_case_cols = load_csv(Path(args.cases), CASE_COLUMNS)
        raw_log, extra_log_cols = load_csv(Path(args.log), LOG_COLUMNS)
    except DataError as exc:
        print(f"DATA ERROR: {exc}", file=sys.stderr)
        return 2

    cases, case_errors, case_warnings, _ = validate_cases(raw_cases)
    if extra_case_cols:
        case_warnings.append(
            "case file has extra column(s) ignored: " + ", ".join(extra_case_cols)
        )
    if extra_log_cols:
        case_warnings.append(
            "log file has extra column(s) ignored: " + ", ".join(extra_log_cols)
        )
    if case_errors:
        print(f"CASE VALIDATION FAILED - {len(case_errors)} error(s):", file=sys.stderr)
        for error in case_errors[:50]:
            print(f"  - {error}", file=sys.stderr)
        if len(case_errors) > 50:
            print(f"  ... and {len(case_errors) - 50} more", file=sys.stderr)
        return 1

    cases_by_id = {c["case_id"]: c for c in cases}
    entries, log_errors, log_warnings = validate_log(raw_log, cases_by_id)
    if extra_log_cols:
        pass
    warnings = case_warnings + log_warnings
    if log_errors:
        print(f"LOG VALIDATION FAILED - {len(log_errors)} error(s):", file=sys.stderr)
        for error in log_errors[:50]:
            print(f"  - {error}", file=sys.stderr)
        if len(log_errors) > 50:
            print(f"  ... and {len(log_errors) - 50} more", file=sys.stderr)
        print("Fix the log; analysis was not run.", file=sys.stderr)
        return 1

    if args.as_of:
        errors = []
        cutoff = parse_dt(args.as_of, "--as-of", 0, errors, [])
        if errors or cutoff is None:
            print("error: --as-of must be an ISO 8601 timestamp", file=sys.stderr)
            return 2
    else:
        cutoff = datetime.now(timezone.utc)

    report = build_report(
        cases, entries, warnings, cutoff, n_boot=args.bootstrap, seed=args.seed,
        arm=args.arm, threshold=args.threshold, min_cases=args.min_cases,
    )
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
