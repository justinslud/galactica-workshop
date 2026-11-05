# Worked examples

**Version:** 1.0, 2026-11-04.
**Purpose:** test the proposed rules against concrete cases, including unhappy paths, and record where the rules
fail or require judgment. The cases are illustrative product walkthroughs, not researched articles. Factual
details in the real-topic cases (cardboard, the telephone) are placeholders that a contributor would have to
source and verify; the hypothetical company and person are explicitly fictional.
**Rule references:** `PRODUCT-SPEC.md` §3 (objects/invariants), §4 (reader), §5 (editorial), §6
(contribution/governance), §8 (technical). Decisions: `DECISION-REGISTER.md`.
**Companion:** [experiment backlog](EXPERIMENTS.md).

---

## Case A — Cardboard (ordinary subject)

### A.0 Creating the topic

A contributor proposes a new topic:

- **Canonical title:** Cardboard. **Aliases:** corrugated cardboard, corrugated fiberboard, fibreboard.
- **Scope:** "Paper-based packaging material, especially corrugated fiberboard and paperboard; covers
  definitions, history, manufacture, uses, recycling and environmental impact. Excludes papermaking chemistry,
  corrugated steel, and packaging design as a profession."
- **Risk class:** low (ordinary industrial material; no living subjects; no active controversy).
- **Coverage checklist:** definition, history, types, manufacture, uses, recycling/environment, current status,
  further reading.
- **Proposed article:** 600 words, 8 claims, 6 sources, one table of material types.

**Triage.** The router assigns `factual` + `source` + `readability`, and raises the risk to **standard** because
the article makes quantitative recycling claims and a historical patent claim. Triage can raise risk but not
lower it silently (spec §6.4).

**Review.**
- Factual reviewer: the 1856 patent date and the recycling percentage need exact citations; the claim "most
  cardboard is recycled" is an overgeneralization without a region and year.
- Source reviewer: the trade association is an interested party for the recycling claim; the standards body is
  strong for definitions, weak for environmental outcomes. A shared-origin check finds two "different" articles
  that both rewrite the same press release.
- Readability reviewer: the lead is clear; the manufacture section needs a diagram or a simpler explanation.

**Decision.** The author adds an environmental-agency figure with an "as of" date, attributes the industry
estimate, and splits the overgeneralized claim into region-specific claims. Approved and published as r1.
Publication writes a `PublicationEvent` (who, when, which revision, which policy) — not just a pointer update.

**Reader view.** The article shows a "Seed" maturity badge, last reviewed date, and a correction link. The lead
defines cardboard in the first sentence and says what the article excludes. The "At a glance" table has four
facts, each with a claim link and an "as of" date. The reader can expand the patent claim and see the patent
record, the snapshot hash and the reviewer's note.

**Where this is harder than it looks.** "Cardboard" is ambiguous (paperboard vs corrugated fiberboard) and the
scope statement has to choose. If the contributor had written a general "packaging" article, the topic would be
too broad and the lead could not summarize it. The scope statement is doing real work.

### A.1 A normal correction

A reader reports: "The 2018 recycling rate is 68.8%, but the EPA page says 68.2%." They include the URL.

1. The correction form creates a `Correction` with status `received`, relationship `reader`, and a tracking
   code; no account required (spec §4.4).
2. Triage marks it `factual`, severity low, links it to the claim, and assigns a factual reviewer. Acknowledge
   within 2 business days.
3. The reviewer checks the EPA page and the preserved snapshot. The snapshot is from 2024; the page has been
   revised. The reviewer creates a new snapshot, confirms 68.2%, and proposes an edit against the current
   revision.
4. The proposal goes through factual + source review. Approved; published as r2. The correction notice says:
   "Corrected 12 Nov 2026: updated the 2018 recycling rate from 68.8% to 68.2% after the EPA revised its page
   (new snapshot)."
5. The correction page shows `accepted` with a link to r2 and the diff. The reader is notified if they left a
   contact.

**Unhappy path 1: the reader is wrong.** The reviewer checks and finds the article is right (the reader looked
at a different table). The correction is closed `rejected` with a link to the evidence and an explanation. The
reader can appeal within 14 days. This is a valid outcome, not a failure.

