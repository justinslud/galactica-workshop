"""Demonstration content. ALL ARTICLES ARE LABELLED DEMONSTRATION DRAFTS, not verified reference articles.

Sources: each entry records how it was checked. 'opened' means a page was read on the retrieval date. 'metadata' means only
a DOI or citation record was resolved, or the source was known only through a secondary summary. Claims that rest on
metadata-only or secondary sources are written as such. Claims with no source carry a [needs source] marker.
"""
import uuid
from datetime import date

RETRIEVED = date(2026, 10, 28)
NAMESPACE = uuid.UUID('6f1c2b8e-3d4a-4f5e-9a7b-1e2d3c4b5a69')

SOURCES = {
    'wiki-svr': dict(
        title='Subvocal recognition', url='https://en.wikipedia.org/wiki/Subvocal_recognition', kind='encyclopedia',
        publisher='Wikipedia', published_on='accessed 2026-10-28', check_status='opened',
        retrieval_note='Fetched 2026-10-28 (oldid 1370969221). Secondary summary; the primary sources it cites were not all opened.'),
    'denby-2010': dict(
        title='Silent speech interfaces', url='https://doi.org/10.1016/j.specom.2009.08.002', kind='paper',
        authors='Denby, Schultz, Honda, Hueber, Gilbert, Brumberg', publisher='Speech Communication 52(4), 270-287',
        published_on='2010', check_status='metadata',
        retrieval_note='DOI resolved to citation metadata on 2026-10-28. Full text not read.'),
    'alterego-2018': dict(
        title='AlterEgo: A Personalized Wearable Silent Speech Interface', url='https://doi.org/10.1145/3172944.3172977',
        kind='paper', authors='Kapur, Kapur, Maes', publisher='IUI 2018, pp. 43-53', published_on='2018',
        check_status='metadata',
        retrieval_note='DOI resolved to citation metadata on 2026-10-28. Full text not read; sensing details unverified.'),
    'pei-2011': dict(
        title='Decoding vowels and consonants in spoken and imagined words using electrocorticographic signals in humans',
        url='https://doi.org/10.1088/1741-2560/8/4/046028', kind='paper', authors='Pei, Barbour, Leuthardt, Schalk',
        publisher='Journal of Neural Engineering 8(4) 046028', published_on='2011', check_status='metadata',
        retrieval_note='Known through the Wikipedia reference list. DOI not resolved.'),
    'newscientist-2002': dict(
        title='Lip-reading cellphone silences loudmouths', kind='web', authors='Fitzpatrick, M.', publisher='New Scientist',
        published_on='2002', check_status='metadata', retrieval_note='Cited through Wikipedia. Not opened.'),
    'nbc-2008': dict(
        title="Army developing 'synthetic telepathy'", kind='web', publisher='NBC News', published_on='13 Oct 2008',
        check_status='metadata', retrieval_note='Cited through Wikipedia. Not opened.'),
    'buterin-2018': dict(
        title='A Flexible Design for Funding Public Goods', url='https://arxiv.org/abs/1809.06421', kind='paper',
        authors='Vitalik Buterin, Zoe Hitzig, E. Glen Weyl',
        publisher='arXiv:1809.06421 (earlier title: Liberal Radicalism: A Flexible Design For Philanthropic Matching Funds); Management Science 65(11), 2019',
        published_on='2018 (v1); revised 2020', check_status='metadata',
        retrieval_note='Abstract page read 2026-10-28. Full text not read; matching-pool and collusion details unverified.'),
    'wiki-qv': dict(
        title='Quadratic voting', url='https://en.wikipedia.org/wiki/Quadratic_voting', kind='encyclopedia',
        publisher='Wikipedia', published_on='accessed 2026-10-28', check_status='opened',
        retrieval_note='Fetched 2026-10-28 (oldid 1371200400). Its quadratic-funding section is flagged by Wikipedia as needing better sources.'),
    'wiki-eg': dict(
        title='Encyclopedia Galactica', url='https://en.wikipedia.org/wiki/Encyclopedia_Galactica', kind='encyclopedia',
        publisher='Wikipedia', published_on='accessed 2026-10-28', check_status='opened',
        retrieval_note='Fetched 2026-10-28 (oldid 1360654560). Secondary summary of Asimov and later uses.'),
    'wein-wells': dict(
        title='HG Wells and the Golden Age of Science Fiction (ch. 4, pp. 25-26)', kind='book', authors='Theodore Wein',
        check_status='metadata', retrieval_note='Cited through Wikipedia. Not opened.'),
    'holby-1942': dict(
        title='The Strange Case of the Missing Hero', kind='web', authors='Frank Holby', publisher='Astounding Science Fiction',
        published_on='July 1942', check_status='metadata',
        retrieval_note='Cited through Wikipedia (Historical Dictionary of Science Fiction). Not opened.'),
    'adams-1979': dict(
        title="The Hitchhiker's Guide to the Galaxy", kind='book', authors='Douglas Adams', published_on='1979',
        check_status='metadata', retrieval_note='Quoted through Wikipedia. Not opened.'),
    'sagan-1980': dict(
        title='Cosmos', kind='book', authors='Carl Sagan', published_on='1980', check_status='metadata',
        retrieval_note='Cited through Wikipedia. Not opened.'),
    'foundation-1942': dict(
        title='Foundation (short story, Astounding Science Fiction, May 1942)', kind='other', authors='Isaac Asimov',
        check_status='metadata', retrieval_note='Known through the Wikipedia summary. Not opened.'),
}


