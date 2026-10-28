import json
import tempfile
from pathlib import Path
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, override_settings

from core import blocks as block_rules
from core import configs, prompts, scenarios
from core.markup import render_block, render_markdown, word_diff_html
from core.runners import RunnerError, Task
from core.runners.opencode import OpenCodeRunner, redact
from core.agents import sandbox_config
from core.runners.simulated import simulate_review


class MarkupSafetyTests(SimpleTestCase):

    def test_scripts_and_event_handlers_are_removed(self):
        html = str(render_markdown('Hello <script>alert(1)</script> <img src=x onerror="alert(2)"> world'))
        self.assertNotIn('<script', html)
        self.assertNotIn('onerror', html)

    def test_javascript_links_are_not_rendered(self):
        html = str(render_markdown('[click](javascript:alert(3))'))
        self.assertNotIn('javascript:', html)

    def test_details_and_summary_are_kept_for_explanations(self):
        html = str(render_markdown('<details>\n<summary>Why</summary>\n\nBecause.\n\n</details>'))
        self.assertIn('<details>', html)
        self.assertIn('<summary>', html)

    def test_table_and_timeline_values_are_escaped(self):
        html = str(render_block('table', {'caption': '<b>c</b>', 'headers': ['<i>h</i>'], 'rows': [['<u>x</u>']]}))
        self.assertNotIn('<b>c</b>', html)
        self.assertIn('&lt;b&gt;', html)
        html = str(render_block('timeline', {'title': 't', 'events': [{'date': '1', 'text': '<script>x</script>'}]}))
        self.assertNotIn('<script>', html)

    def test_image_src_must_be_static_or_https(self):
        with self.assertRaises(ValidationError):
            block_rules.validate_block('image', {'src': 'javascript:alert(1)', 'alt': 'a', 'credit': 'c'})
        with self.assertRaises(ValidationError):
            block_rules.validate_block('image', {'src': 'data:image/svg+xml,<svg/>', 'alt': 'a', 'credit': 'c'})
        ok = block_rules.validate_block('image', {'src': '/static/img/x.svg', 'alt': 'a', 'credit': 'c'})
        self.assertEqual(ok['src'], '/static/img/x.svg')

    def test_table_row_width_is_checked(self):
        with self.assertRaisesRegex(ValidationError, 'exactly 2 cells'):
            block_rules.validate_block('table', {'caption': 'c', 'headers': ['a', 'b'], 'rows': [['only one']]})

    def test_timeline_needs_events(self):
        with self.assertRaises(ValidationError):
            block_rules.validate_block('timeline', {'title': 't', 'events': []})

    def test_diff_escapes_text_and_marks_changes(self):
        html = str(word_diff_html('The <b>old</b> claim.', 'The <b>new</b> claim.'))
        self.assertIn('<del>', html)
        self.assertIn('<ins>', html)
        self.assertNotIn('<b>', html)

    def test_block_ids_must_be_unique_uuids(self):
        import uuid
        one = str(uuid.uuid4())
        with self.assertRaises(ValidationError):
            block_rules.validate_blocks([
                {'block_id': one, 'kind': 'markdown', 'data': {'text': 'a'}},
                {'block_id': one, 'kind': 'markdown', 'data': {'text': 'b'}},
            ])
        with self.assertRaises(ValidationError):
            block_rules.validate_blocks([{'block_id': 'not-a-uuid', 'kind': 'markdown', 'data': {'text': 'a'}}])


