# Reader experience and structured views

**Status:** research note for the 2026-11-04 product-specification pass. Not a spec.
**Scope:** why a reader would use Galactica/T5 instead of an encyclopedia or a chatbot, how an article should
be shaped, how evidence and disagreement stay inspectable, how derived views stay tied to a revision, and
what that costs. **All sources accessed 2026-11-04.**

**Labels:** **[demonstrated]** I opened the policy, spec or paper and verified the claim. **[claimed]** an
operator or vendor asserts it; not independently tested. **[historical/abandoned]** a project that ran and
declined. **[proposed adaptation]** my inference for Galactica/T5. **[open]** could not verify.

**Method:** `web_search` unavailable as stated. Discovery used DuckDuckGo's HTML endpoint, which began
returning a bot challenge partway through; remaining pages came from links inside pages I had already fetched
or from canonical URLs fetched directly. Every page in the table was fetched and read. Numbers taken from a
research-synthesis page whose underlying papers I did not open are marked as such. Load-bearing claims carry a
short-form URL inline; full URLs, labels and lessons for every source are in *Sources checked*.

---

## Top findings

1. **Three reader tasks, stable across studies.** Overview 39–47%, quick fact 25–38%, in-depth 21–29%
   [demonstrated, two independent surveys]. No single article length serves all three; summary-first with
   layered depth is a constraint, not a style choice.

2. **Citations are believed but not clicked.** ~1 in 300 page views (0.29%; 0.56% desktop, 0.13% mobile)
   produces a reference click, and clicks rise on *shorter, lower-quality* pages — readers open evidence when
   the prose failed them [demonstrated]. Evidence behind a drawer nobody opens is not evidence.

3. **Surfacing process lowers measured quality while raising self-reported trust.** Showing editorial discussion
   depressed quality ratings, conflict depressed them further, collaboratively resolved conflict removed the
   penalty; participants did not notice and said it raised their trust [demonstrated].

4. **Placement beats prominence claims by 100×.** Version-history engagement is ~1:500–1,000 page views on
   desktop (link at top) and ~1:50,000–100,000 on mobile (link at bottom); talk pages are ~100× lower where the
   link is hidden from logged-out readers [demonstrated].

5. **The lead does disproportionate work.** 17% of links, 32% of clicks; infobox 4% → 18%; only ~40% of mobile
   readers open any collapsed section [demonstrated]. The first screen is the product.

6. **Derived views should "follow through," not duplicate citations.** Wikipedia's portal practice: derived
   reader surfaces carry no references and link to the sourced article [demonstrated]. Cheapest correct answer to
   "how does a summary stay honest."

7. **Stable revisions are a throughput problem.** German Wikipedia runs sighted revisions on 99.99% of articles;
   English Wikipedia uses pending changes on <0.05% (3,912 of 8,367,837 eligible pages) [demonstrated]. Wikis
   without review capacity downgrade the flag to a banner and a backlog.

8. **Maintenance debt is the binding constraint.** English Wikipedia today: 587,590 pages tagged unsourced,
   362,781 with dead external links, 1,929 still asserting "as of 2015" [demonstrated, live API]. Each new view
   type is another queue of the same shape.

9. **A chatbot cannot be cited — the one task it structurally loses.** In a human audit of four generative search
   engines, 51.5% of sentences were fully supported by their citations and 74.5% of citations supported their
   sentence [demonstrated]. The defensible niche is the citation-grade artifact at a fixed revision.

---

## 1. Why use it instead of an ordinary encyclopedia or a chatbot?

