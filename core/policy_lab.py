"""Policy lab: score editorial policy against simulated review panels.

No database, no model calls, no network. Deterministic for a given seed.

The lab answers one question: given agents that propose edits, reviewers that are
imperfect and often correlated (one model wearing three hats), and a publication
policy, how many defective edits reach readers, and what does that cost in human
attention?

Two kinds of numbers come out of a run:

* escape rate - share of trials where a defective edit was published;
* human load - expected human reviews per 100 edits.

A policy that publishes nothing has a zero escape rate and infinite cost. The lab
exists to price that trade-off per risk class rather than argue about it.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence

# --- vocabulary -------------------------------------------------------------

#: Ways an edit can be wrong without looking wrong.
DEFECT_KINDS = (
    "unsupported_claim",
    "overgeneralization",
    "dropped_qualification",
    "number_change",
    "citation_laundering",
    "dead_link",
    "framing_omission",
)

#: Risk classes, ordered from least to most consequential.
RISK_CLASSES = ("cosmetic", "low", "standard", "high", "contentious")

#: Reviewer roles the workshop can convene.
ROLES = ("fact_check", "citation", "readability", "coverage", "source_policy")

#: What a policy can decide.
ACTIONS = ("auto_publish", "publish_with_audit", "queue_human", "block")

PUBLISHING = frozenset({"auto_publish", "publish_with_audit"})

ALL_RISK = frozenset(RISK_CLASSES)


# --- scenarios --------------------------------------------------------------


@dataclass(frozen=True)
class Defect:
    """One planted fault in a candidate edit."""

    id: str
    kind: str
    severity: int  # 1 cosmetic .. 3 changes meaning
    where: str = ""

    def __post_init__(self) -> None:
        if self.kind not in DEFECT_KINDS:
            raise ValueError(f"unknown defect kind: {self.kind}")
        if not 1 <= self.severity <= 3:
            raise ValueError("severity must be 1..3")


@dataclass(frozen=True)
class Scenario:
    """A candidate edit, the defects planted in it, and the risk class it belongs to."""

    id: str
    title: str
    risk_class: str
    defects: tuple[Defect, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        if self.risk_class not in RISK_CLASSES:
            raise ValueError(f"unknown risk class: {self.risk_class}")

    @property
    def clean(self) -> bool:
        return not self.defects

    @property
    def worst_severity(self) -> int:
        return max((d.severity for d in self.defects), default=0)


# --- reviewers --------------------------------------------------------------


@dataclass(frozen=True)
class Reviewer:
    """A role filled by some model, with the faults it tends to catch.

    ``catches`` maps defect kind to the probability this reviewer flags it.
    ``false_object`` is the probability it objects to a clean edit.
    """

    role: str
    catches: Mapping[str, float]
    false_object: float = 0.05

    def __post_init__(self) -> None:
        if self.role not in ROLES:
            raise ValueError(f"unknown role: {self.role}")


@dataclass(frozen=True)
class Panel:
    """The reviewers convened for an edit, plus how correlated their judgment is.

    ``correlation`` 0 means independent reviewers; 1 means every reviewer of a
    defect sees the same draw, so adding roles adds no information. Real panels
    sit closer to 1 when one model serves every role.
    """

    id: str
    reviewers: tuple[Reviewer, ...]
    correlation: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.correlation <= 1.0:
            raise ValueError("correlation must be 0..1")

    @property
    def size(self) -> int:
        return len(self.reviewers)


# --- policy -----------------------------------------------------------------


@dataclass(frozen=True)
class Rule:
    """First matching rule decides. ``max_objections`` is an objection budget."""

    action: str
    risk_classes: frozenset[str] = ALL_RISK
    max_objections: int = 0
    min_reviews: int = 1

    def __post_init__(self) -> None:
        if self.action not in ACTIONS:
            raise ValueError(f"unknown action: {self.action}")

    def matches(self, risk_class: str, objections: int, reviews: int) -> bool:
        return (
            risk_class in self.risk_classes
            and objections <= self.max_objections
            and reviews >= self.min_reviews
        )


@dataclass(frozen=True)
class Policy:
    """An ordered rule list plus the audit rate for publish_with_audit."""

    id: str
    rules: tuple[Rule, ...]
    audit_sample: float = 0.1
    notes: str = ""

    def decide(self, risk_class: str, objections: int, reviews: int) -> str:
        for rule in self.rules:
            if rule.matches(risk_class, objections, reviews):
                return rule.action
        return "block"


# --- simulation -------------------------------------------------------------


@dataclass(frozen=True)
class Trial:
    scenario_id: str
    risk_class: str
    action: str
    reviews: int
    objections: int
    caught: tuple[str, ...]
    missed: tuple[str, ...]
    audited: bool

    @property
    def defective(self) -> bool:
        return bool(self.missed)

    @property
    def escaped(self) -> bool:
        return self.action in PUBLISHING and self.defective


def _catches(reviewer: Reviewer, defect: Defect, draw: float, rng: random.Random, correlation: float) -> bool:
    rate = reviewer.catches.get(defect.kind, 0.0)
    if rate <= 0.0:
        return False
    if correlation >= 1.0:
        return draw < rate
    if correlation <= 0.0:
        return rng.random() < rate
    return (draw if rng.random() < correlation else rng.random()) < rate


def run_trial(scenario: Scenario, panel: Panel, policy: Policy, rng: random.Random) -> Trial:
    """One edit, one panel, one policy decision."""
    caught: set[str] = set()
    objections = 0
    # One shared draw per defect: when reviewers are correlated they see the same
    # signal, so adding roles adds no information.
    shared = {defect.id: rng.random() for defect in scenario.defects}
    for reviewer in panel.reviewers:
        objected = False
        for defect in scenario.defects:
            if _catches(reviewer, defect, shared[defect.id], rng, panel.correlation):
                caught.add(defect.id)
                objected = True
        if not objected and rng.random() < reviewer.false_object:
            objected = True
        if objected:
            objections += 1
    action = policy.decide(scenario.risk_class, objections, panel.size)
    audited = action == "publish_with_audit" and rng.random() < policy.audit_sample
    missed = tuple(d.id for d in scenario.defects if d.id not in caught)
    return Trial(
        scenario_id=scenario.id,
        risk_class=scenario.risk_class,
        action=action,
        reviews=panel.size,
        objections=objections,
        caught=tuple(sorted(caught)),
        missed=missed,
        audited=audited,
    )


# --- reporting --------------------------------------------------------------


@dataclass
class Cell:
    """One policy x risk class."""

    policy_id: str
    risk_class: str
    trials: int = 0
    published: int = 0
    escaped: int = 0
    blocked: int = 0
    queued: int = 0
    audited: int = 0
    defective_trials: int = 0
    clean_trials: int = 0
    caught_by_kind: dict[str, int] = field(default_factory=dict)
    defects_by_kind: dict[str, int] = field(default_factory=dict)

    def add(self, trial: Trial, scenario: Scenario) -> None:
        self.trials += 1
        if trial.action in PUBLISHING:
            self.published += 1
        if trial.action == "block":
            self.blocked += 1
        if trial.action == "queue_human":
            self.queued += 1
        if trial.audited:
            self.audited += 1
        if trial.defective:
            self.defective_trials += 1
        else:
            self.clean_trials += 1
        if trial.escaped:
            self.escaped += 1
        for defect in scenario.defects:
            self.defects_by_kind[defect.kind] = self.defects_by_kind.get(defect.kind, 0) + 1
            if defect.id in trial.caught:
                self.caught_by_kind[defect.kind] = self.caught_by_kind.get(defect.kind, 0) + 1

    @property
    def escape_rate(self) -> float:
        return self.escaped / self.trials if self.trials else 0.0

    @property
    def publish_rate(self) -> float:
        return self.published / self.trials if self.trials else 0.0

    @property
    def human_load_per_100(self) -> float:
        """Expected human reviews per 100 edits: queued, plus sampled audits."""
        if not self.trials:
            return 0.0
        return 100.0 * (self.queued + self.audited) / self.trials

    def recall(self, kind: str) -> float | None:
        total = self.defects_by_kind.get(kind, 0)
        return self.caught_by_kind.get(kind, 0) / total if total else None

    def as_dict(self) -> dict:
        return {
            "policy": self.policy_id,
            "risk_class": self.risk_class,
            "trials": self.trials,
            "escape_rate": round(self.escape_rate, 4),
            "publish_rate": round(self.publish_rate, 4),
            "human_load_per_100": round(self.human_load_per_100, 1),
            "defective_trials": self.defective_trials,
            "clean_trials": self.clean_trials,
            "recall": {k: round(v, 3) for k, v in ((k, self.recall(k)) for k in DEFECT_KINDS) if v is not None},
        }


@dataclass
class Report:
    trials: int
    seed: int
    panel: str
    correlation: float
    scenarios: list[dict]
    cells: list[Cell]

    def table(self) -> list[dict]:
        return [cell.as_dict() for cell in self.cells]

    def as_dict(self) -> dict:
        return {
            "generated_at": None,  # filled by the caller
            "trials_per_cell": self.trials,
            "seed": self.seed,
            "panel": self.panel,
            "correlation": self.correlation,
            "scenarios": self.scenarios,
            "cells": self.table(),
        }

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), indent=2, sort_keys=False)

    def cell(self, policy_id: str, risk_class: str) -> Cell | None:
        for cell in self.cells:
            if cell.policy_id == policy_id and cell.risk_class == risk_class:
                return cell
        return None

    def best_cell(self, risk_class: str, max_escape: float = 0.0) -> Cell | None:
        """Cheapest policy that stayed within the escape budget for one risk class."""
        candidates = [
            c for c in self.cells
            if c.risk_class == risk_class and c.trials and c.escape_rate <= max_escape
        ]
        return min(candidates, key=lambda c: c.human_load_per_100) if candidates else None


def run_lab(
    scenarios: Sequence[Scenario],
    panel: Panel,
    policies: Sequence[Policy],
    trials: int = 400,
    seed: int = 7,
) -> Report:
    if trials < 1:
        raise ValueError("trials must be positive")
    cells: dict[tuple[str, str], Cell] = {}
    for policy in policies:
        for risk_class in RISK_CLASSES:
            cells[(policy.id, risk_class)] = Cell(policy_id=policy.id, risk_class=risk_class)
    for scenario in scenarios:
        for policy in policies:
            cell = cells[(policy.id, scenario.risk_class)]
            for index in range(trials):
                rng = random.Random(f"{seed}:{scenario.id}:{policy.id}:{index}")
                cell.add(run_trial(scenario, panel, policy, rng), scenario)
    return Report(
        trials=trials,
        seed=seed,
        panel=panel.id,
        correlation=panel.correlation,
        scenarios=[
            {
                "id": s.id,
                "title": s.title,
                "risk_class": s.risk_class,
                "defects": [{"id": d.id, "kind": d.kind, "severity": d.severity, "where": d.where} for d in s.defects],
            }
            for s in scenarios
        ],
        cells=[cells[key] for key in sorted(cells)],
    )


# --- the shipped pack -------------------------------------------------------


def _reviewer(role: str, **rates: float) -> Reviewer:
    base = {"fact_check": 0.0, "citation": 0.0, "readability": 0.0, "coverage": 0.0, "source_policy": 0.0}
    base.update(rates)
    return Reviewer(role=role, catches=base)


def panels() -> dict[str, Panel]:
    """Three panels worth comparing, all plausible for this workshop today."""
    return {
        # One free model serving every role: the current setup.
        "one-model": Panel(
            id="one-model",
            correlation=0.85,
            reviewers=(
                _reviewer("fact_check", unsupported_claim=0.62, overgeneralization=0.34, number_change=0.45, dead_link=0.20),
                _reviewer("citation", citation_laundering=0.40, unsupported_claim=0.30, dead_link=0.55),
                _reviewer("readability", dropped_qualification=0.30, overgeneralization=0.25, framing_omission=0.15),
            ),
        ),
        # Three roles on three different models with different prompts.
        "mixed": Panel(
            id="mixed",
            correlation=0.30,
            reviewers=(
                _reviewer("fact_check", unsupported_claim=0.78, overgeneralization=0.55, number_change=0.62, dead_link=0.30),
                _reviewer("citation", citation_laundering=0.70, unsupported_claim=0.45, dead_link=0.80),
                _reviewer("coverage", framing_omission=0.45, dropped_qualification=0.40, overgeneralization=0.35),
            ),
        ),
        # A rubber stamp: fast, cheap, and the reason policy matters.
        "weak": Panel(
            id="weak",
            correlation=0.90,
            reviewers=(
                _reviewer("fact_check", unsupported_claim=0.30, overgeneralization=0.15, number_change=0.20),
                _reviewer("readability", dropped_qualification=0.10),
            ),
        ),
    }


def scenarios() -> list[Scenario]:
    """A small pack: five clean controls and seven planted defects."""
    return [
        Scenario("typo", "Fix a spelling mistake", "cosmetic", (), "control: clean cosmetic edit"),
        Scenario("format", "Normalise heading levels", "cosmetic", (), "control: clean formatting edit"),
        Scenario("deadlink", "Replace a dead link with the same source", "low", (), "control: clean low-risk edit"),
        Scenario("addsource", "Add a source without changing claims", "low", (), "control: clean low-risk edit"),
        Scenario("metadata", "Normalise publication metadata", "cosmetic", (), "control: clean cosmetic edit"),
        Scenario(
            "unsupported",
            "Add a claim with no citation",
            "standard",
            (Defect("d1", "unsupported_claim", 3, "body paragraph"),),
        ),
        Scenario(
            "overgeneral",
            "Turn 'some studies' into 'research shows'",
            "standard",
            (Defect("d1", "overgeneralization", 2, "body paragraph"),),
        ),
        Scenario(
            "numbers",
            "Change a figure from 12% to 21%",
            "high",
            (Defect("d1", "number_change", 3, "body paragraph"),),
        ),
        Scenario(
            "qualifier",
            "Drop 'preliminary' from a finding",
            "high",
            (Defect("d1", "dropped_qualification", 2, "body paragraph"),),
        ),
        Scenario(
            "launder",
            "Cite three articles that all quote one press release",
            "standard",
            (Defect("d1", "citation_laundering", 2, "claims and evidence"),),
        ),
        Scenario(
            "omission",
            "Rewrite the lead and omit the main objection",
            "contentious",
            (Defect("d1", "framing_omission", 3, "lead section"),),
        ),
        Scenario(
            "contested",
            "Add a contested claim to a disputed topic",
            "contentious",
            (
                Defect("d1", "unsupported_claim", 3, "body paragraph"),
                Defect("d2", "dropped_qualification", 2, "body paragraph"),
            ),
        ),
    ]


def policies() -> list[Policy]:
    """Policies from 'humans decide everything' to 'publish on silence'."""
    return [
        Policy(
            "human-all",
            (Rule("queue_human", ALL_RISK, max_objections=99),),
            notes="Every edit waits for a person. The current app.",
        ),
        Policy(
            "no-objection",
            (
                Rule("auto_publish", ALL_RISK, max_objections=0),
                Rule("queue_human", ALL_RISK, max_objections=99),
            ),
            notes="Publish when no reviewer objects.",
        ),
        Policy(
            "low-risk-audit",
            (
                Rule("auto_publish", frozenset({"cosmetic"}), max_objections=0),
                Rule("publish_with_audit", frozenset({"cosmetic", "low"}), max_objections=1),
                Rule("queue_human", ALL_RISK, max_objections=0),
                Rule("queue_human", ALL_RISK, max_objections=99),
            ),
            audit_sample=0.2,
            notes="Cosmetic edits publish on silence; low-risk ones publish sampled.",
        ),
        Policy(
            "lenient",
            (
                Rule("auto_publish", frozenset({"cosmetic"}), max_objections=0),
                Rule("auto_publish", frozenset({"low", "standard"}), max_objections=1),
                Rule("queue_human", ALL_RISK, max_objections=99),
            ),
            notes="Tolerate one objection on ordinary edits.",
        ),
        Policy(
            "audit-standard",
            (
                Rule("auto_publish", frozenset({"cosmetic"}), max_objections=0),
                Rule("publish_with_audit", frozenset({"low", "standard"}), max_objections=0),
                Rule("queue_human", ALL_RISK, max_objections=99),
            ),
            audit_sample=0.5,
            notes="Ordinary edits publish on silence, half get a human look afterwards.",
        ),
        Policy(
            "tiered",
            (
                Rule("auto_publish", frozenset({"cosmetic"}), max_objections=0),
                Rule("publish_with_audit", frozenset({"low"}), max_objections=0),
                Rule("queue_human", frozenset({"standard"}), max_objections=0),
                Rule("queue_human", frozenset({"high", "contentious"}), max_objections=99),
                Rule("queue_human", ALL_RISK, max_objections=99),
            ),
            audit_sample=0.25,
            notes="Autonomy only where a defect is cheap to undo.",
        ),
    ]


def fingerprint(report: Report) -> str:
    """Short stable id for a run, so a page can say which run it is showing."""
    return hashlib.sha256(report.to_json().encode()).hexdigest()[:12]