class SimulatedReviewTests(SimpleTestCase):

    def side(self, text, cited=False, citation=None):
        bid = 'b1'
        blocks = [{'block_id': bid, 'kind': 'markdown', 'data': {'text': text}}]
        citations = [citation] if citation else []
        return {'title': 't', 'opening': '', 'blocks': blocks, 'citations': citations}

    def payload(self, base_text, cand_text, cand_citation=None, repeat_note=''):
        base = self.side(base_text)
        cand = self.side(cand_text, citation=cand_citation)
        return {'base': base, 'candidate': cand, 'changed_block_ids': ['b1'], 'repeat_note': repeat_note,
                'rationale': 'test'}

    def test_irrelevant_citation_raises_concern(self):
        cit = {'block_id': 'b1', 'source_title': 'x', 'supports': 'electromyography of speech muscles', 'quote': ''}
        result = simulate_review('citation', self.payload('Gitcoin funded many projects.', 'Gitcoin funded many projects.', cit))
        self.assertEqual(result['verdict'], 'concern')

    def test_removed_hedge_is_objected(self):
        result = simulate_review('skeptic', self.payload('It may fail.', 'It fails.'))
        self.assertEqual(result['verdict'], 'object')

    def test_long_sentence_is_objected(self):
        long = ' '.join(['word'] * 45) + '.'
        result = simulate_review('readability', self.payload('Short.', long))
        self.assertEqual(result['verdict'], 'object')

    def test_repeat_note_is_objected(self):
        result = simulate_review('skeptic', self.payload('Same.', 'Same.', repeat_note='Repeats a rejected proposal.'))
        self.assertEqual(result['verdict'], 'object')

    def test_simulated_comments_are_labelled(self):
        result = simulate_review('fact_check', self.payload('x', 'x'))
        self.assertTrue(result['comment'].startswith('[SIMULATED]'))

    def test_scenario_must_apply(self):
        with self.assertRaises(scenarios.ScenarioError):
            scenarios.apply_scenario([{'block_id': 'b', 'kind': 'markdown', 'data': {'text': 'abc'}}],
                                     {'replacements': [{'find': 'zzz', 'with': 'y'}]})