**Unhappy path 2: the reader submits 20 variants.** Duplicate detection merges them; rate limits apply; the
correction is handled once. If the reader is a legitimate expert with new evidence, the duplicate merge should
not lose the evidence — the reviewer can attach it to the original.

**Unhappy path 3: the correction is legally threatening.** The reporter is a company lawyer demanding removal.
The correction is triaged as `policy`; legal review is triggered; the article is not changed merely because of
the threat. If the material is well sourced, the response is a right-of-reply process, not removal (spec §5.7).

### A.2 A credible challenge to an existing source

A reader or reviewer challenges a cited industry report: "This is a press release; the underlying data is not
public, and the company funded the study."

1. A `source` review is opened. A `SourceAssessment` records: authorship (company), process (none), evidence
   access (summary only), independence (funded), competence (topic-relevant), freshness (2023).
2. The assessment is downgraded from `strong` to `weak` for the causal claim. The claim is flagged `partial`.
3. A proposal replaces it with two independent sources and adds a sentence about the industry estimate. The old
   source remains in the record with its assessment and the reason for downgrade; the article's correction
   notice explains the change.
4. The organization that published the report can respond. Its response is included if it provides evidence;
   it is labeled as the organization's response.

**Where the rule fails.** If all available sources share the same origin, the article may have to say "only
industry figures are available" and mark the claim `partial`. That is an honest outcome. A reviewer must resist
the temptation to manufacture balance by citing a weaker source just to have two.

**Machine check vs judgment.** The quote-in-snapshot check passes; the funding and independence judgment is
human. The system can surface a shared `origin_key` and a DOI/publisher graph, but it cannot decide whether the
industry report is trustworthy for this claim. (Spec §5.5.)

### A.3 Conflicting submissions

Agent A proposes: "The 2024 recycling rate was 71%." Agent B proposes: "The 2024 recycling rate was 65%." Both
cite sources; one is an industry estimate, one is a government statistic with a different scope (municipal solid
waste vs all paper and board).

1. Triage sees the conflict and merges the proposals into a `Dispute` (not a duplicate). A factual reviewer
   checks both sources; a coverage reviewer checks scope.
2. The article states: "Estimates differ: the EPA reports 65% for municipal solid waste; the industry
   association reports 71% for all paper and board. The difference reflects scope." Both claims are cited.
3. If one source is clearly better for the claim, the article says so and gives the other proportional space.
   No false balance.
4. The dispute page records the positions and the resolution; the agents' proposals are linked.

**Where the rule fails.** If the sources are genuinely incompatible and neither is clearly better, the article
must present the disagreement and say what would resolve it. A reviewer should not force a single number. If
one agent keeps resubmitting the same claim after the dispute is resolved, the repeat is refused and the
operator is rate-limited, not banned for viewpoint.

### A.4 A coordinated or repetitive campaign

Twenty new accounts submit near-identical proposals adding "cardboard is fully compostable in home compost"
with the same manufacturer's page and the same phrasing.

1. The system clusters them: shared source, text similarity, timing, new accounts. It merges duplicates and
   flags a `campaign`.
2. A steward checks the claim. It is partially true for some uncoated boards, false for coated or laminated
   boards; the source is a manufacturer with a COI. The proposal is rejected with a reason. The article may add
   a nuanced sentence if independent evidence supports it.
3. Accounts are rate-limited, not banned for viewpoint. The operator can appeal. If the accounts are
   sockpuppets of one operator, the operator is suspended for inauthentic behavior; the claim is still evaluated
   on evidence.
4. A public note may say "multiple submissions from one operator were merged" without exposing personal data.

**Where the rule fails.** A legitimate composting-advocacy campaign looks similar. Human review, disclosure and
an appeal path are required; do not infer coordination from agreement alone (spec §6.11). The false-positive
cost is real: a classroom or a translation team can produce near-identical submissions.

### A.5 A change that makes a derived view stale

A timeline view "History of corrugated board" is published from article r5, with 12 events and sources.

1. A correction changes the 1856 patent date and adds an 1871 event; the article is published as r6.
2. The view's base revision is no longer current; it is automatically marked `stale`. Readers see: "This
   timeline was built from r5; the article has since changed. Some events may be out of date."
3. A contributor re-generates or edits the timeline against r6, reviews the changed events, and publishes v2.
   The old view remains readable as historical.
4. Exports and "cite this page" use the current view only; stale views are excluded unless explicitly
   historical.