**Findings.** The reader-task evidence cuts against "one great article." The 2017 WWW study combined surveys
with server logs: no dominant motivation (media 30%, conversation 22%, work/school 16%, current events 13%,
"want to learn" 25%, boredom 20%), and shallow needs (overview 39%, quick fact 38%) outnumber deep ones (21%)
[demonstrated, arxiv.org/abs/1702.05379]. The 2019 Wikimedia trust survey on live English Wikipedia reproduced
the split, overview 42–47% [demonstrated, meta.wikimedia.org/wiki/Research:Why_readers_trust_Wikipedia]. Two instruments, two years, same shape. Behaviour tracks task: bored/exploratory readers produce
long, fast, topically scattered sequences; work/school readers dwell on single articles [demonstrated]. Return use
is not one behaviour — the quick-fact reader returns because the answer was one screen away, the overview reader
because the first screen was legible, the deep reader because the article did not dead-end.

On trust the useful output is a taxonomy, not a ranking: prior experience, citations, prose style, risk of
incorrectness, article structure, Wikipedia process, reputational measures, faith [demonstrated]. Citations are
one input of eight, and mean agreement put *clarity* (4.43) and *structure* (4.37) above "adequate number of
references" (4.06) and "high quality sources" (3.97); "written by many people" (3.73) and "reviewed and corrected
by many people" (3.74) came last [demonstrated, 5-point scale]. Process provenance is the cue readers rate
*least*. Note the sample: 94% of first-round respondents trusted the article in front of them "a great deal"/"a
lot" [demonstrated] — self-selected people who clicked a trust survey.

Against chatbots the evidence is narrower than either side claims. The verifiability audit covers generative
*search*, and is the best available estimate of how often a fluent answer is backed by what it points at
[demonstrated]. What a chatbot structurally cannot offer is a stable, addressable, citable artifact: no revision
to cite, no diff, no correction history on the quoted sentence. That is a real task — student, journalist, analyst, agent that must justify a
claim — but a *minority* one, and the majority task is where a chatbot is fastest. Galactica wins on
inspectability and citation stability, loses on latency and convenience, so the reading surface must be fast and
plain while evidence stays one step away.

**Borrow:** task-first entry points (one-screen answer, "go deeper" path, visible-but-unopened evidence
affordance); structure and clarity treated as trust work. **Don't borrow:** the premise that more visible
provenance increases trust (see §3), or that a topic equals one article of one length. **Spec implication:** two
reader-facing renderings from one revision — a self-contained summary surface and the full article — with the
summary derived and declaring its basis (§4); the quick-fact path is a supported surface, not a degraded one.
**Open:** what share of Galactica's audience has the citation task rather than the overview task.

---

## 2. Default article structure and connected exploration

**Findings.** Wikipedia's lead guideline is the best-documented pattern available. The lead must "stand on its
own as a concise overview," identify the topic, establish context, explain notability, summarize the most
important points including prominent controversies, and normally run 1–4 paragraphs; significant information
should not appear in the lead if it is not in the body [demonstrated]. Its rationale cites reader behaviour: the
lead "is the first thing most people read upon arriving at an article, and may be the only portion of the
article that they read" [demonstrated, en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Lead_section].

The layout guideline fixes an order stable since at least 2003: lead, TOC, body, then See also → Notes and
references → Further reading → External links, with categories and navboxes last. The stated rationale is that
outside-work material follows inside-work material and "readers have come to expect the appendices to appear in
this order" [demonstrated]. Ordering conventions become expectations; violating them costs comprehension even
when the new order is more logical.

Exploration is link-driven and top-heavy: lead 17% of links → 32% of clicks, infobox 4% → 18% [demonstrated, via
synthesis]. `Wikipedia:Contents` is a flat "browse by subject" hub mapping its divisions onto existing classifications —
LCC, Dewey, UDC, *Propædia* [demonstrated]. Borrowing a classification beats inventing one.

Orphans are a named defect: "an article with no links from other pages in the main article namespace," still
findable by search but not reachable by links, with a standing de-orphaning workflow and a "walled garden"
category for clusters that only link to each other [demonstrated]. Wikipedia treats orphanhood as a *queue*, not a
publish gate — which is why the queue persists. Portals are the cautionary case: a separate reader-facing
namespace, defended in its own guideline as something that "should promote content," carrying no references
because readers "follow through" to the article, and needing mass-creation rules to keep it from sprawling
[demonstrated].

