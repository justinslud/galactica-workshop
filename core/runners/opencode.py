"""OpenCode CLI runner.

Each model call is a fresh, standalone OpenCode session (`opencode run --standalone`). Calls run inside a sandbox
directory whose project config denies every tool, so the model can only reply with text. Prompts are attached as a
file, not inlined on the command line. Usage is read from OpenCode's own step events; cost is recorded only when
OpenCode reports it.

Workers call this in a subprocess. Cancellation and timeouts kill the whole process group.
"""
import json
import os
import re
import shutil
import signal
import subprocess
import time
from pathlib import Path

from django.conf import settings

from ..agents import sandbox_config
from ..prompts import build_prompt, extract_json, validate_result
from . import ModelRunner, RunnerError

SANDBOX_CONFIG = {
    '$schema': 'https://opencode.ai/config.json',
    'permissions': [{'action': '*', 'resource': '*', 'effect': 'deny'}],
}
SECRET_PATTERNS = [
    re.compile(r'sk-[A-Za-z0-9_\-]{8,}'),
    re.compile(r'Bearer\s+[A-Za-z0-9._\-]+', re.IGNORECASE),
    re.compile(r'(api[_-]?key|token|secret)\s*[=:]\s*\S+', re.IGNORECASE),
]
POLL_SECONDS = 1.0
INHERITED_SESSION_VARS = ('OPENCODE', 'OPENCODE_SESSION_ID', 'OPENCODE_TERMINAL', 'AI_AGENT')


def clean_environment(cwd):
    """Never inherit an outer OpenCode session or client context into a fresh agent call.

    PWD is set explicitly: OpenCode can use it for project/config discovery, and a stale inherited value points at the
    parent project instead of the sandbox.
    """
    env = {k: v for k, v in os.environ.items()
           if k not in INHERITED_SESSION_VARS and not k.startswith('OPENCODE_CONFIG')}
    env['PWD'] = os.fspath(cwd)
    return env


def redact(text):
    for pattern in SECRET_PATTERNS:
        text = pattern.sub('[redacted]', text)
    return text