def bid(slug, position):
    """Stable block id derived from article and position, so reseeding produces the same ids."""
    return str(uuid.uuid5(NAMESPACE, f'{slug}#{position}'))


# ----- Subvocal interfaces -----------------------------------------------------------------------------

SUBVOCAL = dict(
    slug='subvocal-interfaces',
    title='Subvocal interfaces',
    opening=('A subvocal interface tries to turn silent or near-silent speech movements into text or commands. '
             'Research prototypes read muscle, tongue, lip or throat signals. This is a demonstration draft, '
             'not a verified reference article.'),
    blocks=[
        {'kind': 'markdown', 'data': {'text': """## What a subvocal interface is

A **silent speech interface** lets a person communicate without producing audible sound. The Wikipedia summary of the field describes it as a device that identifies the phonemes a person pronounces from non-auditory information about speech movements, then uses that information to recreate speech.

The output of the process is called **subvocal recognition** (SVR): the conversion of subvocalization into a digital form, either aural or text-based.

<details>
<summary>Why the terminology is unsettled</summary>

Silent speech, subvocalization and non-audible murmur are used in overlapping ways. This draft uses *silent speech interface* for the field and *subvocal* for systems that read small articulatory or muscle signals. That is a drafting choice, not a settled taxonomy.

</details>"""}},
        {'kind': 'markdown', 'data': {'text': """## How the signals are captured

The Wikipedia summary lists several input families. Ultrasound and optical cameras track tongue and lip movement. Electromagnetic devices track the same articulators. Electromyography records electrical activity in speech muscles and the larynx. Another source is the vocal-tract resonance that travels through bone, called non-audible murmur. The most invasive family reads motor-cortex activity through intracortical microelectrodes.

Each family trades comfort for signal quality. Camera and magnetic methods need equipment near the mouth. Muscle sensors can be worn. Intracortical electrodes require surgical implantation. [needs source: comparison of accuracy across these families]"""}},
        {'kind': 'markdown', 'data': {'text': """## Milestones

- **2002.** NTT DoCoMo announced a silent mobile phone that used electromyography and imaging of lip movement, citing the goal of ridding public places of noise.
- **2008.** NBC News reported Army-funded research into "synthetic telepathy" using subvocalization at the University of California, Irvine.
- **2010.** Denby and colleagues published a review of silent speech interfaces in *Speech Communication*.
- **2011.** Pei and colleagues reported decoding vowels and consonants from spoken and imagined words using electrocorticographic signals.
- **2018.** Kapur, Kapur and Maes presented AlterEgo at IUI 2018. Some secondary summaries date it 2019."""}},
        {'kind': 'markdown', 'data': {'text': """## AlterEgo and the publication record

The best-known recent prototype is AlterEgo. In 2019, Arnav Kapur and colleagues described it as a system that reads neural signals linked to speech and translates intended words into text or commands. The paper was published as a personalized wearable silent speech interface at IUI 2018. The paper itself was not opened for this draft, so its sensing details and accuracy figures are unverified here.

<details>
<summary>Disagreement: 2018 or 2019?</summary>

The Wikipedia summary gives AlterEgo's study as 2019. The DOI record for the IUI paper gives 2018, pages 43 to 53. This revision (r1) keeps the summary's date and is pending correction, so the article contradicts its own milestone list until that change is decided.

</details>"""}},
        {'kind': 'markdown', 'data': {'text': """## Uses and limits

Silent speech may aid people who cannot produce voiced speech, for example after a laryngectomy. It can carry communication when background noise or breathing apparatus drowns out speech. It also allows silent communication where privacy matters, including some military and security settings.

The limits matter as much. The sources describe working prototypes, not general-purpose products. The AlterEgo title stresses personalization, which suggests calibration to each user matters, but the paper was not read here. No source in this draft establishes accuracy for everyday speech. [needs source]

<details>
<summary>Privacy and consent</summary>

A device that reads articulatory signals can capture intent before a user speaks aloud. Who may read those signals, and whether bystanders can consent, are open questions. No source in this draft addresses them. [needs source]

</details>"""}},
        {'kind': 'markdown', 'data': {'text': """## In fiction

Silent computer speech appears often in science fiction. In Arthur C. Clarke's story and Stanley Kubrick's film *2001: A Space Odyssey*, the computer HAL 9000 learns of a plot against it by lip reading the astronauts. Orson Scott Card describes an ear implant, called a "jewel", that allows subvocal communication with computers. These stories shaped public expectations. They say nothing about what current hardware can do.

## Open questions

- How accurate are these systems outside lab conditions? [needs source]
- Which signals can be read without surgery, and at what error rate? [needs source]
- What consent rules should apply to reading signals from people who have not chosen to speak aloud? [needs source]"""}},
    ],
    citations=[
        (0, 'wiki-svr', 'Definitions: silent speech interface and subvocal recognition (SVR).',
         'Subvocal recognition (SVR) is the process of taking subvocalization and converting the detected results to a digital output, aural or text-based.'),
        (1, 'denby-2010', 'Overview of silent speech input families (review; metadata only).', ''),
        (1, 'wiki-svr', 'The input-methods section lists these families.', ''),
        (2, 'wiki-svr', 'The 2002, 2008 and 2011 milestones, as summarized there.', ''),
        (2, 'newscientist-2002', '2002 silent phone announcement (cited through Wikipedia).', ''),
        (2, 'nbc-2008', '2008 Army synthetic telepathy report (cited through Wikipedia).', ''),
        (2, 'denby-2010', '2010 review of silent speech interfaces.', ''),
        (2, 'pei-2011', '2011 decoding study (cited through Wikipedia).', ''),
        (2, 'alterego-2018', '2018 IUI publication date.', ''),
        (3, 'alterego-2018', 'IUI 2018 paper: personalized wearable silent speech interface, pages 43-53.', ''),
        (3, 'wiki-svr', 'Summary of AlterEgo as reading neural signals (that summary gives 2019).', ''),
        (4, 'wiki-svr', 'Uses: laryngectomy, noise, privacy, military or security operations.', ''),
        (5, 'wiki-svr', 'In fiction: HAL 9000 lip reading; Orson Scott Card ear implant.', ''),
    ],
)