**Borrow:** a lead genuinely readable as a standalone answer; a fixed, documented element order; subject
browsing on an existing classification; "See also" adjacency; orphan detection as a *publishing gate* (refuse to
publish with no inbound links and no parent topic). **Don't borrow:** banner stacks above the first sentence
(Wikipedia's own order puts deletion/protection/maintenance/dispute tags before the infobox, which is why readers
meet a wall of boxes), separate portal namespaces, infobox-as-content. **Spec implication:** block types get a
canonical order with few required positions (summary first, evidence adjacent to claims, related topics last),
and the summary block must be independently renderable. **Open:** whether a generated-then-reviewed lead stays
adequate as the body changes; whether curated "start here" paths beat link-following.

---

## 3. Inspecting evidence, uncertainty, corrections and disagreement

**Findings.** *Citation engagement is low and conditional.* 0.29% of page views produce a reference click,
rising on shorter and lower-quality pages, favouring recent, open-access and life-event sources
[demonstrated, arxiv.org/abs/2001.08614].
The same group measured external-link CTR at 0.9% (infobox), 0.14% (body), 0.03% (references) [demonstrated, via
synthesis] — a different denominator (see *What I could not verify*).

*"Citation needed" is a dated, tracked queue — an enormous one.* The template takes a `date` parameter and
renders inline [demonstrated]; 587,590 pages currently sit in `Category:All articles with unsourced statements`
[demonstrated]. The date is the design lesson: doubt that records *when* it was raised is a schedulable
obligation; doubt without a date is decoration.

*"As of" is the best small pattern in the corpus.* Each individual, non-contiguous date-sensitive statement must
be tagged separately, precisely so updating one does not silently leave siblings stale; the tag date should be
the source's date, not the edit date; it must not be used for facts that will not change [demonstrated]. Cost is
visible: 1,929 pages still carry "as of 2015" [demonstrated].

*Stable revisions are demonstrated but conditional.* Pending changes shows the last accepted revision to
logged-out readers while logged-in users see the pending one [demonstrated]. Adoption is 99.99% of German
articles versus <0.05% of English eligible pages, and the meta documentation notes that enabling it at scale
"takes a committed community" and that wikis without review capacity end up with an informative banner and a
backlog [demonstrated] — a staffing commitment, not a toggle.

*Surfacing disagreement actively hurts measured quality.* Showing discussion lowered quality ratings, conflict
lowered them further, collaborative resolution removed the penalty; participants "were not generally aware of the
rating-lowering effect" and reported that reading the discussion *raised* their perception of quality
[demonstrated, herbsleb.org/web-pubs/pdfs/towne-yourprocess-2013.pdf]. Read that twice before designing a
disputes panel.

*Corrections must travel with the copy.* Wikipedia's permanent link plus history is weaker than Crossref's
Crossmark: the permalink does not tell you that a *newer* revision corrected it (§4).

**Borrow:** sentence-level anchors (evidence belongs to the claim, not the section); dated "needs evidence"
markers with an owner and an age; per-statement "as of" semantics; a status-of-record object attachable to
exported copies. **Don't borrow:** raw talk pages as the
reader's dispute surface; full history as a default tab; a dispute banner as the primary correction mechanism (a
labour signal, not an information signal, that measurably depresses perceived quality); unbounded tagging
without an ageing policy.

**Spec implication:** three objects that must not be merged — (i) *evidence* (what backs this sentence, how good
is it, can I see the snapshot), inline at sentence level; (ii) *uncertainty* (how confident, since when, what
would change it), a compact always-visible qualifier; (iii) *disagreement* (who disputes what, what was
adjudicated), a summary of adjudication linked to the full record, never the raw thread. **Open:** whether a
visible confidence indicator improves decisions or merely anchors them — the study cited for a compound trust
indicator is unpublished and unread by me [open]; realistic review throughput for a founder-stewarded launch.

