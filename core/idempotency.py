"""Idempotent write helpers and the HTTP problem contract.

The key is scoped to one agent, not one credential: rotating a token must not turn a retry into
a duplicate. A completed request replays its stored response. An in-flight request returns 409
so a client does not create a second proposal while the first is still running. A key reused
with a different body, method or path returns 422.
"""
import hashlib
import json
from datetime import timedelta

from django.db import IntegrityError
from django.http import HttpResponse
from django.utils import timezone

from .models import IdempotencyRecord

IN_FLIGHT_SECONDS = 600
KEY_TTL = timedelta(hours=24)


class ApiProblem(Exception):
    def __init__(self, status, code, detail, headers=None):
        super().__init__(detail)
        self.status = status
        self.code = code
        self.detail = detail
        self.headers = headers or {}


def problem(status, code, detail, headers=None):
    body = json.dumps({
        'type': 'about:blank',
        'title': code.replace('_', ' '),
        'status': status,
        'code': code,
        'detail': detail,
    })
    response = HttpResponse(body, status=status, content_type='application/problem+json')
    for key, value in (headers or {}).items():
        response[key] = value
    return response


def _payload_hash(request):
    return hashlib.sha256(request.body or b'').hexdigest()


def begin(request, agent):
    """Return (record, None) for new work or (None, replay_response) for a completed duplicate."""
    key = (request.headers.get('Idempotency-Key') or '').strip()
    if not key:
        raise ApiProblem(400, 'idempotency_key_required', 'Send an Idempotency-Key header with this write.')
    if len(key) > 200:
        raise ApiProblem(400, 'invalid_idempotency_key', 'Idempotency-Key must be 200 characters or fewer.')
    now = timezone.now()
    payload_hash = _payload_hash(request)
    path = request.path[:500]
    method = request.method

    record = IdempotencyRecord.objects.filter(agent=agent, key=key).first()
    if record is not None:
        if record.payload_hash != payload_hash or record.method != method or record.path != path:
            raise ApiProblem(
                422, 'payload_mismatch',
                'This Idempotency-Key was already used with a different request body, method or path.',
            )
        if record.state == 'in_flight':
            if record.created_at > now - timedelta(seconds=IN_FLIGHT_SECONDS):
                raise ApiProblem(
                    409, 'duplicate_in_flight',
                    'A request with this Idempotency-Key is still running.', {'Retry-After': '2'},
                )
            # A crashed request must not poison the key forever. The old attempt is abandoned;
            # a retry is allowed, and the caller may see the side effect only if it completed.
            record.delete()
        elif record.expires_at > now:
            return None, _replay(record)
        else:
            record.delete()

    try:
        record = IdempotencyRecord.objects.create(
            agent=agent, key=key, method=method, path=path, payload_hash=payload_hash,
            state='in_flight', expires_at=now + KEY_TTL,
        )
    except IntegrityError:
        # Another process won the race. Treat it as in flight rather than creating a duplicate.
        raise ApiProblem(409, 'duplicate_in_flight', 'A request with this Idempotency-Key is already running.')
    return record, None


def complete(record, response, resource_type='', resource_id=''):
    record.state = 'complete'
    record.status_code = response.status_code
    record.response_body = response.content.decode('utf-8', errors='replace')
    record.resource_type = (resource_type or '')[:40]
    record.resource_id = str(resource_id or '')[:80]
    record.completed_at = timezone.now()
    record.save(update_fields=[
        'state', 'status_code', 'response_body', 'resource_type', 'resource_id', 'completed_at',
    ])


def abandon(record):
    """Remove an in-flight record after a failed attempt so a corrected retry can use the key."""
    if record is not None and record.state == 'in_flight':
        record.delete()


def _replay(record):
    response = HttpResponse(
        record.response_body or '{}', status=record.status_code or 200, content_type='application/json',
    )
    response['Idempotent-Replayed'] = 'true'
    if record.resource_type and record.resource_id:
        response['X-Resource'] = f'{record.resource_type}:{record.resource_id}'
    return response


def check_if_match(request, article):
    """Return the published revision named by If-Match, or raise the 412/428 problem."""
    raw = (request.headers.get('If-Match') or '').strip()
    if not raw:
        raise ApiProblem(
            428, 'precondition_required',
            'Send If-Match with the current published revision id or content hash.',
        )
    current = article.published
    if current is None:
        raise ApiProblem(412, 'stale_base', 'This article has no published revision to write against.')
    tokens = [part.strip().strip('"') for part in raw.split(',')]
    if '*' in tokens:
        return current
    if str(current.pk) in tokens or (current.content_hash and current.content_hash in tokens):
        return current
    raise ApiProblem(
        412, 'stale_base',
        f'The article is now at {current.label}; rebase against revision {current.pk} ({current.content_hash[:12]}).',
        {'ETag': f'"{current.content_hash}"'},
    )