# ----- Quadratic funding -------------------------------------------------------------------------------

QUADRATIC = dict(
    slug='quadratic-funding',
    title='Quadratic funding',
    opening=('Quadratic funding (QF) divides matching money among public-goods projects so that many small '
             'contributions count for more than a few large ones. It was proposed by Vitalik Buterin, Zoe Hitzig and '
             'E. Glen Weyl and extends ideas from quadratic voting. This is a demonstration draft: the formula comes '
             'from the paper abstract, and claims about deployments are secondary.'),
    blocks=[
        {'kind': 'markdown', 'data': {'text': """## The rule

The 2018 working paper (arXiv:1809.06421, cited in older sources as *Liberal Radicalism: A Flexible Design For Philanthropic Matching Funds*) states the core rule in its abstract. The amount a project receives is proportional to the square of the sum of the square roots of its contributions. Under what the authors call the standard model, this yields first-best provision of public goods.

The abstract is the only part of the paper this draft has read. Matching-pool sizing, normalization and collusion variants are discussed in the full paper, and this draft does not yet summarize them. [needs source: full-text summary]

<details>
<summary>Worked example (arithmetic, not from the paper)</summary>

Suppose one donor gives 4 units to a project. The square root of 4 is 2, and squaring gives 4. Suppose four donors each give 1 unit. The square roots sum to 4, and squaring gives 16. The same 4 units of money carry four times the weight when spread across four people. This applies the abstract's rule; the paper's own examples may differ.

</details>"""}},
        {'kind': 'image', 'data': {
            'src': '/static/img/qf-diagram.svg',
            'alt': 'Two bars of the same total money: four 1-unit donors give weight 16, one 4-unit donor gives weight 4',
            'caption': 'Illustrative diagram of the square-root rule, drawn for this demonstration. It is not a figure from any source.',
            'credit': 'Galactica demonstration draft, original drawing',
        }},
        {'kind': 'markdown', 'data': {'text': """## Relation to quadratic voting

Quadratic voting, associated with E. Glen Weyl, lets a voter buy several votes on one issue at a cost that rises with the square of the number of votes. One vote costs 1 credit, two cost 4 and three cost 9. The motivation is the tyranny of the majority: under one-person-one-vote, an intense minority can be outvoted by an indifferent majority.

Quadratic funding borrows the intuition for money. Contributors fund projects, and a matching pool rewards projects with broad support. The abstract says the design extends ideas from quadratic voting to a funding mechanism. The table compares the three rules on the points this draft needs."""}},
        {'kind': 'table', 'data': {
            'caption': 'Three counting rules compared (cells summarize the sources; see evidence)',
            'headers': ['Rule', 'What is counted', 'Cost or weighting rule', 'Main concern named in the sources'],
            'rows': [
                ['One-person-one-vote', 'One vote per person', 'None', 'Majorities can outvote intense minorities (Wikipedia motivation summary).'],
                ['Quadratic voting', 'Votes bought with credits', 'k votes cost k squared credits', 'Wealth can distort outcomes if real money is used (Wikipedia, payment section).'],
                ['Quadratic funding', 'Contributions to projects', 'Project amount proportional to (sum of square roots) squared', 'Depends on matching-pool design and collusion; full paper not summarized here [needs source].'],
            ],
        }},
        {'kind': 'markdown', 'data': {'text': """## Deployments

The Wikipedia summary says the Gitcoin Grants initiative is an early adopter of quadratic funding, and that its implementation differs from the original scheme in several ways. It also reports that the initiative had distributed more than $60 million to over 3,000 open-source projects as of 2022. That figure is attributed to Gitcoin through a secondary source and has not been checked against Gitcoin's own records. [needs source: primary Gitcoin data]

Quadratic voting, the closer relative, has a more documented record. A 2019 experiment in the Colorado House Democratic caucus used it to set legislative priorities among 107 bills. The winning bill received 60 votes, and no member spent all 100 virtual tokens on one bill."""}},
        {'kind': 'markdown', 'data': {'text': """## Disagreements and limits

Quadratic schemes draw two recurring objections. The first is wealth. Willingness to pay tracks wealth as well as preference, so wealthier participants can buy more influence. The Wikipedia summary describes this objection and mitigations such as artificial currencies and income return schemes. Whether those transfer to quadratic funding is not settled here. [needs source]

The second is collusion. The summary reports that quadratic voting is about as sensitive to collusion as one-person-one-vote, and much less sensitive than Vickrey-Clarke-Groves style mechanisms. Neither point has been verified for funding rounds specifically. [needs source]

<details>
<summary>Where the framings differ</summary>

The abstract presents the design as a resolution of the liberal-communitarian debate that provides neutral rules supporting collective organization. The Wikipedia summary describes the original scheme as a way to approach optimal public-goods provision without a centralized legislature. These are compatible, but they stress different things. Read the paper before relying on either framing.

</details>"""}},
        {'kind': 'markdown', 'data': {'text': """## Open questions

- How should a matching pool be sized relative to contributions? [needs source]
- Do small projects fare well when the pool is fixed? [needs source]
- How often do rounds need manual review for suspected collusion? [needs source]"""}},
    ],
    citations=[
        (0, 'buterin-2018', 'Core rule: amount received proportional to the square of the sum of square roots of contributions; first-best claim under the standard model.',
         'The amount received by the project is (proportional to) the square of the sum of the square roots of contributions received.'),
        (2, 'wiki-qv', 'Quadratic voting: vote-cost rule and the tyranny-of-the-majority motivation.', ''),
        (3, 'wiki-qv', 'Quadratic voting cost rule; payment-section objection (table row for quadratic voting).', ''),
        (3, 'buterin-2018', 'Quadratic funding row: abstract rule (full paper not read).', ''),
        (4, 'wiki-qv', 'Gitcoin early adoption and differing implementation; $60 million figure attributed to Gitcoin; Colorado 2019 experiment.', ''),
        (5, 'wiki-qv', 'Payment section: wealth objection and mitigations; robustness: collusion sensitivity.', ''),
        (5, 'buterin-2018', 'Abstract: neutral rules and the liberal-communitarian framing.', ''),
    ],
)

