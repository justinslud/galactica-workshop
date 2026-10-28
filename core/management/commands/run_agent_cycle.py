from django.core.management.base import BaseCommand, CommandError

from core import configs, jobs
from core.models import Agent, ConfigVersion


class Command(BaseCommand):
    help = 'Queue one bounded agent editorial cycle (research, cite, review, leave pending).'

    def add_arguments(self, parser):
        parser.add_argument('--topic', required=True)
        parser.add_argument('--question', required=True)
        parser.add_argument('--agent', default='galactica-agent')
        parser.add_argument('--wait', action='store_true', help='Run the job in this process instead of leaving it queued.')
        parser.add_argument('--runner-family', default='opencode-free')
        parser.add_argument('--instructions-family', default='drafting-explainer')
        parser.add_argument('--reviewers-family', default='panel-four')
        parser.add_argument('--seed-url', action='append', default=[],
                            help='Optional URL to preserve in addition to researcher suggestions. Still allowlisted.')
        parser.add_argument('--evaluation-claim', default='',
                            help='Optional planted claim for a separate never-publishable evaluation candidate.')

    def handle(self, *args, **options):
        agent = Agent.objects.filter(name=options['agent'], is_active=True).first()
        if agent is None:
            raise CommandError('Agent not found. Create one with manage.py create_agent.')
        version = (configs.ConfigVersion.objects.filter(
            kind='runner', family=options['runner_family']).order_by('-version').first()
            or configs.ConfigVersion.objects.filter(kind='runner', data__runner='opencode').order_by('-version').first())
        if version is None or version.data.get('runner') != 'opencode':
            raise CommandError('No OpenCode runner version is configured. No paid fallback is attempted.')
        instructions = ConfigVersion.objects.filter(
            kind='instructions', family=options['instructions_family']).order_by('-version').first()
        reviewers = ConfigVersion.objects.filter(
            kind='reviewers', family=options['reviewers_family']).order_by('-version').first()
        if instructions is None or reviewers is None:
            raise CommandError('Instructions or reviewer family not found.')
        job = jobs.enqueue('agent_cycle', user=agent.operator, runner_name='opencode',
                           input={'topic': options['topic'], 'question': options['question'],
                                  'agent_id': str(agent.pk), 'seed_urls': options['seed_url'],
                                  'evaluation_claim': options['evaluation_claim']},
                           label=f'Agent cycle: {options["topic"]}',
                           selection={'runner': version, 'instructions': instructions, 'reviewers': reviewers})
        self.stdout.write(f'queued {job.pk}')
        if options['wait']:
            job = jobs.run_now(job)
            self.stdout.write(f'status {job.status}')
            if job.error:
                self.stdout.write(job.error)
            if job.output:
                self.stdout.write(str(job.output))
