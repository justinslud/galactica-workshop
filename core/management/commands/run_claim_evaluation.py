from django.core.management.base import BaseCommand, CommandError

from core import jobs
from core.models import Agent, Job, Proposal


class Command(BaseCommand):
    help = 'Re-run the planted claim evaluation against an existing proposal. No new research or writing.'

    def add_arguments(self, parser):
        parser.add_argument('--proposal', required=True)
        parser.add_argument('--claim', required=True)
        parser.add_argument('--agent', default='galactica-agent')
        parser.add_argument('--wait', action='store_true')

    def handle(self, *args, **options):
        proposal = Proposal.objects.select_related('origin_job').filter(pk=options['proposal']).first()
        if proposal is None:
            raise CommandError('Proposal not found.')
        agent = Agent.objects.filter(name=options['agent'], is_active=True).first()
        if agent is None:
            raise CommandError('Agent not found. Create one with manage.py create_agent.')
        if not proposal.candidate.claims.exists():
            raise CommandError('Proposal has no claim-level records. Run manage.py backfill_claims first.')
        snapshot = proposal.origin_job.config_snapshot if proposal.origin_job else None
        job = jobs.enqueue(
            'agent_cycle', user=agent.operator, runner_name='opencode',
            input={'evaluate_proposal': str(proposal.pk), 'claim': options['claim'], 'agent_id': str(agent.pk)},
            label=f'Claim evaluation: {proposal.article.title}',
            article=proposal.article, proposal=proposal, config_snapshot=snapshot,
        )
        self.stdout.write(f'queued {job.pk}')
        if options['wait']:
            job = jobs.run_now(job)
            self.stdout.write(f'status {job.status}')
            if job.error:
                self.stdout.write(job.error)
            if job.output:
                self.stdout.write(str(job.output))