---

## 4. Multiple views without changing the factual basis

**Findings.** Mature systems converge on a few mechanisms, none of which is "regenerate from whatever is
current."

*Immutable revision ids.* MediaWiki exposes every revision by stable id and permanent link, so a view can name
exactly what it was built from; the `as of` guideline extends this to *statements*, so a figure carries its
source's date, not the page's [demonstrated]. That distinction — content date versus revision date — is what most
derived systems get wrong.

*"Follow through" rather than duplication.* Derived reader surfaces carry no references and link prominently to
the sourced article [demonstrated, en.wikipedia.org/wiki/Wikipedia:Portal]. One place holds evidence; many places render it.

*Status of record attached to the artifact.* Crossmark treats a correction as metadata about the record,
retrievable from the copy and updatable after distribution [claimed]. The failure mode it avoids: a web-only
corrections page leaves the copy in the reader's hands silently wrong.

*Provenance vocabulary exists and is heavy.* W3C PROV defines provenance as information about entities,
activities and people involved in producing a thing, to support assessments of quality and trustworthiness, with
Entity/Activity/Agent, derivation relations, versioning and "the provenance of provenance" [demonstrated]. Borrow
the vocabulary, not the ontology. Calibration: even Our World in Data says to cite "the page that [the chart] is
found on," with a "last updated" stamp rather than a data-version id [claimed] — best-in-class, still insufficient
to reproduce a figure.

### Views and provenance — a concrete rule [proposed adaptation]

Every derived view (summary, explainer, timeline, table, map, comparison, audio, translation) is an immutable
artifact with its own revision chain and a machine-readable manifest. The manifest is required to publish and is
what a citation resolves to.

| Field | Meaning |
|---|---|
| `view_id`, `view_revision` | stable identity; edits create a new revision, never mutate |
| `view_type` | summary / explainer / timeline / table / map / translation / audio |
| `basis_article`, `basis_revision` | the exact article revision consumed |
| `basis_hash` | hash of the block/claim set actually consumed |
| `claim_ids` | the claims included, enumerated |
| `coverage` | included / total claims in the basis, plus what was omitted |
| `transformations` | ordered: select, summarize, translate, aggregate, project, bin |
| `generator` | agent or human, model/tool and version, recipe id |
| `as_of` | date of the underlying data, distinct from the revision timestamp |
| `review` | reviewer, date, policy version — or `unreviewed` |
| `status` | draft / reviewed / published / stale / superseded |
| `supersedes`, `superseded_by` | the view revision chain |
| `limitations` | free-text uncertainty and known omissions |

Rendering rules, written as testable requirements:

1. **Persistent basis line**, in human text and not behind a disclosure: "Derived from *Article* revision
   `abc1234` (2 Oct 2026). Covers 34 of 51 claims. Generated by *agent*, reviewed by *person*, 3 Oct 2026." If
   unreviewed, the same position and weight says so.
2. **No silent refresh.** When the basis is stale, show a banner naming the intervening revision count and offer
   a diff; never silently re-render onto the new revision.
3. **No new claims.** A view may assert only what its `claim_ids` support; anything else must be proposed as a
   claim in the article, not smuggled in as narration.
4. **Follow through, don't duplicate.** Views carry no independent citation apparatus; they link to claim anchors
   in the basis revision.
5. **Stable, degrading citation.** A view is citable only via an identifier resolving to its manifest and content
   hash, which keeps resolving after supersession; every view has a text or table equivalent and renders at 320
   CSS px.