**Where the rule fails.** A view can be stale even if the base revision is unchanged — for example, a cited
source is retracted. The system should also mark views stale when a cited source is retracted or a key assertion
changes status. That requires linking views to assertions, not just revisions (spec §3.8 V5).

### A.6 An appeal and rollback

1. A proposal is rejected for "insufficient independent sources." The author appeals with a new government
   dataset published after the decision.
2. The appeal is triaged as `new_evidence`; a panel of 3 (no original decision-maker) reviews the record and the
   dataset. The panel remands for re-review.
3. The proposal is re-reviewed with the new source; approved and published. The appeal record shows `remanded`
   and the outcome.
4. Separately, a published revision is found to contain a privacy violation (a reader's personal data was
   pasted into a source quote). Staff emergency-unpublish it, publish an incident note, and open a post-mortem.
   A corrected revision is published after review.
5. The author of the original revision can appeal the emergency action; the panel checks whether it was
   proportionate. If not, the revision may be restored with redactions.

**Where the rule fails.** Appeals can be used to relitigate. Limits (one appeal, 14 days, new evidence) and a
panel with no stake are necessary but not sufficient; the panel needs a clear standard and a public reasoning
record. The emergency power is also abusable; a second-person review within 24 hours and a public incident note
are the safeguards.

### A.7 Where Case A forces a spec change

- The claim "68.8%" is revision-bound text; tracking it across r1/r2 requires a stable `Assertion` (spec §3.6).
- The publication history requires `PublicationEvent`; the current `Article.published` pointer would lose r1
  after r2 (spec §3.9, §8.1).
- The correction needs a `Correction` object and a public notice; the current app has no reader correction path.
- The source challenge needs `SourceAssessment` with an expiry and an appeal; the current `Source` check status
  is too coarse.
- The view needs a manifest and assertion links, not just a base revision.
- The campaign needs clustering and a review-capacity response, not just a rate limit.

---

## Case B — The invention of the telephone (contested historical subject)

### B.0 Scope and contested terminology

A contributor proposes a topic:

- **Canonical title:** Invention of the telephone.
- **Scope:** "The development of telephony from the mid-19th century to the early 20th, including the
  contributions of Antonio Meucci, Philipp Reis, Elisha Gray and Alexander Graham Bell, the Bell patents, and the
  subsequent legal and historical disputes. Excludes modern telephony and the technical details of switching."
- **Risk class:** contentious (national narratives, priority disputes, a well-known legal case).
- **Contested terminology:** "invention" itself is contested; the article uses "invention" in the lead but
  defines what it means (first working device, first patent, first commercial system) and says that different
  claimants satisfy different definitions.

**Review.** The coverage reviewer checks that the lead does not declare a single winner. The factual reviewer
checks the dates and the patent numbers. The source reviewer notes that some sources are nationalist or
hagiographic; the article must attribute the framing, not adopt it.

**Where the rule fails.** The scope is genuinely contested. A US-centric reader may expect Bell; an Italian
reader may expect Meucci; a German reader may expect Reis. The article cannot satisfy all three with one lead;
it can define the question, present the evidence for each claimant, and say why the answer depends on the
criterion. This is not false balance; it is a genuine definitional dispute.

### B.1 Reading the article

The lead says: "The invention of the telephone is conventionally attributed to Alexander Graham Bell, who
received the first US patent for a telephone in 1876; other claimants, including Antonio Meucci and Elisha Gray,
made contributions that are recognized to varying degrees. The word 'invention' is used differently in different
accounts."

The article has a **timeline** view (1849–1888), a **comparison table** of claimants (device, patent, first
public demonstration, legal outcome), and a **dispute** page on priority. Each claim has evidence. The
"Confidence and gaps" panel says: "The patent facts are well documented; the priority question is contested;
the role of Meucci is better documented in Italian-language sources than in English-language ones."

**Reader value.** A reader who came for "who invented the telephone?" gets a direct answer in the lead and a
nuanced explanation below. A reader who came for the priority dispute gets a structured comparison. A reader
who wants to cite a specific claim gets a revision and claim ID.

### B.2 Neutrality checks in practice

The coverage reviewer records:

1. **Proportion:** the lead gives Bell the conventional attribution but does not erase the others; the body
   gives each claimant proportional space based on reliable-source coverage.