# ----- Encyclopedia Galactica ---------------------------------------------------------------------------

ENCYCLOPEDIA = dict(
    slug='encyclopedia-galactica',
    title='Encyclopedia Galactica',
    opening=('Encyclopedia Galactica is the name of fictional encyclopedias that hold the accumulated knowledge of a '
             'galaxy-spanning civilization. Isaac Asimov\'s version first appears in 1942 and is named in the 1951 novel. '
             'This is a demonstration draft that summarizes secondary sources and does not replace them.'),
    blocks=[
        {'kind': 'markdown', 'data': {'text': """## Asimov's encyclopedia

The Encyclopedia first appears in Isaac Asimov's short story "Foundation", published in *Astounding Science Fiction* in May 1942. In the story it is a compendium of everything known in the Galactic Empire. It is meant to preserve that knowledge in a remote region of the galaxy against a foreseen catastrophe. The story later reveals its real purpose: to gather a group of scientists on Terminus, a remote, resource-poor planet, so that a stagnant empire can be revitalized.

In the story the Encyclopedia begins as a physical work and later becomes computerized and subject to continual change. That detail matters for any reference that keeps changing: it still needs a record of what it said and why it changed."""}},
        {'kind': 'markdown', 'data': {'text': """## A device for chapter openings

Asimov uses extracts from the Encyclopedia as epigraphs that open many sections and chapters of the Foundation series. Each extract introduces a key character or event, giving the reader a hazy idea of what is to come. Critics read the device as paratext: material around the story that frames how it should be read.

<details>
<summary>A possible older source: H. G. Wells</summary>

Theodore Wein suggests the Encyclopedia may have been inspired by a passage in H. G. Wells's *The Shape of Things to Come* (1933). Wells describes an encyclopaedic organization centred on Barcelona, tasked with building a "Fundamental Knowledge System". Wein's suggestion concerns influence and is not a documented statement of Asimov's intent.

</details>"""}},
        {'kind': 'timeline', 'data': {
            'title': 'Dates in the Encyclopedia Galactica record',
            'events': [
                {'date': '1933', 'text': "H. G. Wells's The Shape of Things to Come describes an encyclopaedic organization (possible influence, per Wein)."},
                {'date': 'May 1942', 'text': 'Foundation appears in Astounding Science Fiction. The story calls the work "the Encyclopedia"; the full name comes later.'},
                {'date': 'July 1942', 'text': 'Frank Holby\'s "The Strange Case of the Missing Hero" uses the term; the Historical Dictionary of Science Fiction credits it as the first use.'},
                {'date': '1951', 'text': 'The fix-up novel Foundation gives the Encyclopedia its name.'},
                {'date': '1978', 'text': 'Encyclopedia Galactica: from the Fleet Library aboard the Battlestar Galactica is published as a tie-in.'},
                {'date': '1979', 'text': 'Douglas Adams contrasts The Hitchhiker\'s Guide with "the great Encyclopaedia Galactica".'},
                {'date': '1980', 'text': 'Carl Sagan uses the term in Cosmos for a store of extraterrestrial knowledge.'},
                {'date': '1989', 'text': "Orson Scott Card's short story The Originist mentions an Encyclopedia of the Galactic Empire."},
            ],
        }},
        {'kind': 'markdown', 'data': {'text': """## Later uses

Writers have reused the device widely. Arthur C. Clarke and Gentry Lee mention an Encyclopedia Galactica in *Rama II* (1989). Robert A. Heinlein refers to it in *To Sail Beyond the Sunset* (1987). The term appears in films such as *The Arrival* (1996) and *Contact* (1997), and in comics set in future histories. Outside fiction, a 1993 video series distributed in Australia used the title, and Carl Sagan's 1980 use is the best-known non-fictional example."""}},
        {'kind': 'markdown', 'data': {'text': """## Disagreement about the first use

The Wikipedia summary says Frank Holby used the term first, in July 1942, while Asimov's May 1942 story did not use the name at that point. Read carefully, the two claims are compatible: the story existed before the name did. A reader who assumes Asimov coined the name in 1942 will be wrong. [needs source: primary text of the 1951 novel]"""}},
        {'kind': 'markdown', 'data': {'text': """## Editorial note (not sourced)

The Encyclopedia is a useful model for a public reference that must stay trustworthy across many revisions. It is fiction, so its contents are invented and it teaches little about verification. The narrower lesson this wiki takes is that a reference should record what it said, when, and why it changed. That is why this demonstration article keeps its history visible."""}},
        {'kind': 'markdown', 'data': {'text': """## Open questions

- What did the 1951 novel's version of the Encyclopedia say about its own methods? [needs source]
- How do modern wikis preserve revision history for readers? [needs source]"""}},
    ],
    citations=[
        (0, 'wiki-eg', 'First appearance (May 1942), purpose, Terminus plot, later computerization.',
         'Encyclopedia Galactica first appeared in Isaac Asimov\'s short story "Foundation" (Astounding Science Fiction, May 1942)'),
        (1, 'wiki-eg', 'Epigraphs that open sections and chapters of the Foundation series.', ''),
        (1, 'wein-wells', 'Wells as a possible influence (suggestion by Wein; not read).', ''),
        (2, 'wiki-eg', 'Timeline entries: 1942 story, 1951 naming, 1978 tie-in, 1980 Sagan, 1989 Card.', ''),
        (2, 'holby-1942', 'July 1942 first use of the term (cited through Wikipedia).', ''),
        (2, 'adams-1979', '1979 contrast with The Hitchhiker\'s Guide (quoted through Wikipedia).', ''),
        (2, 'sagan-1980', '1980 use in Cosmos (cited through Wikipedia).', ''),
        (3, 'wiki-eg', 'Later uses: Heinlein (1987), Rama II (1989), films and comics.', ''),
        (4, 'wiki-eg', 'Summary of the first-use dispute between Holby and Asimov.', ''),
    ],
)

