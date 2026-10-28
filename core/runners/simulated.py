"""SIMULATED runner. Deterministic and offline. Every output is labelled SIMULATED.

It is not a model and makes no judgment about real evidence. Its rules are simple, inspectable heuristics so the
application workflow (job -> proposal -> independent reviews -> decision -> publication) can be exercised and tested
without spending anything. Reviews from this runner must never be presented as real review.
"""
import json

from ..scenarios import ScenarioError, apply_scenario, numbers, qualifier_count, sentence_lengths, words
from . import ModelRunner, RunnerError

LABEL = 'SIMULATED'


class SimulatedRunner(ModelRunner):
    name = 'simulated'
    label = LABEL

    def available(self):
        return True, 'SIMULATED runner is local and offline.'

    def call(self, ctx, task):
        ctx.spend_call()
        ctx.check()
        if task.kind == 'draft':
            return self._draft(task.payload)
        if task.kind == 'edit':
            return self._edit(task.payload)
        if task.kind == 'review':
            return simulate_review(task.role, task.payload)
        raise ValueError(task.kind)

    def _draft(self, payload):
        topic = payload['topic']
        return {
            'title': f'{topic} (SIMULATED draft)'[:200],
            'opening': 'SIMULATED placeholder: no research was performed. Replace with a sourced opening before proposing.',
            'blocks': [
                {'kind': 'markdown', 'data': {'text': f'## Overview\n\nSIMULATED placeholder for {topic}. [needs source]'}},
                {'kind': 'markdown', 'data': {'text': '## Open questions\n\nSIMULATED: list the questions a reader would ask. [needs source]'}},
            ],
            'citations': [],
            'rationale': 'SIMULATED draft skeleton. It contains placeholders, not research.',
        }

    def _edit(self, payload):
        scenario = payload['scenario']
        try:
            new_items = apply_scenario(payload['base']['blocks'], scenario)
        except ScenarioError as exc:
            raise RunnerError(str(exc))
        return {
            'rationale': scenario.get('rationale', 'SIMULATED edit.'),
            'blocks': [{'block_id': i['block_id'], 'kind': i['kind'], 'data': i['data']} for i in new_items],
            'citations': scenario.get('citations', []),
        }


def _text_of(block):
    if block.get('kind') == 'markdown':
        return block.get('data', {}).get('text', '')
    return json.dumps(block.get('data', {}), ensure_ascii=False)


def _block_map(side):
    return {b['block_id']: b for b in side['blocks']}


def simulate_review(role, payload):
    base, cand = payload['base'], payload['candidate']
    changed = set(payload.get('changed_block_ids', []))
    cand_blocks = _block_map(cand)
    base_blocks = _block_map(base)
    cited = {}
    for c in cand.get('citations', []):
        cited.setdefault(c['block_id'], []).append(c)

    if role == 'fact_check':
        added = set()
        for bid in changed:
            if bid in cand_blocks and cand_blocks[bid]['kind'] == 'markdown':
                old = base_blocks.get(bid, {}).get('data', {}).get('text', '')
                added |= numbers(cand_blocks[bid]['data']['text']) - numbers(old)
        uncited = [bid for bid in changed if bid in cand_blocks and numbers(_text_of(cand_blocks[bid])) and bid not in cited]
        if added and uncited:
            return _verdict('concern', f'New figures {sorted(added)} appear in a changed block with no citation.')
        return _verdict('support', 'Changed figures are either unchanged or carry a citation in this revision.')

    if role == 'citation':
        if not any(bid in cited for bid in changed):
            return _verdict('abstain', 'No citations attached to changed blocks.')
        for bid, entries in cited.items():
            if bid not in cand_blocks:
                continue
            block_words = words(_text_of(cand_blocks[bid]))
            for entry in entries:
                if not (words(entry['supports']) & block_words):
                    return _verdict('concern', f'The note "{entry["supports"][:80]}" shares no key terms with the block it is attached to.')
        return _verdict('support', 'Each citation note overlaps the text it is attached to.')

    if role == 'readability':
        longest = 0
        for bid in changed:
            if bid in cand_blocks and cand_blocks[bid]['kind'] == 'markdown':
                lengths = sentence_lengths(cand_blocks[bid]['data']['text'])
                if lengths:
                    longest = max(longest, max(lengths))
        if longest > 40:
            return _verdict('object', f'A changed sentence runs {longest} words; hard to follow for a general reader.')
        if longest > 28:
            return _verdict('concern', f'A changed sentence runs {longest} words; consider splitting it.')
        return _verdict('support', 'Changed sentences are a readable length.')

    if role == 'skeptic':
        if payload.get('repeat_note'):
            return _verdict('object', payload['repeat_note'])
        before = sum(qualifier_count(b['data'].get('text', '')) for b in base['blocks'] if b['kind'] == 'markdown')
        after = sum(qualifier_count(b['data'].get('text', '')) for b in cand['blocks'] if b['kind'] == 'markdown')
        if after < before:
            return _verdict('object', f'Hedges and qualifications dropped from {before} to {after}.')
        return _verdict('support', 'Qualifications are kept.')

    raise ValueError(f'Unknown review role: {role}')


def _verdict(verdict, comment):
    return {'verdict': verdict, 'comment': f'[SIMULATED] {comment}', 'evidence_notes': 'SIMULATED heuristic; not a human or model judgment.'}
