"""Pure helpers for candidate edits. No database access, so the simulated runner and tests can use them directly."""
import copy
import re

QUALIFIERS = [
    'may', 'might', 'could', 'uncertain', 'debated', 'according to', 'preliminary',
    'likely', 'estimated', 'suggests', 'unclear', 'approximately', 'roughly', 'reportedly',
]


class ScenarioError(Exception):
    """A scripted edit does not apply to the revision it targets."""


def apply_scenario(items, scenario):
    """items: [{'block_id', 'kind', 'data'}]. Returns new items with the scenario's text replacements applied."""
    new = copy.deepcopy(items)
    for rep in scenario.get('replacements', []):
        find = rep['find']
        position = rep.get('position')
        applied = False
        for index, item in enumerate(new):
            if item['kind'] != 'markdown' or (position is not None and index != position):
                continue
            text = item['data']['text']
            if find in text:
                item['data']['text'] = text.replace(find, rep['with'], 1)
                applied = True
                break
        if not applied:
            raise ScenarioError(f'Scripted edit does not apply to this revision: text not found ({find[:60]!r}).')
    return new


def qualifier_count(text):
    lowered = (text or '').lower()
    return sum(len(re.findall(rf'\b{re.escape(q)}\b', lowered)) for q in QUALIFIERS)


def numbers(text):
    return set(re.findall(r'\b\d{3,}\b', text or ''))


def sentence_lengths(text):
    sentences = [s for s in re.split(r'(?<=[.!?])\s+', text or '') if s.strip()]
    return [len(s.split()) for s in sentences]


def words(text):
    return {w for w in re.findall(r'[a-z]{4,}', (text or '').lower())}