2. **Attribution:** "conventionally attributed to" and "Italian-language sources emphasize" rather than
   asserting one national narrative.
3. **Framing:** no "Criticism of Bell" section; the dispute is integrated into the history, not segregated as a
   hierarchy of fact.
4. **Omission:** the legal cases and the US House resolution are included; the article does not omit the
   commercial and patent context.
5. **False balance:** the article does not give a fringe claim equal weight; it distinguishes documented
   contributions from later nationalist embellishment.
6. **Labeling:** fact, legal finding, and historical interpretation are distinguished.
7. **Scope:** dates and jurisdictions are specified.
8. **Language:** "invented" is defined; "stole" is avoided unless attributed.
9. **Sourcing symmetry:** claims about Bell and Meucci are held to the same evidentiary standard.
10. **Reader takeaway:** a reasonable reader understands that the answer depends on the criterion, not that
    "both sides" are equally supported.

**Where the rule fails.** The line between "proportional space" and "false balance" is judgment. A reviewer may
disagree with the weighting. The dispute page and the review reasons make the disagreement inspectable; they do
not eliminate it. This is a case where the appeals panel may need a historian, not just a generalist.

### B.3 A credible challenge to a national narrative

A contributor proposes to add: "Meucci was the true inventor; Bell stole the idea." The factual reviewer objects:
the claim is not supported by the cited sources, which say Meucci's caveat was filed earlier but lapsed, and
that the legal cases did not establish theft. The contributor argues that Italian sources say otherwise.

**Handling:**
- The proposal is rejected with a reason: the claim overstates the evidence and uses "stole" without attribution.
- A `Dispute` is opened on the priority question. The article adds a sentence: "Some Italian-language accounts
  describe Meucci as the true inventor; the legal record does not establish that Bell stole the invention."
- The contributor can appeal; the appeal panel checks whether the rejection misapplied the sourcing standard.
  If the panel finds a genuine source gap, it remands for a source-assessment review, not for the claim to be
  published as fact.

**Where the rule fails.** The contributor may be right that English-language sources are biased. The system's
answer is not "both are true" but "the evidence is uneven across languages; here is what each source supports."
That is a scope/coverage problem as much as a factual one. A language edition with Italian sources may present
a different emphasis; the shared assertion IDs keep the factual base connected.

### B.4 A timeline view goes stale

The timeline is published from r3. A later revision adds a newly digitized 1876 letter and changes the date of
a demonstration. The timeline is marked stale; a contributor re-reviews the affected events and publishes v2.
The old timeline remains as a historical artifact.

**Where the rule fails.** The timeline includes events whose dates are disputed. The manifest records `as_of`
per event? The spec's manifest has one `as_of` for the view; a timeline needs per-event dates and sources. The
spec should require per-row/per-event source and date fields for timeline/table views, not just a view-level
`as_of`. **This is a revision to the spec.** (Added to the experiment backlog: "structured view schema".)

### B.5 Where Case B forces a spec change

- A single "neutrality" verdict is inadequate; the ten checks and the reasons are necessary.
- "Due weight" must be defined against reliable-source prevalence, not national popularity (spec §5.6).
- Contested terminology needs a first-class terminology note (spec §5.4).
- A timeline needs per-event sources/dates; a view-level `as_of` is not enough.
- The appeal panel may need domain expertise; a generalist panel can check procedure but not historiography.

---

## Case C — Northwind Logistics (hypothetical company) and Dr. Maya Chen (hypothetical living person)

> **These are fictional examples.** "Northwind Logistics" and "Dr. Maya Chen" do not exist. The case is written
> to test the rules without making claims about real people or companies.

### C.0 The company article

A contributor proposes a topic:

- **Canonical title:** Northwind Logistics.
- **Scope:** "A freight and warehousing company; covers its founding, operations, regulatory findings, labor
  disputes and environmental record. Excludes routine commercial listings and advertising."
- **Risk class:** high (company with a regulatory finding and a labor dispute).
- **Sources:** a regulator's enforcement notice, two independent news reports, the company's own website, a
  trade publication, and a union report.

**Triage.** `factual` + `source` + `policy` (COI/legal). The company has a verified organization account and
submits a correction/response through the proper channel; it does not edit the article directly.

### C.1 A company submission with COI

