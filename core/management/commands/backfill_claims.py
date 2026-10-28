"""Create claim-level records for existing agent revisions without changing the article text.

This is a deterministic migration aid, not a general claim extractor. It handles markdown bullets and plain sentences,
attaches existing block citations by support-note overlap, and marks disagreement composites as conflicting. Idempotent.
"""
import re

from django.core.management.base import BaseCommand

from core.models import Article, Citation, Claim, Revision

WORD = re.compile(r'[a-z]{4,}')
DISAGREEMENT = re.compile(r'\bwhile\b|\bwhereas\b|disagree|conflict', re.IGNORECASE)


def _words(text):
    return set(WORD.findall((text or '').lower()))


def _units(text):
    """Return (text, start, end) for bullets, else sentences in non-heading paragraphs."""
    units = []
    offset = 0
    bullet_found = False
    for line in text.splitlines(keepends=True):
        match = re.match(r'^\s*[-*]\s+(.+?)\s*$', line)
        if match:
            bullet_found = True
            value = match.group(1)
            start = offset + line.find(value)
            units.append((value, start, start + len(value)))
        offset += len(line)
    if bullet_found:
        return units
    # Sentence-level fallback, skipping headings and HTML wrappers.
    for paragraph in re.split(r'\n\s*\n', text):
        stripped = paragraph.strip()
        if not stripped or stripped.startswith('#') or stripped.startswith('<'):
            continue
        base = text.find(paragraph)
        for sentence in re.split(r'(?<=[.!?])\s+', paragraph):
            value = sentence.strip()
            if not value:
                continue
            start = text.find(value, base)
            if start == -1:
                continue
            units.append((value, start, start + len(value)))
    return units


def _recompute_statuses(created):
    for claim in created:
        citations = list(claim.citations.all())
        if not citations:
            claim.support_status = 'absent'
            claim.support_note = 'No preserved citation is attached.'
        elif DISAGREEMENT.search(claim.text):
            claim.support_status = 'conflicting'
            claim.support_note = 'Claim states a disagreement; attached citations may cover different parts.'
        elif any(not c.quote for c in citations):
            claim.support_status = 'partial'
            claim.support_note = 'At least one citation has no stored quotation.'
        else:
            claim.support_status = 'direct'
            claim.support_note = 'Every attached citation states direct support.'
        claim.save(update_fields=['support_status', 'support_note'])


def backfill_revision(revision, refresh=False):
    if revision.claims.exists():
        if refresh:
            _recompute_statuses(list(revision.claims.all()))
        return 0
    position = 0
    created = []
    for block in revision.blocks.order_by('position'):
        if block.kind != 'markdown':
            continue
        for value, start, end in _units(block.data.get('text', '')):
            position += 1
            claim = Claim.objects.create(
                revision=revision, block_id=block.block_id, position=position, text=value,
                start=start, end=end, support_status='absent', support_note='No preserved citation is attached.',
            )
            created.append(claim)
    by_block = {}
    for claim in created:
        by_block.setdefault(str(claim.block_id), []).append(claim)
    for citation in revision.citations.filter(claim__isnull=True):
        claims = by_block.get(str(citation.block_id), [])
        if not claims:
            continue
        note = _words(citation.supports) | _words(citation.quote)
        scored = sorted(((len(note & _words(c.text)), c) for c in claims), key=lambda pair: pair[0], reverse=True)
        if scored and scored[0][0] > 0:
            citation.claim = scored[0][1]
            citation.save(update_fields=['claim'])
    _recompute_statuses(created)
    return len(created)


class Command(BaseCommand):
    help = 'Create claim-level records for existing agent article revisions. Idempotent; never edits article text.'

    def add_arguments(self, parser):
        parser.add_argument('--article', default='alterego-silent-speech-project')
        parser.add_argument('--all-agent', action='store_true', help='Backfill every article with provenance=agent.')
        parser.add_argument('--refresh-status', action='store_true', help='Recompute statuses for existing claims.')

    def handle(self, *args, **options):
        if options['all_agent']:
            articles = Article.objects.filter(provenance='agent')
        else:
            articles = Article.objects.filter(slug=options['article'])
        total = 0
        for article in articles:
            for revision in article.revisions.all():
                n = backfill_revision(revision, refresh=options['refresh_status'])
                if n:
                    total += n
                    assigned = Citation.objects.filter(revision=revision, claim__isnull=False).count()
                    self.stdout.write(f'{article.slug} r{revision.number}: {n} claims, {assigned} citations attached')
        self.stdout.write(f'created {total} claim(s)')