**Borrow:** PROV's entity/activity/agent vocabulary; MediaWiki revision ids and permanent links; follow-through;
Crossmark's status-of-record; the `as of` content-date/revision-date split. **Don't borrow:** full PROV
serialization; a corrections page as the only correction channel; "cite the page" targets. **Spec implication:**
the manifest is a schema object specified alongside the revision schema. `coverage` is the field most likely to
be dropped and the one that most affects honesty — a summary covering 20% of claims and one covering 90% look
identical without it. **Open:** whether readers understand a coverage percentage or it invites false precision;
whether review attaches to each artifact or to the generator recipe.

---

## 5. Language editions, reading levels, personalized explanations

**Findings.** Simple English Wikipedia is the best-documented reading-level variant and it is a **fork**, not a
rendering mode [demonstrated, simple.wikipedia.org/wiki/Wikipedia:About]. Its policy says articles use fewer words and simpler grammar, serving learners, children and
adults with learning difficulties, and — decisively — that "most Simple English articles take articles from
other Wikipedias and make them simple; they are usually not new articles" [demonstrated]. It has 286,395
articles against English Wikipedia's 7,259,287 [demonstrated] — a fork at roughly 1:25, with permanent drift:
the simple article is not tied to the revision it was simplified from. It recommends bidirectional interwiki
links so readers can move between versions [demonstrated], which is the part worth copying.

MT in production is gated on *modification*, not detection. Wikimedia's Content Translation provides MT as "a
starting point for the user to actively review and correct"; warns that unmodified MT is likely to be deleted;
shows warnings when a user tries to publish unmodified content; and tracks how much the initial MT was modified,
using it to encourage review or prevent publishing [demonstrated, mediawiki.org/wiki/Help:Content_translation].
That modification-ratio gate is the most transferable mechanism I found.

Our World in Data takes the opposite stance: translations permitted, but the translator must state the result is
"not official or authorized... nor endorsed in any way" [claimed]. Wikimedia builds a gate; OWID disclaims and
links back. The incoherent position is a translation that looks official and has no reviewer.

On personalization the evidence is negative by omission: the reader research is about tasks, trust cues and
navigation, not per-reader explanation. Nothing I read demonstrates that personalized explanations improve
comprehension or trust, and the transparency experiments show perception moves easily in the wrong direction.
Per-reader rewriting of the factual layer looks like unjustified risk.

**Borrow:** reading-level variants as *views* over one claim base, labelled and linked, not separate wikis; a
modification-ratio gate plus publish warnings for MT; explicit unofficial-translation labelling with a link to
the canonical revision; bidirectional links between variants. **Don't borrow:** a separate simplified edition
with its own community and facts; unlabelled MT; per-reader rewriting of claims. **Spec implication:** language
is a property of the *view*, with `basis_revision` and a reviewer per language; unreviewed MT may exist but not
be presented as equivalent; record the modification ratio so "reviewed" means something. **Open:** whether
automatic simplification can be constrained to preserve claim-level meaning (no evaluation found); whether
readers of small editions prefer reviewed-but-stale or unreviewed-but-current — the German/English
flagged-revision split suggests this is culturally variable.

---

## 6. Accessibility and mobile

**Findings.** WCAG 2.2 adds criteria that land on a reference site's chrome and its data views [demonstrated,
W3C Recommendation, w3.org/TR/WCAG22/]:

- **2.4.11 Focus Not Obscured (Minimum), AA** — a focused component must not be *entirely* hidden by
  author-created content; sticky headers and floating drawers are the usual offenders, so a persistent citation
  drawer is a textbook risk (2.4.12/2.4.13 tighten this and the focus indicator at AAA).
- **2.5.8 Target Size (Minimum), AA** — targets ≥24×24 CSS px, with spacing, inline and user-agent exceptions.
  Inline citation superscripts qualify as inline; the drawer's close button does not.
- **1.4.10 Reflow, AA** — must work at 320 CSS px (1280px at 400% zoom) without two-dimensional scrolling,
  *except* content requiring 2D layout, explicitly including "data tables (not individual cells)" and maps
  [demonstrated].