The company submits a proposed change: "The 2023 fine was a paperwork error, not a safety violation; please
remove the word 'unsafe'." It discloses the relationship and provides the regulator's settlement document.

**Handling:**
- The proposal is labeled "provided by Northwind Logistics" and reviewed by a `policy` reviewer with no COI.
- The factual reviewer checks the settlement: it says the company paid a fine for record-keeping failures and
  agreed to a safety audit, without admitting the underlying safety allegation. The word "unsafe" is not
  supported as a finding; "regulators found record-keeping failures and required a safety audit" is.
- The article is corrected to the precise finding; the company's response is included ("Northwind says the
  penalty concerned paperwork, not unsafe operations"). The well-sourced negative information (the fine, the
  audit requirement) stays.
- The company cannot remove the independent reporting. It can submit a response and correct its own basic facts
  (founding date, headquarters) with a primary source.

**Where the rule fails.** The line between "paperwork error" and "safety violation" is exactly the kind of
framing a company wants to litigate. The regulator's document is the anchor; the article should quote it and
attribute the company's characterization. A generalist reviewer may not know the regulatory context; the
`policy` role should include someone with domain or legal knowledge.

### C.2 Well-supported negative information and right of reply

Two independent news investigations report that Northwind warehouses had unsafe heat conditions; a regulator
finds record-keeping failures; a worker death is reported by a local newspaper and a union report.

**Handling:**
- The article includes the investigations, the regulator's finding, and the death, with high-quality sources.
- The company's response is included in the same section, not buried: "Northwind disputes the characterization
  and says it has installed cooling systems."
- The article does not give a denial equal weight to the investigations if the evidence is one-sided; it states
  the weight of evidence and attributes the denial.
