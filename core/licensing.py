"""Content licenses and citation strings.

This is a small, explicit table, not legal advice. The default follows the product specification
(CC BY-SA 4.0 for articles); changing a license is a steward decision and is recorded on each
publication event so a published copy cannot be silently relicensed.
"""
from datetime import date

LICENSES = {
    'CC-BY-SA-4.0': {
        'name': 'Creative Commons Attribution-ShareAlike 4.0 International',
        'short': 'CC BY-SA 4.0',
        'url': 'https://creativecommons.org/licenses/by-sa/4.0/',
        'redistributable': True,
    },
    'CC-BY-4.0': {
        'name': 'Creative Commons Attribution 4.0 International',
        'short': 'CC BY 4.0',
        'url': 'https://creativecommons.org/licenses/by/4.0/',
        'redistributable': True,
    },
    'CC0-1.0': {
        'name': 'Creative Commons Zero 1.0 Universal',
        'short': 'CC0 1.0',
        'url': 'https://creativecommons.org/publicdomain/zero/1.0/',
        'redistributable': True,
    },
    'all-rights-reserved': {
        'name': 'All rights reserved',
        'short': 'All rights reserved',
        'url': '',
        'redistributable': False,
    },
    'other': {
        'name': 'Other license (see the article credit line)',
        'short': 'Other',
        'url': '',
        'redistributable': False,
    },
}

DEFAULT_LICENSE = 'CC-BY-SA-4.0'
LICENSE_CHOICES = [(key, value['short']) for key, value in LICENSES.items()]


def license_info(code):
    """Return a complete record even for a legacy or unknown code."""
    if code in LICENSES:
        return dict(LICENSES[code], code=code)
    return dict(LICENSES['other'], code=code or 'other', name=f'Unrecognised license: {code}' if code else LICENSES['other']['name'])


def citation(article, revision, permalink, accessed=None, author=None):
    """A readable citation for one immutable revision.

    The revision ID and content hash are both included: the ID is the identity, the hash is the
    content address. A citation that only names the slug can silently point at a newer revision.
    """
    accessed = accessed or date.today()
    info = license_info(article.license)
    who = author or (revision.created_by.username if revision.created_by_id else 'Galactica contributors')
    published = revision.published_at or revision.created_at
    when = published.date().isoformat() if published else 'n.d.'
    return {
        'author': who,
        'title': revision.title,
        'site': 'Galactica Workshop',
        'published': when,
        'revision': revision.label,
        'revision_id': str(revision.pk),
        'content_hash': revision.content_hash,
        'license': info['short'],
        'license_name': info['name'],
        'license_url': info['url'],
        'url': permalink,
        'accessed': accessed.isoformat(),
        'text': (
            f'{who}. "{revision.title}." Galactica Workshop, {when}. '
            f'Revision {revision.label} ({revision.content_hash[:12] if revision.content_hash else "no hash"}). '
            f'{info["short"]}. {permalink} (accessed {accessed.isoformat()}).'
        ),
    }
