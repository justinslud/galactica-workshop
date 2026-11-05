# Product specification and planning documents

**Status:** proposal for review (2026-11-04), updated 2026-11-05. Three slices are implemented: the first M0
slice (2026-11-04), the authorization/state-machine/human-review-dashboard slice, and the M0 remainder
(permalinks, claim resolver, license fields, FTS5 search, backup drill, write idempotency). This directory extends
the existing specification; it does not replace the earlier decision record in `~/projects/galactica` or the
workshop's `CURRENT.md`/`README.md`.
**Working name:** Galactica. Candidate: T5 / t5.wiki. No rename is authorized.
**Implementation:** M0 is implemented and tested (190 tests): `PublicationEvent`, minimal `Topic`, byline/credit
page, watchlist, publication log; revision permalinks and a claim resolver; `Article.license`/`attribution`,
`Source.license`/`attribution` and a per-publication licence snapshot; `SearchDocument` + FTS5 `/search/`; a local
backup/restore drill; and `Idempotency-Key`/`If-Match` on the write API. The authorization evaluator,
`ContributorProfile`, `Review.reviewer`, `/review/` queue and human review form are also implemented. See
[`CURRENT.md`](../CURRENT.md), [the design note](AUTHORIZATION-STATE-MACHINE.md), [operations](OPERATIONS.md) and
the appended [change record](CHANGE-RECORD.md). **All M1+ items remain proposals.**

## Read in this order

1. [Briefing](BRIEFING.md) — the short version, biggest findings, disagreements, five questions for Justin.
2. [Current state and gaps](00-CURRENT-STATE.md) — what exists and works, what is accepted direction, what is
   proposal/inference/contradiction, and what to extend rather than replace.
3. [Product specification](PRODUCT-SPEC.md) — the expanded spec: actors, objects, reader experience, editorial
   model, contribution/governance, technical/operational, launch, user flows, state machines, checklists.
4. [Authorization and editorial state machine](AUTHORIZATION-STATE-MACHINE.md) — the implemented capability table,
   derived proposal states, transition table, reason codes, quotas and the human review dashboard; a design note,
   not a constitution.
5. [Decision register](DECISION-REGISTER.md) — 43 decisions with recommendation, status, authority route (A–E),
   evidence, tradeoffs, reversal/revisit trigger, and product-vs-governance domain.
6. [Worked examples](WORKED-EXAMPLES.md) — cardboard, the invention of the telephone, a hypothetical company and
   living person; normal and unhappy paths; where the rules fail.
7. [Experiment backlog](EXPERIMENTS.md) — 15 pre-registered experiments with options, measurements, cost,
   stopping rules, and the decision each would change.
8. [Launch plan](LAUNCH-PLAN.md) — stages, seed corpus, strong-launch definition, readiness criteria, minimum
   reliable core, admission control, risks, decision points.
9. [Critique response](CRITIQUE-RESPONSE.md) — the two independent critiques, what changed, what did not, and
   the dissent preserved.
10. [Operations](OPERATIONS.md) — backup, restore drill, restore procedure and the RPO/RTO caveat.
11. [Change record](CHANGE-RECORD.md) — what changed and where, what was preserved, what was not changed.
12. [E1 reader-task kit](../experiments/E1-reader-task/README.md) and [E4 correction-triage
    kit](../experiments/E4-correction-triage/README.md) — protocols and analysis scripts; no human results.

## Critique

Two independent critics reviewed the spec, register, cases, experiments and launch plan with separate briefs;
they did not see each other's work. Their files are preserved verbatim:
[trust/governance](critique/trust-governance.md) and [product/feasibility](critique/product-feasibility.md).
[The response](CRITIQUE-RESPONSE.md) records what was changed, what was not, and where the lead disagrees. The
critiques are advisory; they did not ratify policy.

## Research notes

| Note | Covers |
|---|---|
| [01 — Reader experience](research/01-reader-experience.md) | Reader tasks, trust, citation engagement, evidence/uncertainty/disagreement, views and provenance, language/reading levels, accessibility/mobile, structured views. |
| [02 — Editorial and governance](research/02-editorial-governance.md) | Editable objects, scope/coverage, neutrality checks, evidence quality, contribution/review, sybil/coordination, separation of powers, prompt injection. |
| [03 — Technical and launch](research/03-technical-launch.md) | Versioning/provenance, API/concurrency, reproducibility, search/exports/licensing, ops, launch evidence. |

Each note labels findings as **[demonstrated]**, **[claimed]**, **[historical/abandoned]**, **[proposed
adaptation]** or **[open]**, lists source URLs and access dates, and records failed fetches. Read the labels;
they are the difference between evidence and a product claim.

## How to use this directory

- **Do not treat proposals as decisions.** A `proposed` item in the decision register is a recommendation, not a
  commitment. A `D` (ask Justin) item needs his answer. An `accepted` item is a dated decision, Justin's dated
  answer (2026-11-04), or behavior that is implemented and recorded as an accepted direction (e.g. D-41/D-42).
- **Do not edit earlier decisions in place.** If a decision changes, record the change in the register and the
  change record, and preserve the earlier record.
- **Link follow-up work to the spec and the evidence.** The experiment backlog is the place for "we should test
  this"; the decision register is the place for "we chose this"; the change record is the place for "this is what
  changed".
- **Keep the research notes' labels honest.** If you update a finding, update the label and the source; do not
  turn a claim into a demonstrated fact.
- **Preserve the existing material.** The workshop `CURRENT.md`, `README.md`, code and tests are the
  implementation record; the earlier `~/projects/galactica` decision record is the historical product record.

## What this directory does not contain

- A deployment plan, credentials, production data, or a rename.
- A full authorization policy engine, automatic trust promotion, identity verification or a reputation score. The
  2026-11-05 slice is a small transition table plus a review queue; quota numbers are starting parameters, not
  measured.
- A final decision on the name, the specific seed wedge/anchor topics or public beta timing. Licensing and the
  governance-transition mechanism have dated answers in the register (subject to counsel / foundation deferred);
  real-vs-hypothetical seed subjects is settled in direction, not in subject list.
- Measured catch rates, reader usability results, load tests, a live restore drill on real data, or accessibility
  audits. Those are in the experiment backlog, not in the spec. The 2026-11-05 backup drill verified a restored
  copy, not a live-database replacement; E1/E4 have kits but no sessions.