class OpenCodeRunner(ModelRunner):
    name = 'opencode'
    label = 'OpenCode'

    def __init__(self):
        self.runtime = Path(settings.GALACTICA['RUNTIME_DIR'])
        self.sandbox = self.runtime / 'opencode-sandbox'
        self.binary = shutil.which(settings.GALACTICA['OPENCODE_BIN']) or settings.GALACTICA['OPENCODE_BIN']

    def available(self):
        if shutil.which(settings.GALACTICA['OPENCODE_BIN']) is None and not Path(self.binary).exists():
            return False, 'The OpenCode CLI is not installed or not on PATH.'
        return True, ''

    def _sandbox(self, profile, allowed_domains, job_id='adhoc'):
        """One directory and config per job and profile, so concurrent workers cannot swap permission sets."""
        if profile not in ('researcher', 'writer', 'reviewer'):
            raise RunnerError(f'Unknown agent profile: {profile}')
        path = self.sandbox / str(job_id) / profile
        path.mkdir(parents=True, exist_ok=True)
        config = path / 'opencode.json'
        wanted = json.dumps(sandbox_config(profile, allowed_domains), indent=2)
        if not config.exists() or config.read_text() != wanted:
            config.write_text(wanted)
        return path

    def call(self, ctx, task):
        ok, message = self.available()
        if not ok:
            raise RunnerError(message)
        profile = task.profile or 'writer'
        sandbox = self._sandbox(profile, task.payload.get('allowed_domains', ()), ctx.job.pk)
        ctx.spend_call()
        ctx.check()
        instructions = task.payload.get('instructions', '')
        preamble = task.payload.get('preamble', '')
        prompt = build_prompt(task, instructions, preamble)
        run_dir = self.runtime / 'runs' / str(ctx.job.pk) / profile
        run_dir.mkdir(parents=True, exist_ok=True)
        stamp = f'{ctx.job.model_calls:03d}-{task.kind}-{task.role or profile}'
        prompt_path = run_dir / f'{stamp}.prompt.md'
        prompt_path.write_text(prompt, encoding='utf-8')
        model = task.model + (f"#{task.payload['variant']}" if task.payload.get('variant') else '')
        timeout = min(task.payload.get('call_timeout', 180), ctx.seconds_left())
        if timeout <= 0:
            raise RunnerError('Job time limit reached before this model call.')
        cmd = [
            self.binary, 'run', '--standalone', '--format', 'json', '--agent', profile,
            '--model', model, '--title', f'galactica {ctx.job.pk} {profile} {task.kind} {task.role}'.strip(),
            '--file', str(prompt_path),
            'Follow the attached instructions exactly. Reply with only the requested JSON object.',
        ]
        out_path = run_dir / f'{stamp}.events.jsonl'
        err_path = run_dir / f'{stamp}.stderr.txt'
        with open(out_path, 'w') as out, open(err_path, 'w') as err:
            proc = subprocess.Popen(cmd, cwd=sandbox, stdout=out, stderr=err, start_new_session=True,
                                    env=clean_environment(sandbox))
            started = time.monotonic()
            try:
                while proc.poll() is None:
                    if time.monotonic() - started > timeout:
                        _kill(proc)
                        raise RunnerError(f'Model call exceeded {timeout}s and was stopped.')
                    try:
                        ctx.check()
                    except Exception:
                        _kill(proc)
                        raise
                    ctx.heartbeat()
                    time.sleep(POLL_SECONDS)
            except BaseException:
                _kill(proc)
                raise
        return self._parse(task, out_path, err_path, proc.returncode, ctx, model)

    def _session_usage(self, session_id):
        """Read measured token usage from OpenCode's session message API.

        Text-only runs in this build emit no step_finish event, so the event stream alone is incomplete. This is a
        read-only local API call; only numeric usage fields are kept, never message content.
        """
        if not session_id:
            return None
        try:
            proc = subprocess.run(
                [self.binary, 'api', 'get', f'/api/session/{session_id}/message'],
                cwd=self.runtime, env=clean_environment(self.runtime), capture_output=True, text=True, timeout=15,
            )
            payload = json.loads(proc.stdout or '{}')
        except (subprocess.TimeoutExpired, OSError, json.JSONDecodeError):
            return None
        data = payload.get('data') if isinstance(payload, dict) else payload
        if not isinstance(data, list):
            return None
        totals = {'calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'reasoning_tokens': 0,
                  'cache_read_tokens': 0, 'reported_cost': 0.0}
        for message in data:
            tokens = message.get('tokens') if isinstance(message, dict) else None
            if not isinstance(tokens, dict):
                continue
            totals['calls'] += 1
            totals['input_tokens'] += int(tokens.get('input', 0) or 0)
            totals['output_tokens'] += int(tokens.get('output', 0) or 0)
            totals['reasoning_tokens'] += int(tokens.get('reasoning', 0) or 0)
            totals['cache_read_tokens'] += int((tokens.get('cache') or {}).get('read', 0) or 0)
            cost = message.get('cost')
            if isinstance(cost, (int, float)):
                totals['reported_cost'] += float(cost)
        if not totals['calls']:
            return None
        totals['source'] = 'OpenCode session message API (measured by OpenCode)'
        return totals

    def _parse(self, task, out_path, err_path, returncode, ctx, model):
        text_parts, error = [], None
        session_id = ''
        step_usage = {'calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'reasoning_tokens': 0,
                      'cache_read_tokens': 0, 'reported_cost': 0.0}
        for line in out_path.read_text(encoding='utf-8', errors='replace').splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = event.get('type')
            part = event.get('part') or {}
            session_id = event.get('sessionID') or session_id
            if kind == 'text' and part.get('text'):
                text_parts.append(part['text'])
            elif kind == 'step_finish':
                tokens = part.get('tokens') or {}
                step_usage['calls'] += 1
                step_usage['input_tokens'] += int(tokens.get('input', 0) or 0)
                step_usage['output_tokens'] += int(tokens.get('output', 0) or 0)
                step_usage['reasoning_tokens'] += int(tokens.get('reasoning', 0) or 0)
                step_usage['cache_read_tokens'] += int((tokens.get('cache') or {}).get('read', 0) or 0)
                cost = part.get('cost')
                if isinstance(cost, (int, float)):
                    step_usage['reported_cost'] += float(cost)
            elif kind == 'error':
                info = event.get('error') or {}
                error = info.get('message') or info.get('type') or 'OpenCode reported an error.'
        usage = None
        if step_usage['calls']:
            step_usage['model'] = model
            step_usage['source'] = 'OpenCode step events (measured by OpenCode)'
            usage = step_usage
        session_usage = self._session_usage(session_id)
        if session_usage and (not usage or session_usage['calls'] >= usage['calls']):
            session_usage['model'] = model
            usage = session_usage
        if usage:
            ctx.record_usage(usage)
        if error:
            raise RunnerError(redact(f'OpenCode error for {model}: {error}')[:400])
        if returncode != 0 and not text_parts:
            tail = redact(err_path.read_text(encoding='utf-8', errors='replace')[-400:])
            raise RunnerError(f'OpenCode exited with code {returncode}. {tail}'.strip())
        obj = validate_result(task.kind, extract_json(''.join(text_parts)))
        return obj


def _kill(proc):
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        return
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