- **3.2.6 Consistent Help, 3.3.7 Redundant Entry, 3.3.8 Accessible Authentication (Minimum)** are new AA criteria
  [names and levels verified from the spec's contents; full normative text not read].

The reflow exemption is the key operational fact for §7: a wide table or map may scroll in two dimensions, but
must not lose information and must remain usable at 320px.

Tables are a graduated problem. WAI defines four levels — one header, two headers, irregular headers (spanning
cells needing `colgroup`/`rowgroup` and `scope` ranges), and multi-level headers (needing explicit `headers`/`id`)
— and requires header cells marked up as `<th>` with scope for assistive technology to convey relationships
[demonstrated]. Complexity is permitted; it is paid for in markup and screen-reader verbosity.

Mobile is the majority context and structurally different: 63–65% of trust-survey respondents were on the mobile
site [demonstrated], and Wikipedia moves the lead's first paragraph *above* the infobox "for the sake of
readability" [demonstrated]. Sections below the lead collapse by default on phones; only 39.9% of non-tablet
mobile readers opened one [demonstrated, one-day sample], and history is effectively invisible there
(1:50,000–100,000) [demonstrated]. Desktop layout stays contentious even when it tests better:
Vector 2022's sticky TOC was claimed to improve readability, yet adoption required an RfC and a user-configurable
width toggle [claimed for the benefit; demonstrated for the RfC].

Offline access is real and commercially invisible. Kiwix packages free knowledge for offline use, claiming 10M+
users in 212+ countries and 100+ languages against "50% of the world lacks reliable internet access" [claimed].
The counter-example instructs: Wikipedia Zero waived mobile data costs via 97 operators in 72 countries, reaching
800M+ people, and was discontinued in February 2018 [historical/abandoned]. Carrier-deal distribution was
politically fragile; offline and small-payload design was not.

**Borrow:** WCAG 2.2 AA as the floor, with 2.4.11 and 2.5.8 named explicitly because the citation drawer and
inline anchors are where they bite; lead-above-infobox on narrow screens; `th`/`scope` from the start; a text
equivalent for every timeline and map. **Don't borrow:** fixed-width layouts without a control; JS-dependent
reading; hiding history/talk affordances on mobile "because mobile users don't use them" — the evidence says they
do not use them *because they are hidden*. **Spec implication:** conformance stated as WCAG 2.2 AA with named
criteria, not aspiration; map/timeline views are blocked from `published` until an accessible fallback exists.
**Open:** whether a citation drawer can satisfy 2.4.11 on small screens at all; how offline packaging carries
per-view manifests — no example found of an offline package that carries revision provenance.

---

## 7. When structured views are worth it

**Findings.** The costs are documented, mostly as backlogs: 1,929 pages still asserting "as of 2015" despite an
explicit per-statement rule; 362,781 pages with dead external links; 587,590 with unsourced statements; a standing
de-orphaning workflow for a defect a publish gate would have prevented; and a portal namespace its own guidance
must defend and fence [all demonstrated].

Some views are cheap because the data already exists as structure. A **table over claims** — value, unit, as-of
date, source, confidence — is nearly free once claims are typed, accessible by construction if marked up
properly, machine-checkable, and diffable. A **timeline over dated claims** is cheap *only* if dates are already
claim fields; assembled by hand from prose it is a permanent editing obligation with no verification path. A
**map** needs geodata with licensing, projections, a fallback and an owner for boundary changes — the most
expensive view per unit of reader value I saw in any of these systems.

**Borrow:** tables over typed claims first; timelines only where dates are structured; "as of" semantics on every
cell that can go stale; publish gates instead of queues. **Don't borrow:** hand-curated narrative timelines,
decorative maps, or any view type without a named maintenance owner and an ageing policy. **Spec implication:**
sequence the types — tables now, timelines when dates are fields, maps and audio deferred — and each admitted type
ships with its maintenance contract (who refreshes it, how staleness is detected, what happens on supersession).
**Open:** whether readers use timelines and maps enough to justify their cost; I found no usage data.

---

## Sources checked

| URL | What it is | Label | Lesson | Access |
|---|---|---|---|---|
| https://arxiv.org/abs/1702.05379 | Singer et al., *Why We Read Wikipedia*, WWW'17 | demonstrated | Three-task split; shallow 39%/38% vs deep 21% | 2026-11-04 |
| https://meta.wikimedia.org/wiki/Research:Why_readers_trust_Wikipedia | Wikimedia/Drexel trust study, 2019 | demonstrated | 8 trust families; clarity 4.43 & structure 4.37 outrank references 4.06 | 2026-11-04 |
| https://meta.wikimedia.org/wiki/Research:Which_parts_of_an_article_do_readers_read | Synthesis on which parts get read | demonstrated | Lead 17% of links → 32% of clicks; infobox 4% → 18% | 2026-11-04 |
| https://meta.wikimedia.org/wiki/Research:Understanding_Curious_and_Critical_Readers | Project on critical reading | demonstrated | Talk/history as trust affordances; transparency can *lower* trust | 2026-11-04 |
| https://meta.wikimedia.org/wiki/Research:Understanding_Curious_and_Critical_Readers/Reader_interactions_with_talk-pages_and_version-history | Log analysis of talk/history | demonstrated | History 1:500–1,000 desktop vs 1:50k–100k mobile; placement drives 100× | 2026-11-04 |
| https://arxiv.org/abs/2001.08614 | Piccardi et al., citation engagement, WWW'20 | demonstrated | 0.29% of page views → reference click; higher on short/low-quality pages | 2026-11-04 |
| https://par.nsf.gov/servlets/purl/10038301 | Towne et al., *Your process is showing*, CSCW'13 | demonstrated | Surfacing deliberation lowered quality ratings; resolved conflict removed penalty | 2026-11-04 |
| https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Lead_section | Lead style guideline | demonstrated | Lead stands alone; 1–4 paragraphs; may be the only part read | 2026-11-04 |
| https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Layout | Layout guideline | demonstrated | Fixed order since 2003; mobile moves lead above infobox | 2026-11-04 |
| https://en.wikipedia.org/wiki/Wikipedia:Orphan | De-orphaning how-to | demonstrated | Orphan = no inbound links; queue rather than publish gate | 2026-11-04 |
| https://en.wikipedia.org/wiki/Wikipedia:Contents | Subject-browse hub | demonstrated | Start-here browsing on LCC/Dewey/UDC, not an invented taxonomy | 2026-11-04 |
| https://en.wikipedia.org/wiki/Wikipedia:Portal | Portal information page | demonstrated | "Follow through": derived surfaces carry no references | 2026-11-04 |
| https://en.wikipedia.org/wiki/Wikipedia:Pending_changes | Pending-changes policy | demonstrated | Accepted revision shown to public; pending saved and marked | 2026-11-04 |
| https://meta.wikimedia.org/wiki/Flagged_Revisions | FlaggedRevs documentation | demonstrated | de.wiki 99.99% vs en.wiki <0.05% (3,912 of 8,367,837) | 2026-11-04 |
| https://en.wikipedia.org/wiki/Wikipedia:Citation_needed | Inline tag page | demonstrated | Dated inline doubt → schedulable obligation; 587,590 pages tagged | 2026-11-04 |
| https://en.wikipedia.org/wiki/Wikipedia:As_of | "As of" guideline | demonstrated | Per-statement dating; source date not edit date; 1,929 pages at 2015 | 2026-11-04 |
| https://www.w3.org/TR/WCAG22/ | W3C WCAG 2.2 | demonstrated | 2.4.11 AA; 2.5.8 AA 24px; 1.4.10 reflow with table/map exemption | 2026-11-04 |
| https://www.w3.org/WAI/tutorials/tables/ | WAI tables tutorial | demonstrated | Four complexity levels; `th`+`scope`; `headers`/`id` | 2026-11-04 |
| https://www.mediawiki.org/wiki/Help:Content_translation | Content Translation help | demonstrated | MT gated on modification ratio; unmodified MT likely deleted | 2026-11-04 |
| https://simple.wikipedia.org/wiki/Wikipedia:About | Simple English project page | demonstrated | Simplified fork; 286,395 vs 7,259,287 articles | 2026-11-04 |
| https://www.kiwix.org/en/ | Kiwix homepage | claimed | Offline packaging; "50% lack reliable internet" | 2026-11-04 |
| https://foundation.wikimedia.org/wiki/Archive:Wikipedia_Zero | WMF archive | historical/abandoned | 97 operators, 800M people; discontinued Feb 2018 | 2026-11-04 |
| https://www.crossref.org/services/crossmark/ | Crossref Crossmark | claimed | Status-of-record attached to the artifact, incl. PDFs | 2026-11-04 |
| https://ourworldindata.org/faqs | OWID FAQs | claimed | Cite the *page*, not a data version; label unofficial translations | 2026-11-04 |
| https://www.w3.org/TR/prov-overview/ | W3C PROV overview | demonstrated | Entity/Activity/Agent; versioning | 2026-11-04 |
| https://arxiv.org/abs/2304.09848 | Liu et al., generative search verifiability, EMNLP'23 | demonstrated | 51.5% of sentences fully supported; 74.5% of citations support sentence | 2026-11-04 |
| https://en.wikipedia.org/wiki/Wikipedia:Vector_2022 | Vector 2022 skin page | demonstrated | Sticky TOC; fixed width forced an RfC and a toggle | 2026-11-04 |
| https://en.wikipedia.org/w/api.php | Live MediaWiki API queries | demonstrated | 7,259,287 articles; 587,590 unsourced; 362,781 dead links | 2026-11-04 |

---

## What I could not verify

- **Kuznetsov et al., "Templates and Trust-o-meters" (2020)** — cited by the Wikimedia research page for the claim
  that a compound trust indicator moves readers toward true quality. Listed as unpublished there; not obtained.
  Do not treat "a trust indicator improves judgement" as established.
- **Kittur, Suh & Chi, "Can you ever trust a wiki?" (CSCW 2008)** — read only a third-party summary, not the paper.
  Its claim that trust signals moved ratings in *both* directions is consistent with Towne et al. but unverified.
- **Primary studies behind the "which parts of an article" synthesis** (Paranjape WSDM'16; Lamprecht 2015/2016;
  Dimitrov WWW'16; Piccardi WWW'21). I read the synthesis, so the 32%/18% click shares and 0.03%/0.14%/0.9% CTRs
  are second-hand.
- **Reconciliation of reference-click rates** — 0.29% per page view versus 0.03% per reference-link impression:
  same group, different denominators, no reconciling source. Quote neither without its denominator.
- **Reader usage of Wikipedia's timeline and map surfaces** — no data. "Maps are expensive per unit of value" is
  an inference from maintenance structure, not a measured cost-benefit.
- **Automatic reading-level simplification preserving claim-level meaning** — no evaluation found either way.
- **Scale of the English Wikipedia portal namespace** — the guideline is defensive about maintenance, but I did not
  count surviving portals; my framing rests on tone, not a count.
- **Search coverage** — DuckDuckGo returned a bot challenge for the last third of the session, so later discovery
  relied on in-page links and canonical URLs. Cross-language reader-motivation work and Wikimedia Diff posts on
  reader research were not reached; absence of a finding is not evidence of absence.
- **Blocked page** — `business.columbia.edu` returned HTTP 403 for the ChatGPT/Wikipedia traffic brief; no
  alternative copy pursued, so no claim about chatbot-driven traffic decline appears above.