ARTICLES = [SUBVOCAL, QUADRATIC, ENCYCLOPEDIA]

# ----- Scripted scenarios ------------------------------------------------------------------------------
# A scenario is applied to the article's published revision by the SIMULATED runner and by eval runs.
# Replacements must match exact text. A scenario that does not match is reported, not forced.

LONG_SENTENCE = (
    'The Encyclopedia first appears, embedded within a sequence of administrative, historical and speculative passages '
    'that together describe how a galaxy-spanning state organized its accumulated knowledge into a single compendium '
    'whose purpose is only gradually disclosed, inside Isaac Asimov\'s short story'
)

SCENARIOS = {
    'supported-correction': {
        'candidates': [{
            'label': 'A',
            'rationale': 'Correct the AlterEgo date to 2018 to match the IUI 2018 DOI record, and cite that record.',
            'replacements': [{'find': 'In 2019, Arnav Kapur and colleagues', 'with': 'In 2018, Arnav Kapur and colleagues', 'position': 3}],
            'citations': [{'position': 3, 'source_title': SOURCES['alterego-2018']['title'],
                           'supports': 'AlterEgo, a personalized wearable silent speech interface, at IUI 2018 pages 43-53.', 'quote': ''}],
        }],
    },
    'irrelevant-citation': {
        'candidates': [{
            'label': 'A',
            'rationale': 'Make the early-adopter sentence more specific and attach a citation.',
            'replacements': [{'find': 'is an early adopter', 'with': 'is one of the earliest adopters', 'position': 4}],
            'citations': [{'position': 4, 'source_title': SOURCES['denby-2010']['title'],
                           'supports': 'electromyography of speech articulator muscles', 'quote': ''}],
        }],
    },
    'removed-qualification': {
        'candidates': [{
            'label': 'A',
            'rationale': 'Tighten the uses paragraph by dropping the hedge.',
            'replacements': [{'find': 'Silent speech may aid people', 'with': 'Silent speech aids people', 'position': 4}],
            'citations': [],
        }],
    },
    'unreadable-rewrite': {
        'candidates': [{
            'label': 'A',
            'rationale': 'Rewrite the first-appearance sentence with fuller detail (accurate wording, long sentence).',
            'replacements': [{'find': 'The Encyclopedia first appears in Isaac Asimov\'s short story', 'with': LONG_SENTENCE, 'position': 0}],
            'citations': [],
        }],
    },
    'conflict-a': {
        'candidates': [{
            'label': 'A',
            'rationale': 'Change the story date to May 1941 (deliberately conflicting candidate for evaluation).',
            'replacements': [{'find': 'in May 1942. In the story', 'with': 'in May 1941. In the story', 'position': 0}],
            'citations': [],
        }],
    },
    'conflict-b': {
        'candidates': [{
            'label': 'B',
            'rationale': 'Change the story date to June 1942 (deliberately conflicting candidate for evaluation).',
            'replacements': [{'find': 'in May 1942. In the story', 'with': 'in June 1942. In the story', 'position': 0}],
            'citations': [],
        }],
    },
    'unsupported-date': {
        'candidates': [{
            'label': 'A',
            'rationale': 'Deliberately unsupported test change: adds a 1931 first-publication date with no source.',
            'replacements': [{'find': 'its contents are invented and', 'with': 'its contents are invented, it was first published in 1931, and', 'position': 5}],
            'citations': [],
        }],
    },
    'qf-rule-rewrite': {
        'candidates': [{
            'label': 'A',
            'rationale': 'Restate the rule in plainer words and keep the abstract as the source.',
            'replacements': [{
                'find': 'The amount a project receives is proportional to the square of the sum of the square roots of its contributions.',
                'with': "In the abstract's rule, the amount a project receives is proportional to the square of the sum of the square roots of its contributions, so many small contributors weigh more than one large one.",
                'position': 0,
            }],
            'citations': [],
        }],
    },
    'qf-accepted-change': {
        'candidates': [{
            'label': 'A',
            'rationale': 'Make the deployment sentence name the original quadratic funding scheme explicitly.',
            'replacements': [{'find': 'the original scheme', 'with': 'the original quadratic funding scheme', 'position': 4}],
            'citations': [],
        }],
    },
}