class OpenCodeRunnerTests(SimpleTestCase):

    def runner(self, tmp):
        with override_settings(GALACTICA={'RUNTIME_DIR': tmp, 'OPENCODE_BIN': 'opencode', 'HEARTBEAT_STALE_SECONDS': 90}):
            return OpenCodeRunner()

    def write_events(self, tmp, lines):
        path = Path(tmp) / 'events.jsonl'
        path.write_text('\n'.join(json.dumps(l) for l in lines))
        return path

    def test_sandbox_config_is_per_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = self.runner(tmp)
            writer = r._sandbox('writer', [])
            written = json.loads((writer / 'opencode.json').read_text())
            self.assertEqual(written, sandbox_config('writer', []))
            self.assertEqual(written['permissions'], [{'action': '*', 'resource': '*', 'effect': 'deny'}])
            researcher = r._sandbox('researcher', ['en.wikipedia.org'])
            rules = json.loads((researcher / 'opencode.json').read_text())['permissions']
            self.assertIn({'action': 'websearch', 'resource': '*', 'effect': 'allow'}, rules)
            self.assertNotIn('shell', {r['action'] for r in rules if r['effect'] == 'allow'})

    def test_parse_reads_text_and_measured_usage(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = self.runner(tmp)
            out = self.write_events(tmp, [
                {'type': 'step_start', 'part': {}},
                {'type': 'text', 'part': {'type': 'text', 'text': '```json\n{"verdict": "support", "comment": "fine", "evidence_notes": ""}\n```'}},
                {'type': 'step_finish', 'part': {'tokens': {'input': 100, 'output': 20, 'reasoning': 5, 'cache': {'read': 7}}, 'cost': 0}},
            ])
            usage = {}

            class Ctx:
                def record_usage(self, u):
                    usage.update(u)
            task = Task(kind='review', model='opencode/x', role='fact_check')
            err = tmp + '/err.txt'
            Path(err).write_text('')
            result = r._parse(task, out, Path(err), 0, Ctx(), 'opencode/x')
            self.assertEqual(result['verdict'], 'support')
            self.assertEqual(usage['input_tokens'], 100)
            self.assertEqual(usage['reported_cost'], 0)
            self.assertIn('measured', usage['source'])

    def test_multiple_step_finish_events_are_summed(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = self.runner(tmp)
            out = self.write_events(tmp, [
                {'type': 'text', 'part': {'text': '```json\n{"verdict":"support","comment":"x","evidence_notes":""}\n```'}},
                {'type': 'step_finish', 'part': {'tokens': {'input': 100, 'output': 20, 'reasoning': 5, 'cache': {'read': 7}}, 'cost': 0}},
                {'type': 'step_finish', 'part': {'tokens': {'input': 50, 'output': 10, 'reasoning': 2, 'cache': {'read': 3}}, 'cost': 0}},
            ])
            usage = {}

            class Ctx:
                def record_usage(self, u):
                    usage.update(u)
            err = Path(tmp) / 'err.txt'; err.write_text('')
            r._parse(Task(kind='review', model='m'), out, err, 0, Ctx(), 'm')
            self.assertEqual(usage['calls'], 2)
            self.assertEqual(usage['input_tokens'], 150)
            self.assertEqual(usage['output_tokens'], 30)
            self.assertEqual(usage['cache_read_tokens'], 10)

    def test_session_message_usage_is_fallback_for_text_only_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = self.runner(tmp)
            out = self.write_events(tmp, [
                {'type': 'step_start', 'sessionID': 'ses_test', 'part': {}},
                {'type': 'text', 'sessionID': 'ses_test', 'part': {'text': '```json\n{"verdict":"support","comment":"x","evidence_notes":""}\n```'}},
            ])
            usage = {}

            class Ctx:
                def record_usage(self, u):
                    usage.update(u)
            r._session_usage = lambda session_id: {
                'calls': 1, 'input_tokens': 2591, 'output_tokens': 666, 'reasoning_tokens': 1325,
                'cache_read_tokens': 0, 'reported_cost': 0.0, 'source': 'OpenCode session message API',
            }
            err = Path(tmp) / 'err.txt'; err.write_text('')
            r._parse(Task(kind='review', model='m'), out, err, 0, Ctx(), 'm')
            self.assertEqual(usage['input_tokens'], 2591)
            self.assertEqual(usage['source'], 'OpenCode session message API')

    def test_error_event_is_reported_and_redacted(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = self.runner(tmp)
            out = self.write_events(tmp, [{'type': 'error', 'error': {'type': 'provider.free-limit',
                                                                     'message': 'Free limit for key sk-abcdef123456789'}}])
            err = Path(tmp) / 'err.txt'
            err.write_text('')

            class Ctx:
                def record_usage(self, u):
                    pass
            with self.assertRaises(RunnerError) as ctx:
                r._parse(Task(kind='review', model='m'), out, err, 1, Ctx(), 'm')
            self.assertNotIn('sk-abcdef', str(ctx.exception))
            self.assertIn('[redacted]', str(ctx.exception))

    def test_invalid_reply_is_rejected(self):
        with self.assertRaises(RunnerError):
            prompts.validate_result('review', {'verdict': 'maybe'})
        with self.assertRaises(RunnerError):
            prompts.extract_json('no json here')

    def test_review_prompt_marks_article_text_as_untrusted(self):
        task = Task(kind='review', model='m', role='skeptic', label='Skeptic')
        task.payload = {'instructions': 'Judge hedges.', 'preamble': 'Be independent.', 'rationale': 'why',
                        'base': {'blocks': []}, 'candidate': {'blocks': []}, 'sources': []}
        prompt = prompts.build_prompt(task, 'Judge hedges.', 'Be independent.')
        self.assertIn('<untrusted-candidate-revision>', prompt)
        self.assertIn('not instructions', prompt)

    def test_redaction_patterns(self):
        self.assertEqual(redact('key sk-ABCDEFGHIJKL and Bearer tok123'), 'key [redacted] and [redacted]')

    def test_discovery_failure_is_reported_not_raised(self):
        configs._MODEL_CACHE.update(at=0, models=None, error='')
        with override_settings(GALACTICA={'RUNTIME_DIR': '/tmp', 'OPENCODE_BIN': '/nonexistent/opencode-bin',
                                          'HEARTBEAT_STALE_SECONDS': 90}):
            models, error = configs.discover_models(force=True)
        self.assertEqual(models, [])
        self.assertTrue(error)
        configs._MODEL_CACHE.update(at=0, models=None, error='')
