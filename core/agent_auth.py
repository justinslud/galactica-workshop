"""Scoped credentials for non-human actors.

Tokens are shown once. Only a salted hash and a lookup prefix are stored. There is no admin/session fallback on the API,
and no publication scope is enforced anywhere in this pass.
"""
import secrets

from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone

from .models import Agent, AgentCredential

TOKEN_PREFIX = 'gal_agent_'
VALID_SCOPES = {value for value, _label in Agent.SCOPES}


class AgentAuthError(Exception):
    pass


def create_credential(agent, scopes=None, label=''):
    scopes = list(scopes or agent.scopes or [])
    unknown = set(scopes) - VALID_SCOPES
    if unknown:
        raise ValueError(f'Unknown scopes: {sorted(unknown)}')
    not_granted = set(scopes) - set(agent.scopes or [])
    if not_granted:
        raise ValueError(f'Agent does not hold these scopes: {sorted(not_granted)}')
    prefix = secrets.token_hex(6)
    secret = secrets.token_urlsafe(32)
    token = f'{TOKEN_PREFIX}{prefix}_{secret}'
    credential = AgentCredential.objects.create(
        agent=agent, prefix=prefix, token_hash=make_password(token), scopes=scopes,
    )
    return token, credential


def authenticate(request, scope):
    header = request.META.get('HTTP_AUTHORIZATION', '')
    if not header.startswith('Bearer '):
        raise AgentAuthError('Missing bearer token.')
    token = header[7:].strip()
    if not token.startswith(TOKEN_PREFIX):
        raise AgentAuthError('Invalid token.')
    body = token[len(TOKEN_PREFIX):]
    prefix = body.split('_', 1)[0]
    credential = AgentCredential.objects.select_related('agent').filter(
        prefix=prefix, revoked_at__isnull=True).first()
    if credential is None or not check_password(token, credential.token_hash):
        raise AgentAuthError('Invalid token.')
    agent = credential.agent
    if not agent.is_active:
        raise AgentAuthError('Agent is inactive.')
    if scope not in (credential.scopes or []) or not agent.has_scope(scope):
        raise AgentAuthError('Token does not have the required scope.')
    AgentCredential.objects.filter(pk=credential.pk).update(last_used_at=timezone.now())
    return agent, credential