EVAL_CASES = [
    dict(slug='supported-correction-subvocal', category='supported_correction', article='subvocal-interfaces',
         name='Supported correction: AlterEgo year', scenario=SCENARIOS['supported-correction'],
         description='Corrects 2019 to 2018 and cites the DOI record. A supported factual correction should be supported.',
         expected='supported', label_source='simulated'),
    dict(slug='irrelevant-citation-qf', category='irrelevant_citation', article='quadratic-funding',
         name='Irrelevant citation on Gitcoin sentence', scenario=SCENARIOS['irrelevant-citation'],
         description='Attaches an electromyography paper to a sentence about Gitcoin. Citation check should raise a concern.',
         expected='contested', label_source='simulated'),
    dict(slug='removed-qualification-subvocal', category='removed_qualification', article='subvocal-interfaces',
         name='Hedge removed from uses paragraph', scenario=SCENARIOS['removed-qualification'],
         description='Drops "may" from a claim about who benefits. A skeptic should object.',
         expected='objected', label_source='simulated'),
    dict(slug='unreadable-rewrite-encyclopedia', category='unreadable_rewrite', article='encyclopedia-galactica',
         name='Accurate but unreadable rewrite', scenario=SCENARIOS['unreadable-rewrite'],
         description='Accurate wording, one very long sentence. Human judgement is the real test here.',
         expected='unknown', label_source='unknown'),
    dict(slug='conflicting-proposals-encyclopedia', category='conflicting_proposals', article='encyclopedia-galactica',
         name='Two conflicting date changes', scenario={'candidates': [
             SCENARIOS['conflict-a']['candidates'][0], SCENARIOS['conflict-b']['candidates'][0]]},
         description='Two candidates against the same revision change the same date differently. Both get full panels.',
         expected='unknown', label_source='unknown'),
    dict(slug='repeated-rejected-encyclopedia', category='repeated_rejected', article='encyclopedia-galactica',
         name='Repeat of a rejected unsupported date', scenario=SCENARIOS['unsupported-date'],
         description='Same content as the rejected 1931 proposal. Should be flagged as a repeat and objected to.',
         expected='objected', label_source='simulated'),
]