- The `policy` reviewer checks privacy (the worker's family is not named), legal risk, and sourcing symmetry.
- The company's request to remove the death is refused because the sources are strong; the correction process
  offers a right of reply and a factual correction if the details are wrong.

**Where the rule fails.** A company can threaten litigation; a small project may not have counsel. The spec
requires legal review for high-risk content, but at launch there may be no lawyer. The practical answer is to
avoid real company cases until counsel is available, and to use hypothetical cases for the first pass (D-36).

### C.3 A coordinated PR campaign

A PR firm creates 30 accounts and submits variations of "Northwind is a leader in workplace safety" with the
company's own press releases and awards.

**Handling:**
- The system clusters the accounts by timing, source, and text similarity; it flags a campaign.
- The proposals are merged and rejected as promotional; the company's verified account is asked to disclose the
  PR firm.
- The article is not changed by volume. If the company has a genuine correction, it goes through the COI
  channel.
- Accounts are rate-limited; the operator can appeal; the claim is evaluated on evidence, not on the number of
  submissions.

**Where the rule fails.** A legitimate industry association or a group of employees might coordinate a
good-faith correction campaign. The system must distinguish disclosure and evidence from volume; a campaign
with a disclosed operator and a valid source should be reviewed on its merits.

### C.4 A living person: Dr. Maya Chen (hypothetical)

Dr. Chen is a fictional researcher. An article says she "falsified data in a 2022 study." The claim is based on
a university investigation that found "research misconduct" and a retraction of the paper. Dr. Chen denies the
finding and says the investigation was flawed.

**Handling:**
- The article is flagged high-risk/BLP. The `policy` reviewer checks the sourcing: the university report is a
  primary source; the retraction is a status-of-record; a news report corroborates. The claim is attributed:
  "A university investigation found research misconduct; the paper was retracted. Chen denies the finding and
  says the process was flawed."
- The article does not include unrelated personal details (address, family, health). Privacy review.
- Dr. Chen submits a correction: the investigation report is not public; the finding was appealed; a second
  review is pending. The correction is triaged; the article adds the pending appeal and removes the word
  "falsified" if it is not supported (the finding was "misconduct," not necessarily fabrication).
- The correction is accepted; a new revision is published with a notice. The negative finding remains, with the
  appeal status.
- Dr. Chen appeals the inclusion of the finding. The appeal panel checks BLP policy: the finding is
  well-sourced, but the appeal is pending; the article must say so. The panel does not remove the finding; it
  requires the pending status to be visible.

**Emergency rollback.** A later edit adds Dr. Chen's home address from a leaked document. Staff emergency-
unpublish the revision, publish an incident note, and open a post-mortem. The address is removed; the
contributor is suspended for privacy violation; the operator can appeal.

**Where the rule fails.** BLP is expensive. A small project cannot run a 24/7 legal/privacy desk. The spec
proposes avoiding real living-person cases until there is a named policy reviewer and legal counsel, and using
hypothetical cases for the first pass. The BLP asymmetry (remove first, discuss later) is the right default, but
it requires someone available to act.

### C.5 Where Case C forces a spec change

- A `Correction` object with relationship and public notice is necessary; a company/person submission is not a
  normal edit.
- A `SourceAssessment` with COI/funding fields is necessary; "the company's website" is not a neutral source.
- A `policy` review role with legal/privacy competence is necessary; a generalist reviewer cannot carry BLP.
- A `Dispute`/appeal path with a pending-status field is necessary; "under appeal" is a fact the article must
  show.
- Emergency rollback needs a fast path and a post-mortem; the current revert flow is too slow for a privacy
  violation.
- The risk class must be able to be raised by triage; a company/living-person article cannot be treated as
  standard because the contributor says so.

---

## Cross-cutting unhappy paths

| Situation | What the proposed rules do | Where they fail / require judgment |
|---|---|---|
| A correction is actually a legal threat | Triage as `policy`; legal review; right of reply; no removal without evidence | No counsel at launch; may need to avoid real high-risk subjects |
| A source is retracted after publication | Flag dependent claims `stale`/`retracted`; re-review; correction notice | Crossref gives status; the editorial response is judgment; no demonstrated playbook |
| A contributor keeps resubmitting a rejected claim | Duplicate detection; repeat flag; rate limit; appeal path | A determined operator can create new accounts; clustering is probabilistic |
| Two reviewers disagree | Panel outcome is a summary; publisher decides with reasons; appeal | Reviewer disagreement may be a sign the evidence is genuinely ambiguous; do not force consensus |
| A derived view is stale but no one fixes it | Stale badge; excluded from current citations; maintenance owner | If no owner, the view should be withdrawn; the spec needs an owner field and an expiry |
| A language edition contradicts the English article | Shared assertion IDs; translation review; dispute | Translation may reveal a genuine source difference; do not assume English is right |
| A reader wants a quick answer, not an article | Summary/at-a-glance surface; "cite this page" | The quick answer may be wrong; the summary must carry uncertainty and a link to evidence |
| An agent proposes 50 edits in a minute | Quotas; burst limits; review queue | Legitimate bulk work (translation, link repair) needs a batch path; a blanket limit blocks it |
| A reviewer has a COI | Recusal; policy review | The reviewer may not disclose; the system can only record declared relationships |
| A policy change is unpopular | Comment period; reasons; appeal | The policy steward can still decide; legitimacy depends on transparency and a path to change |

---

## What the cases change in the recommendations

1. **`PublicationEvent` is required before launch**, not just a nice-to-have. Every case with a correction or
   revert needs "what was published on date X"; the current pointer loses it.
2. **`Assertion` is required for cross-revision tracking**, but can be limited to substantive claims. The
   cardboard recycling figure and the telephone priority claims are the motivating examples.
3. **`Correction` and `Dispute` are separate objects**, not proposal subtypes. A reader correction has a
   different lifecycle and service level than an edit proposal.
4. **`SourceAssessment` needs COI/funding/independence fields and an expiry.** The industry report and the
   company website cases fail without them.
5. **`View` needs a manifest, per-event/per-row source fields for timelines/tables, and an owner.** The stale
   timeline case is not solved by a base revision alone.
6. **BLP/company content needs a `policy` role and a legal/privacy path before real subjects.** Hypothetical
   cases are not just a convenience; they are a launch safety requirement.
7. **Campaign clustering must be paired with a batch path and an appeal.** A blanket rate limit will punish
   legitimate translation/link-repair work.
8. **Review at creation is necessary for hoaxes and BLP**, but it must be paired with a fast triage and a
   reviewer pool. The current solo-steward model cannot carry it for high-risk content.
9. **The "stable" state and anti-churn rule need a visible reason taxonomy** so a reviewer can close a
   taste-only proposal without a debate.
10. **The appeals panel needs domain competence for contested history and BLP**, not just procedural review.
