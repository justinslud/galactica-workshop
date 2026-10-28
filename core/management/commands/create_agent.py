from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from core.agent_auth import VALID_SCOPES, create_credential
from core.models import Agent


class Command(BaseCommand):
    help = 'Create or update an agent identity. With --issue-token, print a new scoped token once.'

    def add_arguments(self, parser):
        parser.add_argument('--name', required=True)
        parser.add_argument('--operator', default='admin', help='Human operator username.')
        parser.add_argument('--scopes', default='read,research,propose,review',
                            help='Comma-separated subset of: ' + ', '.join(sorted(VALID_SCOPES)))
        parser.add_argument('--issue-token', action='store_true', help='Issue a new credential and print it once.')
        parser.add_argument('--description', default='')

    def handle(self, *args, **options):
        try:
            operator = User.objects.get(username=options['operator'])
        except User.DoesNotExist:
            raise CommandError('Operator account not found.')
        scopes = [s.strip() for s in options['scopes'].split(',') if s.strip()]
        unknown = set(scopes) - VALID_SCOPES
        if unknown:
            raise CommandError(f'Unknown scopes: {sorted(unknown)}')
        agent, created = Agent.objects.get_or_create(
            name=options['name'],
            defaults={'operator': operator, 'scopes': scopes, 'description': options['description']},
        )
        if not created:
            agent.operator = operator
            agent.scopes = scopes
            agent.is_active = True
            if options['description']:
                agent.description = options['description']
            agent.save()
        self.stdout.write(f'Agent {"created" if created else "updated"}: {agent.name} ({", ".join(scopes)})')
        if options['issue_token']:
            token, credential = create_credential(agent, scopes)
            self.stdout.write('Token shown once. Store it in the agent environment, never in this repo:')
            self.stdout.write(token)
            self.stdout.write(f'Credential prefix: {credential.prefix}')
